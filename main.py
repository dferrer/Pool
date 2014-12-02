from __future__ import division
import poolcv
import poolcam
import sys
from physics import simulation

from SimpleCV import *

def processVideo(video, params):
    display = Display()

    frame = 0
    last = None
    while display.isNotDone():

        frame  = video.getFrameNumber()
        print frame

        img = video.getImage()
        video.skipFrames(20)
        t = poolcv.makeTransformed(img, params)
        # if(last):
            # diff = img - last
        # last = img
        if(t):
            img.save("out/game/frame" + str(frame) + ".png")
            t.save("out/game/transformed" + str(frame) + ".png")
    display.quit()

def mainLoop():
    camera = Camera()
    params = poolcv.getParams(camera)
    while True:
        raw_input("Press press Enter to continue, Ctrl + C to stop.\n")
        img = poolcam.getValidImage(camera, params)
        img.show()

if __name__ == "__main__":
    if(len(sys.argv) < 2):
        print "Arguments required."

    elif(sys.argv[1] == "-f"):
        video = VirtualCamera(sys.argv[2], 'video')
        params = {"area": 650250, "color": (0, 0, 255)} 
        processVideo(video, params)

    elif(sys.argv[1] == "-c"):
        mainLoop()

    elif sys.argv[1] == "-b":
        dim = (1000, 400)
        img = Image(sys.argv[2]).scale(dim[0], dim[1]).crop(.03 * dim[0], .03 * dim[1], .94 * dim[0], .94 * dim[1])
        balls = poolcv.findBalls(img)
        balls = map(lambda p: (p[0]/dim[0], p[1]/dim[1]), balls)
        simulation.run(ball_positions=balls)
