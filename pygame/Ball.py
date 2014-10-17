import math, pygame

class Ball:
    def __init__(self, (x,y), color, speed=0.0, angle=0.0, radius=20):
        self._x = x
        self._y = y
        self._color = color
        self._radius = radius
        self._speed = speed
        self._angle = angle # Angle, in radians
        self._thickness = 0 # A circle with thickness 0 is a filled circle

    def set_angle(self, angle):
        self._angle = angle

    def display(self, screen):
        pygame.draw.circle(screen, self._color, (int(self._x), int(self._y)), self._radius, self._thickness)

    def move(self, screen):
        self._x += math.sin(self._angle) * self._speed
        self._y -= math.cos(self._angle) * self._speed
        self.hit_edge(screen)

    def hit_edge(self, screen):
        width = screen.get_width()
        height = screen.get_height()
        if self._x > (width - self._radius): # Right bound
            self._x = 2 * (width - self._radius) - self._x
            self._angle = -1.0 * self._angle
        elif self._x < self._radius: # Left bound
            self._x = 2 * self._radius - self._x
            self._angle = -1.0 * self._angle
        if self._y > (height - self._radius): # Upper bound
            self._y = 2 * (height - self._radius) - self._y
            self._angle = math.pi - self._angle
        elif self._y < self._radius: # Lower bound
            self._y = 2 * self._radius - self._y
            self._angle = math.pi - self._angle