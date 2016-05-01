#!/usr/bin/env python
from flask import Flask, render_template, Response, redirect, request, url_for
from assoc_client import AssocClient
import itertools
import time

# emulated camera
from camera import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera


app = Flask(__name__)
app.assoc = None
images_path = "/media/images/"

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
            for i, c in enumerate(itertools.cycle('\|/-')):
                yield "data: %s %d\n\n" % (c, i)
                time.sleep(.1)  # an artificial delay
        return Response(events(), content_type='text/event-stream')
    # return redirect(url_for('templates', filename='index.html'))
    return render_template('index.html')


def gen_video(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        if frame is None:
            frame = ''
        elif app.assoc is not None:
            if app.assoc.isQueueEmpty():
                app.assoc.setCamImageByFileContents(frame) # Assumes rpyc server is run locally
                app.assoc.process()
            if app.assoc.hasUpdatedPrediction():
                print 'Updated prediction: %s' % app.assoc.getThreatLevel()
                # app.assoc.getThreadLevel: float between 0 and 1
                print 'Pred:\n%s'% app.assoc.getPrediction()
                #    # TODO: Push prediction to client
                if app.assoc.getThreatLevel() > 0.5: # if greater than 0.5, push to client.
                    # push to client
                    # threatNum1 = app.assoc.getThreatLevel()
                    threatNum1 = 0.7
                    yield render_template('index.html', threatNum = threatNum1)
                    # TODO replace frame depending on the threat

                pass
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')




@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_video(Camera(images_path)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # Start webserver
    app.run(host='0.0.0.0', debug=True, threaded=True)
