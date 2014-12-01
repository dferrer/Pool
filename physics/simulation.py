import pygame, sys, time
from pygame.locals import QUIT
from math import atan2, cos, degrees, pi, sin, sqrt, radians
from Box2D import b2CircleShape, b2Fixture, b2PolygonShape, b2World, b2ContactListener, b2Vec2
from random import randrange
from scipy.constants import g
# from contact import ContactListener

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

def draw_ball(circle, number, screen, body, fixture, color):
    position = body.transform * circle.pos * PPM
    points = (position[0], SCREEN_HEIGHT-position[1])
    coords = map(int, points)
    pygame.draw.circle(screen, color, coords, int(circle.radius*PPM))
    myfont = pygame.font.SysFont("monospace", 15)
    label = myfont.render(str(number), 1, (255,255,255))
    screen.blit(label, coords)

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
    edges = [world.CreateStaticBody(position=pos, shapes=b2PolygonShape(box=dim), restitution=RESTITUTION) for pos, dim in zip(positions, dimensions)]
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
    num_vertices = 12
    offsets = [0.0, 90.0, 180.0, 270.0]
    vertices = [get_vertices(num_vertices, offset) for offset in offsets]
    shapes = [b2PolygonShape(vertices=verts) for verts in vertices]
    pockets = [world.CreateStaticBody(position=pos, shapes=shape, restitution=RESTITUTION) for pos, shape in zip(positions, shapes)]
    return pockets

def make_ball(world, position, density):
    '''Create a dynamic body to respresent a ball.'''
    body = world.CreateDynamicBody(position=position, bullet=True)
    ball = body.CreateCircleFixture(radius=BALL_RADIUS, density=CUE_BALL_DENSITY, restitution=RESTITUTION, friction=FRICTION)#, typ='ball')
    return ball

def break_positions():
    wbase = TABLE_WIDTH / 2.0 - 0.5
    hbase = TABLE_HEIGHT / 2.0
    return [(wbase, hbase), \
                 (wbase - .05, hbase + .025), (wbase - .05, hbase - .025), \
                 (wbase - .10, hbase + .050), (wbase - .10, hbase),        (wbase - .10, hbase - .050), \
                 (wbase - .15, hbase + .075), (wbase - .15, hbase + .025), (wbase - .15, hbase - .025), (wbase - .15, hbase - .075), \
                 (wbase - .20, hbase + .100), (wbase - .20, hbase + .050), (wbase - .20, hbase),        (wbase - .20, hbase - .050), (wbase - .20, hbase - .100)]

def restore_balls(world, positions):
    return [make_ball(world, pos, BALL_DENSITY) for pos in positions]

def make_balls(world, positions=break_positions()):
    '''Create a cue ball and 10 other balls.'''
    cue_ball = make_ball(world, position=(TABLE_WIDTH / 2.0 + TABLE_WIDTH / 4.0 + 0.4, TABLE_HEIGHT / 2.0), density=CUE_BALL_DENSITY)
    other_balls = [make_ball(world, pos, BALL_DENSITY) for pos in positions]
    return [cue_ball] + other_balls

def length(vector):
    return sqrt(vector[0]**2 + vector[1]**2)

def unit(vector):
    return vector / length(vector)

def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]

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

def simulate(world, balls, edges, colors, screen, clock, do_draw):
    world.Step(TIME_STEP, 10, 10)
    while is_moving(world):
        # Check for quit event
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

        # Apply friction forces to balls
        for i, body in enumerate(world.bodies):
            apply_friction(body)

        # Simulate the next step of the Box2D world and destroy balls in the destroy queue (i.e. balls that touched pockets)
        world.Step(TIME_STEP, 10, 10)
        world.contactListener.DestroyBalls(world)
        world.ClearForces()

        # Draw the world
        if do_draw:
            draw(world, balls, edges, screen, clock, colors)

    if abs(balls[0].body.position[0] - 5) < .0001 and abs(balls[0].body.position[1] - 5) < .0001: 
        print "scratch"
        balls[0].body.position = (TABLE_WIDTH / 2.0 + TABLE_WIDTH / 4.0 + 0.4, TABLE_HEIGHT / 2.0)

    return world

