from ursina import *
import time
import math
import random
from particle import Particle

class Crowd :

    def __init__(self,rounds,on_win,on_loose,player):
        self.spawn_coords = ((-71, 1, -55),(74, 1, -50),(-60, 1, 36),(74, 1, 36))
        self.rounds = rounds
        self.manifestants = []
        self.rate = rounds[0][1]
        self.round = 0
        self.player = player
        self.t = 0
        self.start_round(0)
        self.update()
        self.on_win = on_win
        self.on_loose = on_loose
        self.update_loop = Sequence(
            Func(self.update),
            Wait(.1),
            loop=True
            )
        self.update_loop.start()
        
    def __iter__(self):
        return iter(self.manifestants)

    def start_round(self,round_nb):
        self.rate = self.rounds[round_nb][1]
        self.spawn_manifestant(self.rounds[round_nb][0])

    def next_round(self):
        print("next")
        self.round += 1
        if self.round < len(self.rounds):
            self.start_round(self.round)
        else:
            self.win()

    def clear(self):
        for man in self.manifestants:
            destroy(man)
        self.manifestants = []

    def update(self):
        
        self.t += 0.1
        if self.t >= self.rate: 
                self.t = 0
                self.spawn_manifestant(self.rounds[self.round][2])
        
        print( str(len(self.manifestants))+" enemies left")
        print(str(len(self.rounds)-self.round)+" rounds left")
        if len(self.manifestants) == 0:
            self.t = 0
            self.next_round()
        
    def win(self):
        self.clear()
        self.on_win()
        self.update_loop.kill()

    def spawn_manifestant(self,number=1):
        for i in range(number):
            spawn = random.choice(self.spawn_coords)
            position = (spawn[0]+math.cos(math.radians(45*i))*(1.2+i*0.2),1,spawn[1]+math.sin(math.radians(45*i))*(1.2+i*0.2))
            man = Manifestant(position=position,collider="box",player = self.player,crowd=self)
            self.manifestants.append(man)

    def remove_manifestant(self,manifestant):
        try :
            self.manifestants.remove(manifestant)
        except :
            pass

    def loose(self):
        self.clear()
        self.on_loose()
        self.update_loop.kill()

