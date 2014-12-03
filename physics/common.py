from __future__ import division
from constants import *
from physics import dot, unit, vector_circle_intersect
from Box2D import b2Vec2
from random import randrange
from sys import argv

def rand_color():
    return (randrange(15,240), randrange(15,240), randrange(15, 240))

def num_made(balls):
    return map(is_made, balls).count(True)

def is_made(ball):
    return abs(ball.body.position[0] - 5) < .0001 and abs(ball.body.position[1] - 5) < .0001

def is_moving(world):
    for i, body in enumerate(world.bodies):
        if abs(body.linearVelocity[0]) > 0 or abs(body.linearVelocity[1] > 0):
            return True
    return False

def remove(ball):
    ball.position = b2Vec2(5.0,5.0)
    ball.linearVelocity[0] = 0
    ball.linearVelocity[1] = 0

def ball_positions(balls):
    c = []
    for ball in balls:
        c.append((ball.body.position[0], ball.body.position[1]))
    return c

#############################################################
#                         SELECTION                         #
#############################################################

def possible_pockets(C, T, pockets):
    return filter(lambda P: P[0] > 0.0, \
                  map(lambda P: (dot(unit(P - T), unit(T - C)), T, P), \
                      pockets))

def shot(C, T, P):
    direction = unit(T + unit(T - P) * BALL_RADIUS * 1.5 - C)
    power = min(100 / dot(unit(P - T), unit(T - C)), 150)
    return power * direction

def break_shot(cue, target):
    print 'Breaking from', cue.body.position[0], cue.body.position[1]
    return unit(target.body.position - cue.body.position) * 200

def set_cue_position(cue):
    cue.body.position += (randrange(-100, 101) * .001, randrange(-100, 101) * .002)

def is_unobstructed(cue, target, pocket, balls):
    CT = target - cue # path to target
    TP = pocket - target # target to pocket
    for b in balls[1:]:
        if not is_made(b):
            d = b.body.position - target

            # check that b !== T
            if abs(d[0]) > .0001 and abs(d[1]) > .0001:
                if vector_circle_intersect(b.body.position, b.shape.radius, cue, target) or vector_circle_intersect(b.body.position, b.shape.radius, target, pocket):
                    return False
    return True

def select_shot(cue, balls, pockets):
    C = cue.body.position
    possible = []
    for ball in balls[1:]:
        T = ball.body.position
        if T[0] < TABLE_WIDTH and T[1] < TABLE_HEIGHT:
            possible += possible_pockets(C, T, pockets)

    possible.sort(reverse=True)

    for (DP, T, P) in possible:
        if is_unobstructed(C, T, P, balls):
            return shot(C, T, P)

    return shot(C, possible[0][1], possible[0][2])
