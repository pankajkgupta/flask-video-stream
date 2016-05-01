#!/usr/bin/env python

import caffe
import numpy as np
import pickle
import PIL.Image
from cStringIO import StringIO

# Instance of loaded model that can perform dreaming
class AssocServer:
    # CONFIG
    model_proto =  '/home/sven2/python/ghack/alexnet.prototxt'
    model_weights = '/home/sven2/python/ghack/alexnet.caffemodel'
    cat_file = '/home/sven2/python/ghack/synset_words.txt'
    mean = [104.0, 116.0, 122.0]
    channel_swap = (2, 1, 0)
    end_layer = 'fc8'
    gpu_idx = -1 # CPU
    is_dummy = False
    threat_categories = [777, 623, 473, 596, 499, 677]

    def __init__(self):
        self.locations = []
        self.gpu_idx = AssocServer.gpu_idx
        self.net = None
        self.model_info = None # Selected model
        self.has_unprocessed_image = False
        self.predictions = None

    # Model interface
    # --------------------------------------------------
    def clearModel(self):
        # Clear any loaded model information
        if self.net is not None:
            del self.net
            self.net = None

    def loadModel(self):
        if AssocServer.is_dummy: return
        # Clear old model first to ensure we don't have two models loaded at the same time
        self.clearModel()
        # Init caffe
        if self.gpu_idx < 0:
            print('ASrv: Caffe init on CPU.')
            caffe.set_mode_cpu()
        else:
            print('ASrv: Caffe init on GPU %d.' % self.gpu_idx)
            caffe.set_mode_gpu()
            caffe.set_device(self.gpu_idx)
        # Init model
        self.net = caffe.Classifier(AssocServer.model_proto, AssocServer.model_weights,
                                    mean=np.array(AssocServer.mean),
                                    channel_swap=AssocServer.channel_swap)
        shape = self.net.blobs['data'].shape
        self.net.blobs['data'].reshape(1, shape[1], shape[2], shape[3])
        # Load category file
        self.labels = open(AssocServer.cat_file, 'rt').read().splitlines()
        print('ASrv: Model load done.')

    # Processing interface
    # ---------------------------------------------------
    def setCamImage(self, image_data):
        # Replace image to be dreamt on
        # image_data: numpy array h*w*3
        self.has_unprocessed_image = True
        self.cam_image = image_data.copy() #self.preprocess(image_data.copy())

    def setCamImageSerialized(self, image_data_stream):
        # Set dream image from data stream
        self.setCamImage(pickle.loads(image_data_stream))

    def setCamImageByLocalFilename(self, local_filename):
        # Set dream image from a local filename
        print 'local_filename = ', local_filename
        self.setCamImage(np.float32(PIL.Image.open(local_filename)))

    def setCamImageByFileContents(self, file_contents):
        # Set dream image from a local filename
        file_jpgdata = StringIO(file_contents)
        self.setCamImage(np.float32(PIL.Image.open(file_jpgdata)))

    def hasUnprocessedImage(self):
        return self.has_unprocessed_image

    # Get latest predictions
    def getPredictions(self):
        top_labels = self.predictions.argsort()[-5:][::-1]
        s = ''
        for al in top_labels.tolist():
            l = int(al)
            s += str(l) + '\t' + str(self.predictions[l]) + '\t' + self.labels[l] + '\n'
        return s

    def getThreatLevel(self):
        threat_level = 0.0
        for cat in AssocServer.threat_categories:
            threat_level += self.predictions[cat]
        return threat_level

    # Process image to predictions

    # Processing internals
    # ---------------------------------------------------
    def preprocess(self, input):
        # Return image converted to caffe data format
        if AssocServer.is_dummy:
            return input
        else:
            return np.float32(np.rollaxis(input, 2)[::-1]) - self.net.transformer.mean['data']

    def processImage(self):
        if AssocServer.is_dummy:
            self.predictions = np.ones(1000)
        else:
            #self.net.blobs['data'].data[0,...] = self.cam_image
            #self.net.forward(end=AssocServer.end_layer)
            #self.predictions = self.net.blobs[AssocServer.end_layer].data[0,...].squeeze()
            self.predictions = self.net.predict([self.cam_image]).squeeze()
        self.has_unprocessed_image = False


# Test server
if __name__ == '__main__':
    import PIL.Image
    srv = AssocServer()
    test_fn = '/home/sven2/Documents/louche.jpg'
    img = np.float32(PIL.Image.open(test_fn))
    img_ser = pickle.dumps(img, protocol=0)
    print 'Init caffe'
    srv.loadModel()
    print 'Set'
    srv.setCamImageSerialized(img_ser)
    print 'Process'
    srv.processImage()
    print 'Predictions: %s' % str(srv.getPredictions())
    print 'Threat level: %f' % srv.getThreatLevel()
