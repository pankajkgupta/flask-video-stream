#!/usr/bin/env python

from plumbum import SshMachine
import rpyc
from rpyc.utils.zerodeploy import DeployedServer
import sys
import threading
import copy
import pickle

class AssocClient:
    # Init connection to remote processing server in ctor
    def __init__(self, machine='localhost', username=None, ssh_key_fname=None, python_executable=None, environ=None, extra_paths=None):
        self.conn = None
        self.sshctx = None
        self.processing_server = None
        self.handler = None
        print 'Client: Connect to %s:%s' % (username, machine)
        self.sshctx = SshMachine(machine, user=username, keyfile=ssh_key_fname)
        self.server = DeployedServer(self.sshctx, python_executable=python_executable)
        self.conn = self.server.classic_connect()
        self.temp_dir = self.server.remote_machine.tempdir().__enter__()
        if environ is not None:
            for k, v in environ.iteritems():
                if k in self.conn.modules.os.environ:
                    self.conn.modules.os.environ[k] += ':' + v
                else:
                    self.conn.modules.os.environ[k] = v
        if extra_paths is not None:
            for p in extra_paths:
                self.conn.modules.sys.path.append(p)
        self.Assoc = self.conn.modules.ghack.assoc_server.AssocServer
        self.assoc_server = self.Assoc()
        self.last_prediction = None

        self.conn.modules.sys.stdout = sys.stdout #open('/tmp/procout.txt', 'wt')
        self.conn.modules.sys.stderr = sys.stdout #open('/tmp/procout.err', 'wt')
        # Current state
        self.commands = []
        self.has_updated_prediction = False
        # Prepare asynchronous function calls
        self.thread_event = threading.Event()
        self.done = False
        self.thread = threading.Thread(target=self.workerThread)
        self.thread.start()

    def workerThread(self):
        # Executes dreaming communication in a background thread
        try:
            while not self.done:
                while len(self.commands):
                    cmd = self.commands[0]
                    print 'Client: Execute command %s...' % cmd[0]
                    if cmd[0] == 'loadModel':
                        self.assoc_server.loadModel()
                    elif cmd[0] == 'setCamImage':
                        self.last_image = cmd[1]
                        serialized_image = pickle.dumps(self.last_image, protocol=0)
                        self.assoc_server.setCamImageSerialized(serialized_image)
                    elif cmd[0] == 'process':
                        self.assoc_server.processImage()
                        self.last_prediction = self.assoc_server.getPredictions()
                        self.has_updated_prediction = True
                    self.commands.pop(0)
                    print 'Client: Command %s done' % cmd[0]
                    if self.done: break
                print 'Client: Sleeping...'
                self.thread_event.wait()
                self.thread_event.clear()
        finally:
            self.commands = []
            self.done = True

    def loadModel(self):
        self.commands.append(['loadModel'])
        self.thread_event.set()

    def setCamImage(self, img):
        self.commands.append(['setCamImage', img.copy()])
        self.thread_event.set()

    def process(self):
        self.commands.append(['process'])
        self.thread_event.set()

    def hasUpdatedPrediction(self):
        return self.has_updated_prediction

    def isQueueEmpty(self):
        return len(self.commands) == 0

    def getPrediction(self):
        self.has_updated_prediction = False
        return self.last_prediction

    def quit(self):
        self.done = True
        self.thread_event.set()

    def __del__(self):
        self.done = True
        self.thread_event.set()
        if not self.conn is None:
            print 'Client: Disconnect'
            del self.conn
            self.conn = None



if __name__ == "__main__":
    # Test dummy client
    import numpy as np
    import PIL.Image
    import time

    img = np.float32(PIL.Image.open('/home/sven2/Downloads/skunk1.jpg'))
    assoc = AssocClient(extra_paths=['/home/sven2/python', '/home/sven2/s2caffe/python'])
    assoc.loadModel()
    for i in xrange(10):
        assoc.setCamImage(img)
        assoc.process()
        while not assoc.isQueueEmpty():
            print 'Working...'
            time.sleep(0.5)
        pred = assoc.getPrediction()
        print 'Done! Prediction: %s' % pred
        if assoc.done: break
    assoc.quit()