def draw(world, balls, edges, screen, clock, colors):
    '''Main game loop.'''
    background_color = (20, 130, 57)
    # DERP
    pygame.event.get()

    # Draw the table background
    screen.fill(background_color)
    
    # Draw balls and edges!
    for i, body in enumerate(world.bodies):
        body.fixtures[0].shape.draw(screen, body, b2Fixture, colors[i])
    
    # Display. Tick the clock in increments of the FPS variable
    pygame.display.flip()
    clock.tick(FPS)

def rand_color():
    return (randrange(15,240), randrange(15,240), randrange(15, 240))

def possible_pockets(C, T, pockets):
    dot_pockets = sorted(map(lambda P: (dot((P - T), (T - C)), P), pockets), reverse=True)
    return map(lambda P: P[1], filter(lambda P: P[0] > 0, dot_pockets))

def shot(C, T, P):
    print "--------\n"
    print C, T, P
    print "Power: ", length(T - C) + length(P - T)
    print "Direction: ", unit(T + unit(T - P) * BALL_RADIUS - C)
    print "Desired Position: ", T + unit(T - P) * BALL_RADIUS, 
    return 50 * unit(T + unit(T - P) * BALL_RADIUS - C) 

def select_shot(cue, balls, pockets):
    for ball in balls[1:]:
        if ball.body.position[0] < TABLE_WIDTH and ball.body.position[1] < TABLE_HEIGHT:
            ps = possible_pockets(cue.body.position, ball.body.position, pockets)
            return shot(cue.body.position, ball.body.position, ps[0])
    return (0, -200)

class ContactListener(b2ContactListener):
    def __init__(self):
        b2ContactListener.__init__(self)
        self.to_destroy = []

    def DestroyBalls(self, world):
        for ball in self.to_destroy:
            remove(ball)
            # world.DestroyBody(ball)
        self.to_destroy = []

    def PreSolve(self, contact, _):
        if contact.touching:
            if type(contact.fixtureA.shape) is b2PolygonShape and len(contact.fixtureA.shape.vertices) == 14:
                self.to_destroy.append(contact.fixtureB.body)
            elif type(contact.fixtureB.shape) is b2PolygonShape and len(contact.fixtureB.shape.vertices) == 14:
                self.to_destroy.append(contact.fixtureA.body)

def ball_positions(balls):
    c = []
    for ball in balls:
        c.append((ball.body.position[0], ball.body.position[1]))
    return c

def restore_world(positions):
    print "\n\nrestoring world\n\n"
    w = setup_box2D()
    edges = make_table(w)
    pockets = make_pockets(w)
    balls = restore_balls(w, positions)
    return w

def main():
    # Set up the table and balls
    screen, clock = setup_pygame('Physics!')
    world = setup_box2D()
    edges = make_table(world)
    balls = make_balls(world)
    pockets = make_pockets(world)
    pocket_positions = map(lambda p: p.position, pockets)

    # For now, make random ball colors
    colors = [(150, 111, 51)] * 4  # Edges
    colors.append((255, 255, 255)) # Cue ball
    colors.extend([rand_color() for x in range(4)])  # Balls
    colors.append((0, 0, 0))  # 8 ball
    colors.extend([rand_color() for x in range(10)]) # More balls
    colors.extend([(0, 0, 0)]*6) # Pockets

    animate = True

    # Break (hit the cue ball)
    cue_ball = balls[0]
    force = (-200.0, 0.0)
    # draw(world, balls, edges, screen, clock, colors)

    N = 30
     # Do N random shots
    s = time.time()
    for x in range(N):
        cue_ball.body.ApplyForce(force=force, point=cue_ball.body.position, wake=True)
        simulate(world, balls, edges, colors, screen, clock, animate)
        # positions = ball_positions(balls)
        # restore_world(positions)
        force = select_shot(cue_ball, balls, pocket_positions)
        # pygame.draw.line(screen, (255, 0, 0), map(int, PPM*cue_ball.body.position), map(int, PPM*(cue_ball.body.position + force)), 25)
        # raw_input('Press enter to simulate the next shot')
    f = time.time()
    print (f - s)/N
        
if __name__ == '__main__':
    main()