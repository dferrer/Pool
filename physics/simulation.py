from common import break_shot, is_made, is_moving, num_made, select_shot, set_cue_position
from constants import *
from draw import draw
from physics import apply_friction
from setup import make_balls, make_edges, make_pockets, setup_pygame, setup_box2D
from Box2D import b2CircleShape, b2Fixture, b2PolygonShape, b2World, b2ContactListener, b2Vec2
from pygame.locals import QUIT
from random import randrange, seed
from sys import argv, exit
import pygame

# Keep things consistent.
seed(5)

def simulate(world, balls, edges, pockets, screen, clock, do_draw):
    background_color = (20, 130, 57) # Green felty color.
    world.Step(TIME_STEP, 10, 10)    # Kick things off.

    # Run simulation until balls stop moving.
    while is_moving(world):
        # Check for quit event
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

        # Apply friction forces to balls
        for body in world.bodies:
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

    # See if the cue ball went into a pocket.
    scratch = is_made(balls[0])
    if scratch:
        balls[0].body.position = (TABLE_WIDTH / 2.0 + TABLE_WIDTH / 4.0 + 0.4, TABLE_HEIGHT / 2.0)

    return scratch

def run(ball_positions=[], is_break=False, animate=True, balls_made=0):
    # Set up the table and balls
    screen, clock = setup_pygame('Pool!')
    world = setup_box2D()
    edges = make_edges(world)
    pockets = make_pockets(world)
    pocket_positions = map(lambda p: p.position, pockets)
    if ball_positions:
        ball_positions = map(lambda (x, y): (x * TABLE_WIDTH, (1-y) * TABLE_HEIGHT), ball_positions)
    balls = make_balls(world, ball_positions, add_cue=is_break)

    # Break if starting a new game, select shot if starting from existing game (e.g. from an image).
    cue_ball = balls[0]
    if is_break:
        set_cue_position(cue_ball)
        force = break_shot(cue_ball, balls[1])
    else:
        force = select_shot(cue_ball, balls, pocket_positions)

    # Run the simulation!
    misses, scratches, made_last_round = 0, 0, balls_made
    while balls_made < 15: # IMPORTANT: 'made' needs to start at however many balls are missing from table (taken from image, fix in main.py) otherwise there is an out of bounds error
        raw_input('Press enter to simulate the next shot')
        cue_ball.body.ApplyForce(force=force, point=cue_ball.body.position, wake=True)
        scratch = simulate(world, balls, edges, pockets, screen, clock, animate)
        scratches += int(scratch)
        made_total = num_made(balls)
        made_this_round = made_total - balls_made
        if made_this_round == 0:
            misses += 1
        else:
            balls_made += made_this_round
        print 'Made: {0}'.format(balls_made)
        print 'Scratches: {0}'.format(scratches)
        print 'Misses: {0}\n'.format(misses)
        if balls_made < 15:
            force = select_shot(cue_ball, balls, pocket_positions)

if __name__ == '__main__':
    animate = True if '-a' in argv else False
    run(animate=animate, is_break=True)