class Manifestant(Entity):

    def __init__(self, position, collider, player,crowd, scale=(1.2, 1, 1.2), WALKSPEED=3):
        headTexture = random.choice(['blond', 'blonde', 'brun', 'brune'])
        if headTexture.endswith("e"):
            scale = scale+(0, 0, scale[1]*0.45)
        if random.randint(0,250) == 15 :
            headTexture = 'pyweek30'
            scale = (1.2, 1, 1.2)
        super().__init__(model="plane", texture=headTexture,
                         position=position, scale=scale, collider=collider)
        self.WALKSPEED = WALKSPEED
        self.player = player
        self.pv = 100
        self.last_hit = 0
        self.last_attack = 0
        self.pancarte = Animator(animations={"idle": Entity(model="plane", texture="sign_up", position=(0, 0.1, 0), scale=(2, 0, 0.1), collider=None, parent=self), "attack": Entity(
            model="plane", texture=random.choice(["fight_down", "planet_down"]), position=(0, 0.1, 1), scale=(2, 0, 0.72), collider="box", parent=self)})

        self.bam = Audio('sign', loop=False, autoplay=False)
        self.death = Audio('death', loop=False, autoplay=False)
        self.freezed = False
        self.crowd = crowd

    def update(self):
        try :
            if self.player.enabled and self.freezed == False:
                SPEED = time.dt * self.WALKSPEED

                self.look_at(self.player)

                if self.pv > 0 :
                    if distance(self, self.player) > 1.3 and self.last_attack + 1 <= time.time():
                        z_movement = math.cos(math.radians(self.rotation_y)) * SPEED
                        x_movement = math.sin(math.radians(self.rotation_y)) * SPEED
                        

                    else:
                        z_movement, x_movement = 0, 0

                    if (x_movement, z_movement) != (0, 0) and random.randint(0, 25) == 0:
                        Particle(pos=self.position-(random.random()-0.5, 0.1, random.random()-0.5),
                                start=(0.01, 0.01), maxi=(0.2, 0.2), length=0.2)

                    self.velocity_x, self.velocity_z = x_movement, z_movement

                    if x_movement != 0:
                        direction = (1,0,0)
                        if x_movement < 0 :
                            direction = (-1,0,0)
                            x_movement
                        xRay = raycast(origin = self.world_position,direction = direction,distance = 0.75+x_movement,ignore=[self,])
                        move = True
                        for entity in xRay.entities :
                            if entity.type != 'Manifestant':
                                move = False
                            else :
                                if distance(self,entity) > 0.75 :
                                    move = False
                        if move :
                            self.x += x_movement

                    if z_movement != 0:
                        direction = (0,0,1)
                        if z_movement < 0 :
                            direction = (0,0,-1)
                            x_movement
                        zRay = raycast(origin = self.world_position,direction = direction,distance = 0.75+z_movement,ignore=[self,])
                        move = True
                        for entity in zRay.entities :
                            if entity.type != 'Manifestant':
                                move = False
                            else :
                                if distance(self,entity) > 0.75 :
                                    move = False
                        if move :
                            self.z += z_movement

                if self.last_attack + 1 <= time.time() :
                    self.pancarte.state = "idle"

                if distance(self, self.player) <= 1.3 :
                    if self.last_attack + 1 <= time.time():
                        self.pancarte.state = "idle"
                    if self.last_attack + 2 <= time.time():
                        self.attack()


            
            if self.last_hit + .3 < time.time() and self.color == color.red:
                self.color = color.white

            self.position = [round(i, 9) for i in self.position]
        except :
            pass

    def losePV(self, damage, direction= None,Power = 3):
        if self.last_hit + .3 < time.time():
            self.last_hit = time.time()
            self.pv -= damage
            self.animate_color(color.red, duration=.1, curve=curve.linear)

            for _ in range(2):
                Particle(color=color.rgb(150, 0, 0), pos=self.position-(random.random()-0.5, 0.1, random.random()-0.5),
                         start=(0.01, 0.01), maxi=(0.2, 0.2), length=0.2)
            if direction :
                z_movement = round(math.cos(math.radians(direction)) * Power,5)
                x_movement = round(math.sin(math.radians(direction)) * Power,5)

                self.animate_position(
                    self.position + (x_movement, 0, z_movement), duration=.1, curve=curve.linear)

        if self.pv <= 0:
            self.die()

        self.position = [round(i, 9) for i in self.position]

    def die(self):
        self.crowd.remove_manifestant(self)
        self.death.play()
        for elem in  self.children :
            destroy(elem,delay = .2)
        destroy(self,delay=.2)

    def attack(self):
        if self.pancarte.state == "idle":
            self.bam.play()
            self.pancarte.state = "attack"
            self.last_attack = time.time()
            self.player.hit(10)
            pancarte = self.pancarte.animations[self.pancarte.state]
            for _ in range(5):
                try :
                    Particle(color=color.rgb(150, 0, 0), pos=pancarte.world_position-(random.random()-0.5, -0.1, random.random()-0.5),
                            start=(0.01, 0.01), maxi=(0.2, 0.2), length=0.2)
                except :
                    pass

    def freeze(self,particle = True,time = 1):
        self.freezed = True
        if particle :
            for _ in range(4):
                Particle(color=color.rgb(150, 150, 250), pos=self.position-(random.random()-0.5, -0.1, random.random()-0.5),
                                        start=(0.01, 0.01), maxi=(0.2, 0.2), length=0.2)
        
        
        invoke(self.unfreeze,delay = time)
    
    def unfreeze(self):
        self.freezed = False