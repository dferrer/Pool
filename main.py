from __future__ import division
from vision.poolcv import makeTransformed, getParams, findBalls
from vision.poolcam import getValidImage
from physics.simulation import run
from sys import argv, exit
from SimpleCV import *

def processVideo(video, params):
    display = Display()
    frame = 0
    last = None
    while display.isNotDone():
        frame  = video.getFrameNumber()
        img = video.getImage()
        video.skipFrames(20)
        transform = makeTransformed(img, params)
        if(transform):
            img.save("out/game/frame" + str(frame) + ".png")
            transform.save("out/game/transformed" + str(frame) + ".png")
    display.quit()

def from_video():
    vid = VirtualCamera(sys.argv[2], 'video')
    params = {"area": 650250, "color": (0, 0, 255)} 
    processVideo(vid, params)

def from_camera():
    camera = Camera()
    params = getParams(camera)
    while True:
        raw_input("Press press Enter to continue, Ctrl + C to stop.\n")
        img = poolcam.getValidImage(camera, params)
        img.show()

def from_image():
    dim = (1000, 400)
    img = Image(sys.argv[2])
    params = {"area": 1463010.0, "color": Color.BLUE}
    transform = makeTransformed(img, params)
    img = transform.scale(dim[0], dim[1]).crop(.03 * dim[0], .03 * dim[1], .94 * dim[0], .94 * dim[1])
    balls = [(ball[0]/dim[0], ball[1]/dim[1]) for ball in findBalls(img)]
    made = 15 - len(balls)
    run(ball_positions=balls, is_break=False, balls_made=made, get_cue=True, add_eight=False)

def main():
    # Check number of command-line arguments.
    if len(argv) < 2:
        print 'Not enough arguments.'
        exit(1)

    # Build dispatcher.
    dispatcher = {
        '-i' : from_image,
        '-c' : from_camera,
        '-v' : from_video,
        '-r' : run
    }

    # Dispatch.
    flag = argv[1].lower()
    dispatcher[flag]()

if __name__ == "__main__":
    main()
