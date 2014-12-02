from Box2D import b2Fixture
from constants import *
import pygame

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
    myfont = pygame.font.SysFont('monospace', 15)
    label = myfont.render(str(number), 1, (255,255,255))
    screen.blit(label, coords)

def draw(world, screen, background):
    screen.fill(background)
    for body in world.bodies:
        body.fixtures[0].shape.draw(screen, body, b2Fixture, body.userData)
