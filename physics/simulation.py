import pygame, sys, time
from pygame.locals import QUIT
from math import atan2, cos, degrees, pi, sin, sqrt, radians
from Box2D import b2CircleShape, b2Fixture, b2PolygonShape, b2World, b2ContactListener, b2Vec2
from random import randrange
from scipy.constants import g
from contact import ContactListener

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

def draw_polygon(polygon, screen, body, fixture, color):
    '''Extend the shape class to use pygame for drawing polygons.'''
    vertices=[(body.transform*v)*PPM for v in polygon.vertices]
    points=[(v[0], SCREEN_HEIGHT-v[1]) for v in vertices]
    pygame.draw.polygon(screen, color, points)

def draw_circle(circle, screen, body, fixture, color):
    '''Extend the shape class to use pygame for drawing circles.'''
    position = body.transform * circle.pos * PPM
    points = (position[0], SCREEN_HEIGHT - position[1])
    pygame.draw.circle(screen, color, map(int, points), int(circle.radius * PPM))

def setup_pygame(message):
    '''Make a Pygame screen and clock.'''
    dimensions = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(dimensions)
    clock=pygame.time.Clock()
    pygame.display.set_caption(message)
    return screen, clock

def setup_box2D():
    '''Create Box2D world.'''
    world = b2World(gravity=(0, 0), doSleep=True, contactListener=ContactListener()) # Turn off gravity
    b2PolygonShape.draw = draw_polygon
    b2CircleShape.draw = draw_circle
    return world

def make_table(world):
    '''Create static bodies to represent the edges of the table.'''
    positions = [(TABLE_WIDTH / 2.0, EDGE_WIDTH), (EDGE_WIDTH,TABLE_HEIGHT / 2), (TABLE_WIDTH - EDGE_WIDTH,TABLE_HEIGHT / 2), (TABLE_WIDTH / 2.0, TABLE_HEIGHT - EDGE_WIDTH)]
    dimensions = [(TABLE_WIDTH / 2,EDGE_WIDTH), (EDGE_WIDTH, TABLE_HEIGHT / 2), (EDGE_WIDTH, TABLE_HEIGHT / 2), (TABLE_WIDTH / 2, EDGE_WIDTH)]
    edge_color = (150, 111, 51)
    edges = [world.CreateStaticBody(position=pos, shapes=b2PolygonShape(box=dim), restitution=RESTITUTION, userData=edge_color) for pos, dim in zip(positions, dimensions)]
    for edge in edges:
        edge.fixtures[0].friction = FRICTION
    return edges

def get_vertices(n, offset):
    vertices = [b2Vec2(0,0)]
    for i in range(n+1):
        angle = radians(offset + i * 90.0 / n)
        vertex = b2Vec2(POCKET_RADIUS * cos(angle), POCKET_RADIUS * sin(angle))
        vertices.append(vertex)
    return vertices

def make_pockets(world):
    positions = [(EDGE_WIDTH * 2, EDGE_WIDTH * 2), 
                 (TABLE_WIDTH - EDGE_WIDTH * 2, EDGE_WIDTH * 2), 
                 (TABLE_WIDTH - EDGE_WIDTH * 2, TABLE_HEIGHT - EDGE_WIDTH * 2), 
                 (EDGE_WIDTH * 2, TABLE_HEIGHT - EDGE_WIDTH * 2)]
    offsets = [0.0, 90.0, 180.0, 270.0]
    vertices = [get_vertices(12, offset) for offset in offsets]
    shapes = [b2PolygonShape(vertices=verts) for verts in vertices]
    color = (0, 0, 0)
    pockets = [world.CreateStaticBody(position=pos, shapes=shape, restitution=RESTITUTION, userData=color) for pos, shape in zip(positions, shapes)]
    return pockets

def make_ball(world, position, density, color):
    '''Create a dynamic body to respresent a ball.'''
    body = world.CreateDynamicBody(position=position, bullet=True, userData=color)
    ball = body.CreateCircleFixture(radius=BALL_RADIUS, density=CUE_BALL_DENSITY, restitution=RESTITUTION, friction=FRICTION)
    return ball

