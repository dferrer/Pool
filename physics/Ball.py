import math, pygame

drag = 0.999
elasticity = 0.75

class Ball:
    def __init__(self, (x,y), color, speed=0.0, angle=0.0, radius=20, cue=False):
        self._x = x
        self._y = y
        self._color = color
        self._radius = radius
        self._speed = speed # Velocity, in meters per second
        self._angle = angle # Angle, in radians
        self._thickness = 0 # A circle with thickness 0 is a filled circle
        self._mass = 0.170097139 if cue else 0.155922376 # Mass of a ball, in kg (cue ball is 6 oz, the rest are 5.5 oz)
        self._friction = .995

    def display(self, screen):
        pygame.draw.circle(screen, self._color, (int(self._x), int(self._y)), self._radius, self._thickness)

    def move(self, screen):
        self._x += math.sin(self._angle) * self._speed
        self._y -= math.cos(self._angle) * self._speed
        self._speed *= self._friction
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

    @property
    def x(self):
        return self._x
        @x.setter
        def x(self, value):
            self._x = value

    @property
    def y(self):
        return self._y
        @y.setter
        def y(self, value):
            self._y = value
            
    @property
    def speed(self):
        return self._speed
        @speed.setter
        def speed(self, value):
            self._speed = value
            
    @property
    def angle(self):
        return self._angle
        @angle.setter
        def angle(self, value):
            self._angle = value

    @property
    def radius(self):
        return self._radius
        @radius.setter
        def radius(self, value):
            self._radius = value

    @property
    def friction(self):
        return self._friction
        @friction.setter
        def friction(self, value):
            self._friction = value
            
    @property
    def bounce(self):
        return self._bounce
        @bounce.setter
        def bounce(self, value):
            self._bounce = value


