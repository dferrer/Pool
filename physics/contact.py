from Box2D import b2ContactListener, b2PolygonShape
from common import remove

class ContactListener(b2ContactListener):
    def __init__(self):
        b2ContactListener.__init__(self)
        self.to_destroy = []

    def DestroyBalls(self, world):
        for ball in self.to_destroy:
            # world.DestroyBody(ball)
            remove(ball)
        self.to_destroy = []

    def PreSolve(self, contact, _):
        if contact.touching:
            if type(contact.fixtureA.shape) is b2PolygonShape and len(contact.fixtureA.shape.vertices) == 14:
                self.to_destroy.append(contact.fixtureB.body)
            elif type(contact.fixtureB.shape) is b2PolygonShape and len(contact.fixtureB.shape.vertices) == 14:
                self.to_destroy.append(contact.fixtureA.body)
