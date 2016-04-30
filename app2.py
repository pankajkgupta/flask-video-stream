#!/usr/bin/env python
from flask import Flask, render_template, Response

# emulated camera
#from camera import Camera

import cv2

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)

cam1 = cv2.VideoCapture(0)
#cam2 = context.get_camera(1)
#cam2.Connect()
#cam2.StartCapture()
	
@app.route('/')
def index():
	"""Playroom FlyCap video"""
	return render_template('index.html')

def get_frame(cam):
	#cam.StartCapture()
	frame = cam.GrabNumPyImage('bgr')
	#### OpenCV capture ######
	#success, frame = self.cap.read()
	#####################
	# We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tostring()
        #return self.frames[int(time()) % 3]
	
def gen(cam):
    """Video streaming generator function."""
    while True:
        frame = get_frame(cam)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed1')
def video_feed1():
	"""Video streaming route. Put this in the src attribute of an img tag."""
	return Response(gen(cam1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#@app.route('/video_feed2')
#def video_feed2():
#	"""Video streaming route. Put this in the src attribute of an img tag."""
#	return Response(gen(cam2),
#                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, threaded=True)
