from __future__ import division
import poolcv
from SimpleCV import *

def processVideo(video):
    display = Display()

    frame = 0
    last = None
    while display.isNotDone():

        frame  = video.getFrameNumber()
        print frame

        img = video.getImage()
        video.skipFrames(20)
        t = poolcv.makeTransformed(img)
        # if(last):
            # diff = img - last
        # last = img
        if(t):
            img.save("out/game/frame" + str(frame) + ".png")
            t.save("out/game/transformed" + str(frame) + ".png")
    display.quit()

if __name__ == "__main__":
    video = VirtualCamera('game.mp4', 'video')

    processVideo(video)
                
