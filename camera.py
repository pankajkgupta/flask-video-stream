from time import time
import glob

class Camera(object):
    """ takes a list of frames from a directory and """

    def __init__(self, images_path, is_prerec_video=False):
        self.images_path = images_path
        self.is_prerec_video = is_prerec_video
        self.frame_index = 0

    def get_frame(self):
        l_files = glob.glob(self.images_path + "/*jpg")
        l_files.sort()
        self.frames = l_files
        if len(self.frames) == 0:
            return None
        else:
            if self.is_prerec_video:
                filename = self.frames[self.frame_index]
                self.frame_index = min(self.frame_index+1, len(self.frames)-1)
            else:
                filename = self.frames[-2]
            print 'FILE: %s' % filename
            return open(filename, 'rb').read()

    # Re-init either for video stream or for pre-recorded video
    def switch_to_video(self, images_path, is_prerec_video):
        self.images_path = images_path
        self.is_prerec_video = is_prerec_video
        self.frame_index = 0
