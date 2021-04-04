import sys

# The major, minor version numbers your require
MIN_VER = (3, 5)

if sys.version_info[:2] < MIN_VER:
    sys.exit(
        "This game requires Python {}.{}.".format(*MIN_VER)
    )

from player import Player
from manifestants import Manifestant, Crowd
from particle import Particle
from ursina import *
import random
import csv



window.title = "Protest Arrests"

application.development_mode = False
app = Ursina()
window.icon = "icon"
window.fps_counter.enabled = False
window.exit_button.input = None


def on_win():
    bg = Entity(parent=camera.ui, model='quad', scale_x=camera.aspect_ratio, color=color.black, z=1)
    bg.scale *= 400
    win = Text(parent = camera.ui,text='You won in '+str(round(time.time()-start,3))+'s', origin=(0,0), color=color.clear,scale =2)
    win.animate_color(color.white,duration = 1)
    create = Text(parent = camera.ui,text='Made by ano002 & NufNuf', origin=(0,1.5), color=color.clear,scale =1)
    create.animate_color(color.white,duration = 1)


def on_loose():
    bg = Entity(parent=camera.ui, model='quad', scale_x=camera.aspect_ratio, color=color.rgb(150, 0, 0), z=1)
    bg.scale *= 400
    win = Text(parent = camera.ui,text='You lost ;C', origin=(0,0), color=color.clear,scale =2)
    win.animate_color(color.white,duration = 1)
    create = Text(parent = camera.ui,text='Made by ano002 & NufNuf', origin=(0,1.5), color=color.clear,scale =1)
    create.animate_color(color.white,duration = 1)

ground = Entity(model='plane', scale_x=240, scale_z=240,
                texture="map", texture_scale=(1, 1))

player = Player(camera, ground, texture="CRS", position=(
    0, 0.5, 0), collider='box', WALKSPEED=5, RUNSPEED=9)

level1 = Crowd([[12,50,4],[20,40,4],[22,30,5]],on_win,on_loose,player)

player.swap_crowd(level1)


camera.parent = player
#EditorCamera()
camera.position = (0, 45, 0)
camera.rotation = (90, 0, 0)
#camera.overlay.color = color.rgba(255,255,255,0)


with open('map.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
    for z, row in enumerate(reader):
        for x, elem in enumerate(row):
            if int(elem) in [57, 66, 67, 70, 71]:
                Entity(model='cube', position=((x+0.5)*2-120, 1, -(z+0.5) *
                                               2+120), color=color.clear, scale=(2, 1, 2), collider='box')
            if int(elem) == 77:
                Entity(model='cube', position=((x)*2-120, 1, -(z+1)*2+120),
                       color=color.clear, scale=(4, 1, 4), collider='box')

Walls = [
    Entity(model='cube', position=((11)*2-120, 1, -(12.5)*2+120),
           color=color.clear, scale=(43, 1, 50), collider='box'),
    Entity(model='cube', position=((11)*2-120, 1, -(52)*2+120),
           color=color.clear, scale=(43, 1, 43), collider='box'),
    Entity(model='cube', position=((11)*2-120, 1, -(96)*2+120),
           color=color.clear, scale=(43, 1, 96), collider='box'),
    Entity(model='cube', position=((72)*2-120, 1, -(102)*2+120),
           color=color.clear, scale=(68, 1, 72), collider='box'),
    Entity(model='cube', position=((54)*2-120, 1, -(107)*2+120),
           color=color.clear, scale=(6, 1, 50), collider='box'),
    Entity(model='cube', position=((70.5)*2-120, 1, -(13)*2+120),
           color=color.clear, scale=(74, 1, 54), collider='box'),
    Entity(model='cube', position=((113)*2-120, 1, -(78.5)*2+120),
           color=color.clear, scale=(28, 1, 166), collider='box'),
    Entity(model='cube', position=((113)*2-120, 1, -(14.5)*2+120),
           color=color.clear, scale=(28, 1, 58), collider='box'),
    Entity(model='cube', position=((115)*2-120, 1, -(33)*2+120),
           color=color.clear, scale=(20, 1, 16), collider='box')
]

music = Audio('audioloop', loop=True, autoplay=False)
music.volume = 0
music.play()
music.fade_in(duration=2, value=0.4)


start = time.time()
app.run()
