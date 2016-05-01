#!/usr/bin/env python
from flask import Flask, render_template, Response, redirect, request, url_for
from assoc_client import AssocClient
import itertools
import time
import os
import subprocess as sb
# from subprocess import call

# emulated camera
from camera import Camera
# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera


app = Flask(__name__)
app.assoc = None
live_images_path = "/media/images/"
recording_images_path = "/home/sven2/vid/v1/"

@app.route('/switch_to_live')
def switch_to_live():
    print 'SWITCH TO VIDEO'
    if app.camera is not None:
        app.camera.switch_to_video(live_images_path, False)
    return Response('OK', content_type='text/plain')

@app.route('/switch_to_recording')
def switch_to_recording():
    print 'SWITCH TO RECORDING'
    if app.camera is not None:
        app.camera.switch_to_video(recording_images_path, True)
    return Response('OK', content_type='text/plain')


@app.route('/')
def index():
    # Ensure classifier init (delayed on server)
    if app.assoc is None:
        app.assoc = AssocClient(extra_paths=['/home/sven2/python', '/home/sven2/caffe/python'])
        app.assoc.loadModel()
    """Video streaming home page."""

    # for threat streaming
    if request.headers.get('accept') == 'text/event-stream':
        def events():
            while True:
                if app.assoc.hasUpdatedPrediction():
                    print 'Updated prediction: %s' % app.assoc.getThreatLevel()
                    # app.assoc.getThreadLevel: float between 0 and 1
                    print 'Pred:\n%s'% app.assoc.getPrediction()
                    #    # TODO: Push prediction to client
                    threat_level = app.assoc.getThreatLevel()
                    if threat_level > 0.08: # if greater than threshold, push to client.
                        # push to client
                        print "THREAT THREAT THREAT THREAT!"
                        threat_string = 'THREAT '
                    else:
                        threat_string = 'OK '
                    yield "data: %s%f\n\n" % (threat_string, threat_level)
                time.sleep(.1)  # an artificial delay
        return Response(events(), content_type='text/event-stream')
    # return redirect(url_for('templates', filename='index.html'))
    return render_template('index.html')


def gen_video(camera):
    """Video streaming generator function."""
    app.camera = camera
    while True:
        time.sleep(0.2)
        frame = camera.get_frame()
        if frame is None:
            frame = ''
        elif app.assoc is not None:
            if app.assoc.isQueueEmpty():
                app.assoc.setCamImageByFileContents(frame) # Assumes rpyc server is run locally
                app.assoc.process()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')




@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_video(Camera(live_images_path)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/play_sound', methods=['POST'])
def play_sound():
    # command line command: omxplayer -o local example.mp3
    print "in play recording"
    # os.system("ssh -Y pi@192.168.1.202 'bash -s' < omxplayer -o local example.mp3")
    aa = sb.Popen("""ssh -Y pi@192.168.1.202 'omxplayer -o local example.mp3'""", shell = True, stdout = sb.PIPE, stderr = sb.PIPE)
    out, err = aa.communicate()
    # subprocess.open("""ssh -Y pi@192.168.1.202 'omxplayer -o local example.mp3'""", shell=True)
    # os.system('')
    # call(['omxplayer -o local example.mp3'])
    # os.system('omxplayer -o local example.mp3')
    print "done"
    return

if __name__ == '__main__':
    # Start webserver
    app.run(host='0.0.0.0', debug=True, threaded=True)
