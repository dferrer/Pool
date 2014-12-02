from setup import make_balls, make_edges, make_pockets, setup_pygame, setup_box2D
from sys import argv, exit
from pygame.locals import QUIT
from math import atan2, cos, degrees, sin, radians
from Box2D import b2CircleShape, b2Fixture, b2PolygonShape, b2World, b2ContactListener, b2Vec2
from random import randrange, seed
from draw import *
from common import break_shot, is_moving, num_made, select_shot, set_cue_position
from physics import apply_friction

# 2 and 5 are decent.
seed(5)

def simulate(world, balls, edges, pockets, screen, clock, do_draw):
    background_color = (20, 130, 57) # Green felty color.
    world.Step(TIME_STEP, 10, 10)    # Kick things off.
    while is_moving(world):
        # Check for quit event
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

        # Apply friction forces to balls
        for i, body in enumerate(world.bodies):
            apply_friction(body)

        # Simulate the next step of the Box2D world and destroy balls in the destroy queue (i.e. balls that touched pockets)
        world.Step(TIME_STEP, 10, 10)
        world.contactListener.DestroyBalls(world)
        world.ClearForces()

        # Draw the world
        if do_draw:
            # Fill in the table background, draw the bodies, and update the display and clock.
            draw(world, screen, background_color)
            pygame.display.flip()
            clock.tick(FPS)

    scratch = False
    if abs(balls[0].body.position[0] - 5) < .0001 and abs(balls[0].body.position[1] - 5) < .0001: 
        scratch = True
        balls[0].body.position = (TABLE_WIDTH / 2.0 + TABLE_WIDTH / 4.0 + 0.4, TABLE_HEIGHT / 2.0)

    return (world, scratch)

def run(ball_positions=[], is_break=False, animate=True, made=0):
    # Set up the table and balls
    screen, clock = setup_pygame('Pool!')
    world = setup_box2D()
    edges = make_edges(world)
    if len(ball_positions) != 0:
        ball_positions = map(lambda (x, y): (x * TABLE_WIDTH, (1-y) * TABLE_HEIGHT), ball_positions)
    balls = make_balls(world, ball_positions, add_cue=is_break)
    pockets = make_pockets(world)
    pocket_positions = map(lambda p: p.position, pockets)

    # Break (hit the cue ball)
    cue_ball = balls[0]
    if is_break:
        set_cue_position(cue_ball)
        force = break_shot(cue_ball, balls[1])
    else:
        force = select_shot(cue_ball, balls, pocket_positions)

    n = -1
     # Do N random shots
    misses, scratches = 0, 0
    while made < 15: # IMPORTANT: 'made' needs to start at however many balls are missing from table (taken from image) otherwise there is an out of bounds error
        raw_input('Press enter to simulate the next shot')
        n += 1
        cue_ball.body.ApplyForce(force=force, point=cue_ball.body.position, wake=True)
        (w, s) = simulate(world, balls, edges, pockets, screen, clock, animate)
        if s:
            scratches += 1
        m = num_made(balls)
        if m == made:
            misses += 1
        made = m
        print 'Made: {0}'.format(made)
        print 'Scratches: {0}'.format(scratches)
        print 'Misses: {0}\n'.format(misses)
        if made < 15:
            force = select_shot(cue_ball, balls, pocket_positions)

if __name__ == '__main__':
    animate = True if '-a' in argv else False
    run(animate=animate, is_break=True)
