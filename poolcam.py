from __future__ import division
import poolcv
from SimpleCV import *

def getValidImage(cam, params):
    img = None
    t = None 
    while not t:
        print "Getting image."
        time.sleep(.1)
        img = cam.getImage()
        img.show()
        t = poolcv.makeTransformed(img, params)
    return t

if __name__ == "__main__":
    video = VirtualCamera('game.mp4', 'video')

    processVideo(video)
