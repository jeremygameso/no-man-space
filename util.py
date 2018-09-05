from __future__ import division

import os
import sys
import math
import random
import time
import pyglet
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

TICKS_PER_SEC = 60

BAG_LIMIT = 500

ND = 1.2
VIEW_DIFF = 1
VIEW_END = 10

# Size of sectors used to ease block loading.
SECTOR_SIZE = 32

GRAVITY = 10.0
MAX_JUMP_HEIGHT = 2.0 # About the height of a block.
# To derive the formula for calculating jump speed, first solve
#    v_t = v_0 + a * t
# for the time at which you achieve maximum height, where a is the acceleration
# due to gravity and v_t = 0. This gives:
#    t = - v_0 / a
# Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
#    s = s_0 + v_0 * t + (a * t^2) / 2
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 50

PLAYER_HEIGHT = 3

if sys.version_info[0] >= 3:
    xrange = range

MAP_EXPAND = pyglet.image.load('./resources/talabheim_paper.jpg')
BAG_EXPAND = pyglet.image.load('./resources/vintage_paper.jpg')
MENU_EXPAND = pyglet.image.load('./resources/scroll_mod.png')

MATERIAL_SQUARE = [0, 0, 1, 0, 1, 1, 0, 1]

MATERIAL_CUBE = [0, 0, 1, 0, 1, 1, 0, 1, 
                0, 0, 1, 0, 1, 1, 0, 1, 
                0, 0, 1, 0, 1, 1, 0, 1, 
                0, 0, 1, 0, 1, 1, 0, 1, 
                0, 0, 1, 0, 1, 1, 0, 1, 
                0, 0, 1, 0, 1, 1, 0, 1]

MATERIAL_TRI = [0, 0, 1, 0, 0, 1]

FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]

IMG_BLIT=[(50,750),(200,750),(350,750),(500,750),(670,750),(800,750),(950,750),
          (50,650),(200,650),(350,650),(500,650),(670,650),(800,650),(950,650),
          (50,550),(200,550),(350,550),(500,550),(670,550),(800,550),(950,550),
          (50,450),(200,450),(350,450),(500,450),(670,450),(800,350),(950,450),
          (50,350),(200,350),(350,350),(500,350),(670,350),(800,350),(950,350),
          (50,250),(200,250),(350,250),(500,250),(670,250),(800,250),(950,250),
          (50,150),(200,150),(350,150),(500,150),(670,150),(800,150),(950,150),
          (50,50),(200,50),(350,50),(500,50),(670,50),(800,50),(950,50),]

def cube_vertices(x, y, z, n):
    """ Return the vertices of the cube at position x, y, z with size 2*n.

    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]
    
def spot_vertices(x, y, z, dx, dy, dz):
    return [
    x+dx, y+dy, z+dz,
    x+dy, y+dx, z+dz,
    x+dx, y+dz, z+dy       
    ]

def normalize(position):
    """ Accepts `position` of arbitrary precision and returns the block
    containing that position.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    block_position : tuple of ints of len 3

    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)

def load_image(*args):
    path = os.path.join(*args)
    return pyglet.image.load(os.path.join(*args)) if os.path.isfile(path) else None

def sectorize(position):
    """ Returns a tuple representing the sector for the given `position`.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    sector : tuple of len 3

    """
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return (x, 0, z)