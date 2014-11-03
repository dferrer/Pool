import math, pygame
from Ball import Ball
pygame.init()

# Set up the window
def make_screen(dimensions, caption):
    screen = pygame.display.set_mode(dimensions)
    pygame.display.set_caption(caption)
    return screen

# Handle collisions
def collide(ball1, ball2):
    dx = ball1.x - ball2.x
    dy = ball1.y - ball2.y
    dist = math.hypot(dx, dy)
    if dist < ball1.radius + ball2.radius:
        normal = math.atan2(dy, dx)


    # dx = ball1.x - ball2.x
    # dy = ball1.y - ball2.y
    # dist = math.hypot(dx, dy)

    # if dist < (ball1.radius + ball2.radius):
    #     print 'collision'
    #     tangent = math.atan2(dy, dx)
    #     angle = 0.5 * math.pi + tangent

    #     angle1 = 2 * tangent - ball1.angle
    #     angle2 = 2 * tangent - ball2.angle
    #     # speed1 = ball2.speed * ball2.bounce
    #     # speed2 = ball1.speed * ball1.bounce
    #     (ball1.speed, ball2.speed) = (ball2.speed, ball1.speed)

    #     ball1.angle = angle1
    #     ball2.angle = angle2
    #     # (ball1.angle, ball1.speed) = (angle1, speed1)
    #     # (ball2.angle, ball2.speed) = (angle2, speed2)

    #     # ball1.x += math.sin(angle)
    #     # ball1.y -= math.cos(angle)
    #     # ball2.x -= math.sin(angle)
    #     # ball2.y += math.cos(angle)

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
    ball1 = Ball(position1, color1, 15.0, math.pi / 4.0)
    ball2 = Ball(position2, color2, 20.0, 3.0 * math.pi / 4.0)
    balls = [ball1, ball2]

    # Main loop
    running = True
    while running:
        # Check for close event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill screen with background color
        screen.fill(background_color)

        # Move and display balls
        for i, ball in enumerate(balls):
            ball.move(screen)
            for collball in balls[i+1:]:
                collide(ball, collball)
            ball.display(screen)

        # Update display
        pygame.display.flip()
