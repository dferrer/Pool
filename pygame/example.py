import pygame
from pygame.locals import *

pygame.init()

# Set Up the Window
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Test!')

# SOTC Green Background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((20, 130, 57))

# Load and convert image
ball = pygame.image.load('ball.jpeg')
ball = ball.convert()

# Ball Position Varibales
lx = 100
ly = 100
speed = 3

# Get bounds for ball
rbound = screen.get_width() - ball.get_width()
botbound = screen.get_height() - ball.get_height()

# Clock and loop variables
framerate = pygame.time.Clock()
running = True


# Main loop
while running:
	# Tick the clock
	framerate.tick(60)

	# Keypress events, move the ball
	if pygame.key.get_pressed()[K_UP]:
		ly = ly - speed
	if pygame.key.get_pressed()[K_DOWN]:
		ly = ly + speed
	if pygame.key.get_pressed()[K_LEFT]:
		lx = lx - speed
	if pygame.key.get_pressed()[K_RIGHT]:
		lx = lx + speed

	# Test for Out-of-Bounds
	if lx > rbound:
		lx = rbound
	if lx < 0:
		lx = 0
	if ly > botbound:
		ly = botbound
	if ly < 0:
		ly = 0

	# Blit images
	screen.blit(background, (0, 0))
	screen.blit(ball, (lx, ly))

	# Update display
	pygame.display.update()

	# Handle a Close Event
	for event in pygame.event.get():
	  if event.type == pygame.QUIT:
	    running = False