import math, pygame
from Ball import Ball
pygame.init()

# Set up the window
def make_screen(dimensions, caption):
    screen = pygame.display.set_mode(dimensions)
    pygame.display.set_caption(caption)
    return screen

if __name__ == '__main__':
    width, height = 640, 480
    screen = make_screen((width, height), 'Pool!')

    # Green background
    background_color = (20, 130, 57)

    # Draw a ball
    position1 = (200, 200)
    position2 = (400, 400)
    color1 = (0,0,255)
    color2 = (255,255,255)
    ball1 = Ball(position1, color1, 5.0, math.pi / 4.0)
    ball2 = Ball(position2, color2, 10.0, 3.0 * math.pi / 4.0)
    balls = [ball1, ball2]

    running = True
    # Main loop
    while running:
        # Check for close event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill screen with background color
        screen.fill(background_color)

        # Move and display balls
        for ball in balls:
            ball.move(screen)
            ball.display(screen)

        # Update display
        pygame.display.flip()
