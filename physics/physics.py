from math import sqrt
from constants import *

def apply_friction(body):
    '''Calculate and apply the frictional force on a body.'''
    x_vel, y_vel = body.linearVelocity[0], body.linearVelocity[1]
    threshold = 0.01
    if x_vel**2 + y_vel**2 > 0:
        if x_vel**2 + y_vel**2 < threshold: 
            # Stop the balls
            body.linearVelocity[0] = 0.0
            body.linearVelocity[1] = 0.0
        else:
            dv = -MU * g * unit(body.linearVelocity) * TIME_STEP
            body.linearVelocity += dv;

def dot(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1]

def unit(vector):
    return vector / sqrt(vector[0]**2 + vector[1]**2)

def vector_circle_intersect(position, radius, source, finish):
	# '''Check if a line segment intersects with a circle.'''
    # This formula works for a ball centered at the origin.
    # Thus, we normalize by subtracting the position of the ball from the source and finish positions.
    source_normal = source - position
    finish_normal = finish - position

    # Rename some things.
    x_1 = source_normal[0]
    y_1 = source_normal[1]
    x_2 = finish_normal[0]
    y_2 = finish_normal[1]

    # Plug and chug.
    d_r = sqrt((x_2 - x_1)**2 + (y_2 - y_1)**2)
    det = x_1 * y_2 - x_2 * y_1
    delta = 4 * radius**2 * d_r**2 - det**2

    # Check for intersection.
    return delta >= 0
