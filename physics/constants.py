from scipy.constants import g
from math import pi

PPM = 400.0 # Pixels per meter, since Box2D uses meters but pygame uses pixels for drawing
FPS = 60 # Frames per second
TIME_STEP = 1.0 / FPS # Synchronize pygame and Box2D using frames per second and a time step
TABLE_WIDTH, TABLE_HEIGHT = 2.34, 1.17 # Regulation pool table is 234cm (8ft) by 117cm (4ft)
SCREEN_WIDTH, SCREEN_HEIGHT = int(PPM * TABLE_WIDTH), int(PPM * TABLE_HEIGHT)
EDGE_WIDTH = 0.025 # This isn't to scale, but makes the edges look nice
BALL_RADIUS = 0.05715 / 2.0 # American-style pool balls are 57.15mm in diameter
POCKET_RADIUS = 0.06 # 4.75cm will do for now
BALL_VOLUME = 4.0 / 3.0 * pi * BALL_RADIUS**3 * 10
CUE_BALL_MASS = 0.170 # 6 oz => kg
CUE_BALL_DENSITY = CUE_BALL_MASS / BALL_VOLUME
BALL_MASS = 0.156 # 5.5 oz => kg
BALL_DENSITY = BALL_MASS / BALL_VOLUME
MU = 0.15 # 0.013 actual, but this looks nice
FRICTION = 0.0 # Turn off friction since we are using a top-down view
RESTITUTION = 1.0 # Elastic collisions