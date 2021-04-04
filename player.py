from ursina import *
import time
import random
import math
from particle import Particle
from ursina.prefabs.health_bar import *


class Player(Entity):

    def __init__(self, camera, ground, texture, position, collider, scale=(1, 1), WALKSPEED=3, RUNSPEED=6, velocity=(0, 0), bat_texture="bat"):
        super().__init__(model=None, position=position, collider=collider, scale=scale)
        self.entity = Entity(model="plane", texture=texture,
                             color=None, scale=(1.5, 1, 1.5), parent=self)
        bat_anim = Animation('Swoosh.gif', fps=12, loop=False, autoplay=False, parent=self.entity, rotation=(
            90, 0, 0), position=(0, -0.01, 0.4), scale=(6, 4))
        ult_anim = Animation('spin.gif', fps=4, loop=True, autoplay=True, parent=self.entity, rotation=(
            90, 0, 0), position=(0, 0.01, 0.2), scale=(4, 4.5))
        self.bat = Animator(
            animations={
                'idle': Entity(model="plane", texture=bat_texture, position=(0.5, -0.01, 0.2),
                               color=None, scale=(0.11, 1, 1), parent=self.entity),
                "attack": bat_anim,
                "ult": ult_anim
            },start_state= "idle"
        )
        self.shield = Entity(model="plane", texture="shield", position=(0, 1, 0.5),
                               color=None, scale=(1.2, 1, 0.26), parent=self.entity,visible = False)
        self.health_bar = HealthBar(max_value=100, show_text=False, roundness=.5)
        self.ui = {"ult": Button(texture="Spin.jpg",color = color.white,scale = .08,highlight_color=color.white,pressed_color =color.white,position = (.4 * window.aspect_ratio, .45),
            origin = (-.5, .5)),"dash": Button(texture="dash",color = color.white,scale = .08,highlight_color=color.white,pressed_color =color.white,position = (.4 * window.aspect_ratio, .45),
            origin = (.7, .5)),"flash": Button(texture="flash.jpg",color = color.white,scale = .08,highlight_color=color.white,pressed_color =color.white,position = (.4 * window.aspect_ratio, .45),
            origin = (1.9, .5))}


        self.velocity_x, self.velocity_z = velocity
        self.camera = camera
        self.WALKSPEED = WALKSPEED
        self.RUNSPEED = RUNSPEED
        self.crowd = None

        self.pv = 100
        self.last_normal_bat = 0
        self.last_flash = 0
        self.last_dash = 0
        self.last_ult = time.time()-10

        self.bat_wipe = Audio('bat', loop=False, autoplay=False)
        self.walk = Audio('walk', loop=True, autoplay=False)
        self.walk.volume = 0
        self.walk.play()



        self.invincible = True

    def ult_hit(self):
        for entity in self.crowd:
                    if entity.type == "Manifestant" :
                        try :
                            if distance(self.position, entity.position) < 3:
                                entity.losePV(75)
                        except :
                            pass
    
    def update(self):

        SPEED = time.dt * self.WALKSPEED
        if held_keys['shift']:
            SPEED = time.dt * self.RUNSPEED

        z_movement = round(held_keys['z'] * SPEED + -held_keys['s'] * SPEED, 5)
        x_movement = round(held_keys['d'] * SPEED + -held_keys['q'] * SPEED, 5)
        
        if self.last_ult + 5 <= time.time():
            self.entity.look_at(
                (mouse.x+self.entity.x, self.entity.y, mouse.y+self.entity.z))
        else:
            self.ult_hit()
            z_movement *= 0.4
            x_movement *= 0.4

        if (x_movement, z_movement) != (0, 0) and random.randint(3, 7) == 5:
            Particle(pos=self.position-(random.random()-0.5, 0.1, random.random()-0.5),
                     start=(0.01, 0.01), maxi=(0.2, 0.2), length=0.2)

        if (self.velocity_z, self.velocity_x) != (0, 0) and (x_movement, z_movement) == (0, 0):
            self.walk.fade_out()
            self.walk.play()
        if (self.velocity_z, self.velocity_x) == (0, 0) and (x_movement, z_movement) != (0, 0):
            self.walk.fade_in(value=5)

        self.velocity_x, self.velocity_z = x_movement, z_movement

        if self.last_ult + 20 > time.time():
            self.ui["ult"].color = color.gray
        else :
            self.ui["ult"].color = color.white

        if self.last_flash + 2 > time.time():
            self.ui["flash"].color = color.gray
        else :
            self.ui["flash"].color = color.white

        if self.last_dash + 3 > time.time():
            self.ui["dash"].color = color.gray
        else :
            self.ui["dash"].color = color.white

        if x_movement != 0:
            direction = (1, 0, 0)
            if x_movement < 0:
                direction = (-1, 0, 0)
                x_movement
            xRay = raycast(origin=self.world_position, direction=direction,
                           distance=0.75+x_movement, ignore=[self, ])
            move = True
            for entity in xRay.entities:
                if entity.type != 'Manifestant':
                    move = False
            if move:
                self.x += x_movement

        if z_movement != 0:
            direction = (0, 0, 1)
            if z_movement < 0:
                direction = (0, 0, -1)
                x_movement
            zRay = raycast(origin=self.world_position, direction=direction,
                           distance=0.75+z_movement, ignore=[self, ])
            move = True
            for entity in zRay.entities:
                if entity.type != 'Manifestant':
                    move = False
            if move:
                self.z += z_movement

    def input(self, key):
        if self.bat.state != "ult":
            if key == "left mouse down":
                self.coupdbat()
            if key == "a":
                self.flash_grenade()
            if key == "e":
                self.shield_dash()
            if key == "r":
                self.ultimate()

    def coupdbat(self):
        if self.last_normal_bat + .25 <= time.time():
            self.bat_wipe.play()
            self.last_normal_bat = time.time()
            self.bat.state = "attack"
            self.bat.animations["attack"].start()
            invoke(setattr, self.bat, 'state', "idle", delay=.15)
            cast = boxcast(origin=self.position, direction=self.entity.forward,
                           distance=1.6, ignore=[self, ], thickness=(2.5, 1))
            if cast.hit:
                for man in cast.entities:
                    if man.type == 'Manifestant':
                        man.losePV( 35,self.entity.rotation_y)

    def flash_grenade(self):
        if self.last_flash + 2 <= time.time():
            pos = self.position + (mouse.x*21, 0.01, mouse.y*21)
            

            if distance(pos, self.position) < 9:
                for i in range(25):
                    angle = 14.4 * i
                    x = math.sin(math.radians(angle))*6
                    z = math.cos(math.radians(angle))*6
                    Particle(pos=pos, start=(0.01, 0.01), maxi=(0.2, 0.2), length=random.random()/2, color=color.rgb(
                        255, random.randint(0, 255), 0), velocity=(x, z))
                for element in self.crowd:
                    if element.type == "Manifestant" :
                        try :
                            if distance(pos, element.position) < 3:
                                element.freeze()
                        except :
                            pass
                self.last_flash = time.time()

    def shield_dash(self) :
        if self.last_dash + 3 <= time.time():
            Power =5
            z_movement = round(math.cos(math.radians(self.entity.rotation_y)) * Power,5)
            x_movement = round(math.sin(math.radians(self.entity.rotation_y)) * Power,5)

            cast = boxcast(origin=self.position, direction=self.entity.forward,
                            distance=Power+.5, ignore=[self, ], thickness=(1.8, 1))
            self.shield.visible = True
            self.invincible = True
            if cast.hit:
                for man in cast.entities:
                    if man.type == 'Manifestant':
                        man.losePV( 70,self.entity.rotation_y+random.choice((90,-90)))
            self.animate_position(
                self.position + (x_movement, 0, z_movement), duration=.1, curve=curve.linear)
            
            for _ in range(10):
                coef = random.random()
                Particle(pos = self.position + (x_movement*coef+random.random(), 1, z_movement*coef+random.random()),start =(0.05,0.05),maxi =(0.1,0.1),length=0.5,color=color.rgb(100,100,255))
            invoke(setattr,self.shield,"visible",False,delay = .15)
            invoke(setattr,self,"invincible",False,delay = .15)
            
            self.last_dash = time.time()

    def ultimate(self):
        if self.last_ult + 20 <= time.time():
            self.invincible = True
            self.bat.state = "ult"
            self.entity.animate_rotation((0,360,0),duration = .2, loop=True,curve = curve.linear)
            invoke(setattr, self.bat, 'state', "idle", delay=5)
            invoke(setattr, self, 'invincible', False, delay=5)
            self.last_ult = time.time()

    def hit(self, damage):
        if not self.invincible :
            self.pv -= damage
            #self.camera.overlay.animate_color(color.rgba(255,0,0,100-self.pv),duration = 0.5)
        if self.pv <= 0:
            self.health_bar.value = 0
            self.die()
        else:
            self.health_bar.value = self.pv

    def swap_crowd(self, crowd):
        self.crowd = crowd

    def die(self):
        for i in range(15):
            Particle(pos=self.position-((random.random()-0.5) * 4, 0.1, (random.random()-0.5) * 8),
                     start=(random.random()*10, random.random()*10), maxi=(random.random()*30, random.random()*30), length=5, loop=False, color=color.rgb(random.randint(50, 150), 0, 0), always_on_top=True)
        self.visible = False
        self.crowd.loose()
        self.disable()
