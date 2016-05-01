from time import time
import glob

class Camera(object):
    """ takes a list of frames from a directory and 

    def __init__(self, images_path):
	self.images_path = images_path

    def get_frame(self):
	l_files = glob.glob(self.images_path + "/*jpg")
	l_files.sort()
	self.frames = l_files
	if len(self.frames) == 0:
		print "no frames found!!"
	else:
		self.frames[-1]
