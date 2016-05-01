#!/usr/bin/env python
from flask import Flask, render_template, Response
from assoc_client import AssocClient
import time

# emulated camera
from camera import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

import cv2

cap = cv2.VideoCapture(0)

app = Flask(__name__)
app.assoc = None


@app.route('/')
def index():
    # Ensure classifier init (delayed on server)
    if app.assoc is None:
        app.assoc = AssocClient(extra_paths=['/home/sven2/python', '/home/sven2/caffe/python'])
        app.assoc.loadModel()
    """Video streaming home page."""
    return render_template('index.html')


def gen_video(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        if app.assoc is not None:
            if app.assoc.isQueueEmpty():
                print 'Tproc=', time.time()
                app.assoc.setCamImageByFileContents(frame) # Assumes rpyc server is run locally
                app.assoc.process()
            if app.assoc.hasUpdatedPrediction():
                print 'Tpred=', time.time()
                print 'Updated prediction: %s' % app.assoc.getThreatLevel()
                #    # TODO: Push prediction to client
                pass
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_video(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # Start webserver
    app.run(host='0.0.0.0', debug=True, threaded=True)
