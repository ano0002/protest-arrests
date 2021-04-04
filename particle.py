from ursina import *
import time

class Particle(Entity):
    def __init__(self, pos, start, maxi, length, color=color.hsv(0, 0, 0.3), curve = curve.linear_boomerang,loop=False,velocity = (0,0), **kwargs):
        super().__init__(model="plane",color=color, position=pos, scale=start)
        self.maxi = maxi
        self.animate_scale(maxi, duration=length,
                           curve=curve, loop=loop)
        self.start = time.time()
        self.velocity = velocity
        self.length = length
        for key, value in kwargs.items():
            try :
                setattr(self, key, value)
            except :
                print(key,value)

    def update(self):
        self.position += Vec3(self.velocity[0]*time.dt,0,self.velocity[1]*time.dt)
        if time.time()-(self.length) > self.start:
            destroy(self)