def make_balls(world):
    '''Create a cue ball and 10 other balls.'''
    wbase = TABLE_WIDTH / 2.0 - 0.5
    hbase = TABLE_HEIGHT / 2.0
    positions = [(wbase, hbase), \
                 (wbase - .05, hbase + .025), (wbase - .05, hbase - .025), \
                 (wbase - .10, hbase + .050),        (wbase - .10, hbase - .050), \
                 (wbase - .15, hbase + .075), (wbase - .15, hbase + .025), (wbase - .15, hbase - .025), (wbase - .15, hbase - .075), \
                 (wbase - .20, hbase + .100), (wbase - .20, hbase + .050), (wbase - .20, hbase),        (wbase - .20, hbase - .050), (wbase - .20, hbase - .100)]
    cue_ball = make_ball(world, position=(TABLE_WIDTH / 2.0 + TABLE_WIDTH / 4.0 + 0.4, TABLE_HEIGHT / 2.0), density=CUE_BALL_DENSITY, color=(255,255,255))
    eight_ball = make_ball(world, position=(wbase - .10, hbase), density=CUE_BALL_DENSITY, color=(0,0,0))
    other_balls = [make_ball(world, pos, BALL_DENSITY, color=rand_color()) for pos in positions]
    return [cue_ball] + other_balls

def unit(vector):
    return vector / sqrt(vector[0]**2 + vector[1]**2)

def apply_friction(body):
    '''Calculate and apply the frictional force on a body.'''
    x_vel, y_vel = body.linearVelocity[0], body.linearVelocity[1]
    threshold = 0.01
    if x_vel**2 + y_vel**2 > 0:
        if x_vel**2 + y_vel**2 < threshold: 
            # Stop the balls
            body.linearVelocity[0] = 0.0
            body.linearVelocity[1] = 0.0
        else:
            dv = -MU * g * unit(body.linearVelocity) * TIME_STEP
            body.linearVelocity += dv;


def is_moving(world):
    for i, body in enumerate(world.bodies):
        if abs(body.linearVelocity[0]) > 0 or abs(body.linearVelocity[1] > 0):
            return True
    return False

def remove(ball):
    ball.position = b2Vec2(5.0,5.0)
    ball.linearVelocity[0] = 0 
    ball.linearVelocity[1] = 0

def simulate(world, balls, edges, pockets, screen, clock, do_draw):
    world.Step(TIME_STEP, 10, 10)
    while is_moving(world):
        # Check for quit event
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

        # Apply friction forces to balls
        map(apply_friction, world.bodies)

        # Simulate the next step of the Box2D world and destroy balls in the destroy queue (i.e. balls that touched a pocket)
        world.Step(TIME_STEP, 10, 10)
        world.contactListener.DestroyBalls(world)
        world.ClearForces()

        # Draw the world
        if do_draw:
            draw(world, balls, edges, screen, clock)

    if abs(balls[0].body.position[0] - 5) < .0001 and abs(balls[0].body.position[1] - 5) < .0001: 
        print "scratch"
        balls[0].body.position = (TABLE_WIDTH / 2.0 + TABLE_WIDTH / 4.0 + 0.4, TABLE_HEIGHT / 2.0)
    return world

def draw(world, balls, edges, screen, clock):
    '''Main game loop.'''
    background_color = (20, 130, 57)

    # Draw the table background
    screen.fill(background_color)
    
    # Draw balls and edges!
    for body in world.bodies:
        body.fixtures[0].shape.draw(screen, body, b2Fixture, body.userData)
    
    # Display. Tick the clock in increments of the FPS variable
    pygame.display.flip()
    clock.tick(FPS)

def rand_color():
    return (randrange(15,240), randrange(15,240), randrange(15, 240))

def select_shot(cue, balls):
    for ball in balls[1:]:
        if ball.body.position[0] < 2.5 and ball.body.position[1] < 2.5:
            return 200 * (ball.body.position - cue.body.position)
    return (0, -200)

def main():
    # Set up the table and balls
    screen, clock = setup_pygame('Physics!')
    world = setup_box2D()
    edges = make_table(world)
    balls = make_balls(world)
    pockets = make_pockets(world)

    animate = True

    # Break (hit the cue ball)
    cue_ball = balls[0]
    force = (-200.0, 0.0)
    draw(world, balls, edges, screen, clock)

    N = 30
     # Do N random shots
    s = time.time()
    for x in range(N):
        cue_ball.body.ApplyForce(force=force, point=cue_ball.body.position, wake=True)
        simulate(world, balls, edges, pockets, screen, clock, animate)
        force = select_shot(cue_ball, balls)
        raw_input('Press enter to simulate the next shot')
    f = time.time()
    print (f - s)/N
        
if __name__ == '__main__':
    main()
