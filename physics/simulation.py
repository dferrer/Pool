import pygame
from pygame.locals import QUIT
from math import atan2, cos, degrees, pi, sin
from Box2D import b2CircleShape, b2Fixture, b2PolygonShape, b2World
from random import randrange
from scipy.constants import g

PPM = 400.0 # Pixels per meter, since Box2D uses meters but we want to use pixels
FPS = 60 # Frames per second
TIME_STEP = 1.0 / FPS # Synchronize pygame and Box2D using frames per second and a time step
TABLE_WIDTH, TABLE_HEIGHT = 2.34, 1.17 # Regulation pool table is 234cm (8ft) by 117cm (4ft)
SCREEN_WIDTH, SCREEN_HEIGHT = int(PPM * TABLE_WIDTH), int(PPM * TABLE_HEIGHT)
EDGE_WIDTH = 0.025 # This isn't to scale, but makes the edges look nice
BALL_RADIUS = 0.05715 / 2.0 # American-style pool balls are 57.15mm in diameter
BALL_VOLUME = 4.0 / 3.0 * pi * BALL_RADIUS**3 * 10
CUE_BALL_MASS = 0.170 # 6 oz => kg
CUE_BALL_DENSITY = CUE_BALL_MASS / BALL_VOLUME
BALL_MASS = 0.156 # 5.5 oz => kg
BALL_DENSITY = BALL_MASS / BALL_VOLUME
MU = 0.05 # 0.013 actual, but this looks nice
FRICTION = 0.0 # Turn off friction since we are using a top-down view
RESTITUTION = 1.0 # Elastic collisions

def draw_polygon(polygon, screen, body, fixture, color):
    '''Extend the shape class to use pygame for drawing polygons.'''
    vertices=[(body.transform*v)*PPM for v in polygon.vertices]
    points=[(v[0], SCREEN_HEIGHT-v[1]) for v in vertices]
    pygame.draw.polygon(screen, color, points)

def draw_circle(circle, screen, body, fixture, color):
    '''Extend the shape class to use pygame for drawing circles.'''
    position=body.transform*circle.pos*PPM
    points=(position[0], SCREEN_HEIGHT-position[1])
    pygame.draw.circle(screen, color, [int(x) for x in points], int(circle.radius*PPM))

def setup_pygame(message):
    '''Make a Pygame screen and clock.'''
    dimensions = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(dimensions)
    clock=pygame.time.Clock()
    pygame.display.set_caption(message)
    return screen, clock

def setup_box2D():
    '''Create Box2D world.'''
    world = b2World(gravity=(0, 0), doSleep=True) # Turn off gravity
    b2PolygonShape.draw = draw_polygon
    b2CircleShape.draw = draw_circle
    return world

def make_table(world):
    '''Create static bodies to represent the edges of the table.'''
    positions = [(TABLE_WIDTH / 2.0, EDGE_WIDTH), (EDGE_WIDTH,TABLE_HEIGHT / 2), (TABLE_WIDTH - EDGE_WIDTH,TABLE_HEIGHT / 2), (TABLE_WIDTH / 2.0, TABLE_HEIGHT - EDGE_WIDTH)]
    dimensions = [(TABLE_WIDTH / 2,EDGE_WIDTH), (EDGE_WIDTH, TABLE_HEIGHT / 2), (EDGE_WIDTH, TABLE_HEIGHT / 2), (TABLE_WIDTH / 2, EDGE_WIDTH)]
    edges = [world.CreateStaticBody(position=pos, shapes=b2PolygonShape(box=dim), restitution=RESTITUTION) for pos, dim in zip(positions, dimensions)]
    for edge in edges: # Set edge frictions to 0
        edge.fixtures[0].friction = FRICTION
    return edges

def make_ball(world, position, density):
    '''Create a dynamic body to respresent a ball.'''
    body = world.CreateDynamicBody(position=position, bullet=True)
    ball = body.CreateCircleFixture(radius=BALL_RADIUS, density=CUE_BALL_DENSITY, restitution=RESTITUTION, friction=FRICTION)
    return ball

def make_balls(world):
    '''Create a cue ball and 10 other balls.'''
    wbase = TABLE_WIDTH / 2.0 - 0.5
    hbase = TABLE_HEIGHT / 2.0
    positions = [(wbase, hbase), \
                 (wbase - .05, hbase + .025), (wbase - .05, hbase - .025), \
                 (wbase - .10, hbase + .050), (wbase - .10, hbase),        (wbase - .10, hbase - .050), \
                 (wbase - .15, hbase + .075), (wbase - .15, hbase + .025), (wbase - .15, hbase - .025), (wbase - .15, hbase - .075), \
                 (wbase - .20, hbase + .100), (wbase - .20, hbase + .050), (wbase - .20, hbase),        (wbase - .20, hbase - .050), (wbase - .20, hbase - .100)]
    cue_ball = make_ball(world, position=(TABLE_WIDTH / 2.0 + TABLE_WIDTH / 4.0 + 0.4, TABLE_HEIGHT / 2.0), density=CUE_BALL_DENSITY)
    other_balls = [make_ball(world, pos, BALL_DENSITY) for pos in positions]
    return [cue_ball] + other_balls

def apply_friction(body):
    '''Calculate and apply the frictional force on a body.'''
    x_vel, y_vel = body.linearVelocity[0], body.linearVelocity[1]
    threshold = 0.15
    if abs(x_vel) > 0.00001 or abs(y_vel) > 0.00001:
        if abs(x_vel) < threshold and abs(y_vel) < threshold:
            # Stop the balls
            body.linearVelocity[0] = 0.0
            body.linearVelocity[1] = 0.0
        else:
            # Apply friction force
            mass = body.massData.mass
            force = -1.0 * mass * g * MU
            angle = degrees(atan2(y_vel, x_vel))
            components = (force * cos(angle), force * sin(angle))
            position = (body.position[0], body.position[1])
            body.ApplyForce(force=components, point=position, wake=True)

def run(world, screen, clock, colors):
    '''Main game loop.'''
    background_color = (20, 130, 57)
    running=True
    while running:
        # Check for close event
        for event in pygame.event.get():
            if event.type==QUIT:
                running=False

        # Draw the table background
        screen.fill(background_color)

        # Apply friction forces to balls, and draw the edges and balls
        for i, body in enumerate(world.bodies):
            apply_friction(body)
            body.fixtures[0].shape.draw(screen, body, b2Fixture, colors[i])

        # Simulate the next step of the Box2D world
        world.Step(TIME_STEP, 10, 10)
        world.ClearForces()

        # Display. Tick the clock in increments of the FPS variable
        pygame.display.flip()
        clock.tick(FPS)

def rand_color():
    return (randrange(15,240), randrange(15,240), randrange(15, 240))

def main():
    # Set up the table and balls
    screen, clock = setup_pygame('Physics!')
    world = setup_box2D()
    edges = make_table(world)
    balls = make_balls(world)

    # For now, make random ball colors
    colors = [(150, 111, 51)]*4 + [(255, 255, 255)] + [rand_color() for x in range(4)] + [(0, 0, 0)] + [rand_color() for x in range(10)]

    # Break (hit the cue ball)
    cue_ball = balls[0]
    force = (-130.0, 0.0)
    cue_ball.body.ApplyForce(force=force, point=cue_ball.body.position, wake=True)

    # Run the simulation
    run(world, screen, clock, colors)

if __name__ == '__main__':
    main()