from Box2D import b2CircleShape, b2PolygonShape, b2World, b2Vec2
from common import rand_color
from constants import *
from contact import ContactListener
from draw import draw_circle, draw_polygon
from math import cos, radians, sin
import pygame

def setup_pygame(message):
    '''Create a Pygame screen and clock.'''
    dimensions = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(dimensions)
    clock=pygame.time.Clock()
    pygame.display.set_caption(message)
    return screen, clock

def setup_box2D():
    '''Create Box2D world.'''    
    world = b2World(gravity=(0, 0), doSleep=True, contactListener=ContactListener())
    b2PolygonShape.draw = draw_polygon
    b2CircleShape.draw = draw_circle
    return world

def make_edges(world):
    '''Create static bodies to represent the edges of the table.'''
    positions = [(TABLE_WIDTH / 2.0, EDGE_WIDTH), (EDGE_WIDTH,TABLE_HEIGHT / 2), (TABLE_WIDTH - EDGE_WIDTH,TABLE_HEIGHT / 2), (TABLE_WIDTH / 2.0, TABLE_HEIGHT - EDGE_WIDTH)]
    dimensions = [(TABLE_WIDTH / 2,EDGE_WIDTH), (EDGE_WIDTH, TABLE_HEIGHT / 2), (EDGE_WIDTH, TABLE_HEIGHT / 2), (TABLE_WIDTH / 2, EDGE_WIDTH)]
    edge_color = (150, 111, 51)
    edges = [world.CreateStaticBody(position=pos, shapes=b2PolygonShape(box=dim), restitution=RESTITUTION, userData=edge_color) for pos, dim in zip(positions, dimensions)]
    for edge in edges:
        edge.fixtures[0].friction = FRICTION
    return edges

def make_semicircle(n, offset):
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
    vertices = [make_semicircle(num_vertices, offset) for offset in offsets]
    shapes = [b2PolygonShape(vertices=verts) for verts in vertices]
    pocket_color = (5,5,5)
    pockets = [world.CreateStaticBody(position=pos, shapes=shape, restitution=RESTITUTION, userData=pocket_color) for pos, shape in zip(positions, shapes)]
    return pockets

def get_break_positions():
    wbase = TABLE_WIDTH / 2.0 -.05
    hbase = TABLE_HEIGHT / 2.0
    positions = [(wbase, hbase), \
                 (wbase - .05, hbase + .025), (wbase - .05, hbase - .025), \
                 (wbase - .10, hbase + .050), (wbase - .10, hbase - .050), \
                 (wbase - .15, hbase + .075), (wbase - .15, hbase + .025), (wbase - .15, hbase - .025), (wbase - .15, hbase - .075), \
                 (wbase - .20, hbase + .100), (wbase - .20, hbase + .050), (wbase - .20, hbase),        (wbase - .20, hbase - .050), (wbase - .20, hbase - .100)]
    return positions    

def make_ball(world, position, density, color):
    '''Create a dynamic body to respresent a ball.'''
    body = world.CreateDynamicBody(position=position, bullet=True, userData=color)
    ball = body.CreateCircleFixture(radius=BALL_RADIUS, density=CUE_BALL_DENSITY, restitution=RESTITUTION, friction=FRICTION)
    return ball

def make_balls(world, positions, add_cue=False, add_eight=False):
    '''Create a cue ball and 15 other balls.'''
    if len(positions) == 0:
        positions = get_break_positions()
        add_cue = True
    balls = [make_ball(world, pos, BALL_DENSITY, color=rand_color()) for pos in positions]
    if add_eight:
        eight_ball = make_ball(world, position=(TABLE_WIDTH / 2.0 - .15, TABLE_HEIGHT / 2.0), density=CUE_BALL_DENSITY, color=(0,0,0))
        balls.append(eight_ball)
    if add_cue:
        cue_ball = make_ball(world, position=(TABLE_WIDTH / 2.0 + TABLE_WIDTH / 4.0 + 0.4, TABLE_HEIGHT / 2.0), density=CUE_BALL_DENSITY, color=(255,255,255))
        balls.insert(0, cue_ball)
    return balls
