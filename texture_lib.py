from __future__ import division

import sys
import math
import random
import time
import pyglet
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse


#-------------------------------------------------------------#

TNT_TOP = './resources/blocks/tnt_top.png'
TNT_BOTTOM = './resources/blocks/tnt_bottom.png'
TNT_SIDE = './resources/blocks/tnt_side.png'
PLANKS_OAK = './resources/blocks/planks_oak.png'
REDSTONE_ORE = './resources/blocks/redstone_ore.png'
STONEBRICK_CARVED='./resources/blocks/stonebrick_carved.png'
BRICK='./resources/blocks/brick.png'
COBBLESTONE='./resources/blocks/cobblestone.png'
COBBLESTONE_MOSSY='./resources/blocks/cobblestone_mossy.png'
GRASS_SIDE ='./resources/blocks/grass_side.png'
GRASS_TOP ='./resources/blocks/grass_top_mod.png'
GRAVEL ='./resources/blocks/gravel.png'
DIAMOND ='./resources/blocks/diamond_block.png'
CACTUS_SIDE ='./resources/blocks/cactus_side.png'
CACTUS_TOP ='./resources/blocks/cactus_top.png'

DESTROY_STAGE_0='./resources/blocks/destroy_stage_0.png'
DESTROY_STAGE_1='./resources/blocks/destroy_stage_1.png'
DESTROY_STAGE_2='./resources/blocks/destroy_stage_2.png'
DESTROY_STAGE_3='./resources/blocks/destroy_stage_3.png'
DESTROY_STAGE_4='./resources/blocks/destroy_stage_4.png'
DESTROY_STAGE_5='./resources/blocks/destroy_stage_5.png'
DESTROY_STAGE_6='./resources/blocks/destroy_stage_6.png'
DESTROY_STAGE_7='./resources/blocks/destroy_stage_7.png'


# Image shown in bag as icon
BLOCK_MAP = {}
BLOCK_MAP['tnt'] = pyglet.image.load(TNT_SIDE)
BLOCK_MAP['planks_oak'] = pyglet.image.load(PLANKS_OAK)
BLOCK_MAP['redstone_ore'] = pyglet.image.load(REDSTONE_ORE)
BLOCK_MAP['stonebrick_carved'] = pyglet.image.load(STONEBRICK_CARVED)
BLOCK_MAP['brick'] = pyglet.image.load(BRICK)
BLOCK_MAP['cobblestone'] = pyglet.image.load(COBBLESTONE)
BLOCK_MAP['cobblestone_mossy'] = pyglet.image.load(COBBLESTONE_MOSSY)
BLOCK_MAP['grass_side'] = pyglet.image.load(GRASS_SIDE)
BLOCK_MAP['gravel'] = pyglet.image.load(GRAVEL)
BLOCK_MAP['diamond'] = pyglet.image.load(DIAMOND)
BLOCK_MAP['cactus'] = pyglet.image.load(CACTUS_SIDE)
BLOCK_MAP['cactus_top'] = pyglet.image.load(CACTUS_TOP)

# A TextureGroup manages an OpenGL texture.        
TEXTURE_MAP = {}
TEXTURE_MAP['tnt_top'] = TextureGroup(image.load(TNT_TOP).get_texture())
TEXTURE_MAP['tnt_bottom'] = TextureGroup(image.load(TNT_BOTTOM).get_texture())
TEXTURE_MAP['tnt'] = TextureGroup(image.load(TNT_SIDE).get_texture())
TEXTURE_MAP['planks_oak'] = TextureGroup(image.load(PLANKS_OAK).get_texture())
TEXTURE_MAP['redstone_ore'] = TextureGroup(image.load(REDSTONE_ORE).get_texture())
TEXTURE_MAP['stonebrick_carved'] = TextureGroup(image.load(STONEBRICK_CARVED).get_texture())
TEXTURE_MAP['brick'] = TextureGroup(image.load(BRICK).get_texture())
TEXTURE_MAP['cobblestone'] = TextureGroup(image.load(COBBLESTONE).get_texture())
TEXTURE_MAP['cobblestone_mossy'] = TextureGroup(image.load(COBBLESTONE_MOSSY).get_texture())
TEXTURE_MAP['grass_side'] = TextureGroup(image.load(GRASS_SIDE).get_texture())
TEXTURE_MAP['grass_top'] = TextureGroup(image.load(GRASS_TOP).get_texture())
TEXTURE_MAP['gravel'] = TextureGroup(image.load(GRAVEL).get_texture())
TEXTURE_MAP['diamond'] = TextureGroup(image.load(DIAMOND).get_texture())
TEXTURE_MAP['cactus'] = TextureGroup(image.load(CACTUS_SIDE).get_texture())
TEXTURE_MAP['cactus_top'] = TextureGroup(image.load(CACTUS_TOP).get_texture())

TEXTURE_MAP['destroy_stage_0'] = TextureGroup(image.load(DESTROY_STAGE_0).get_texture())
TEXTURE_MAP['destroy_stage_1'] = TextureGroup(image.load(DESTROY_STAGE_1).get_texture())
TEXTURE_MAP['destroy_stage_2'] = TextureGroup(image.load(DESTROY_STAGE_2).get_texture())
TEXTURE_MAP['destroy_stage_3'] = TextureGroup(image.load(DESTROY_STAGE_3).get_texture())
TEXTURE_MAP['destroy_stage_4'] = TextureGroup(image.load(DESTROY_STAGE_4).get_texture())
TEXTURE_MAP['destroy_stage_5'] = TextureGroup(image.load(DESTROY_STAGE_5).get_texture())
TEXTURE_MAP['destroy_stage_6'] = TextureGroup(image.load(DESTROY_STAGE_6).get_texture())
TEXTURE_MAP['destroy_stage_7'] = TextureGroup(image.load(DESTROY_STAGE_7).get_texture())

#-------------------------------------------------------------#

DISPLAY2TEXTURE = {}
DISPLAY2TEXTURE['tnt'] = ['tnt_top','tnt_bottom','tnt','tnt','tnt','tnt']
DISPLAY2TEXTURE['planks_oak'] = ['planks_oak']*6
DISPLAY2TEXTURE['redstone_ore'] = ['redstone_ore']*6
DISPLAY2TEXTURE['stonebrick_carved'] = ['stonebrick_carved']*6
DISPLAY2TEXTURE['brick'] = ['brick']*6
DISPLAY2TEXTURE['cobblestone'] = ['cobblestone']*6
DISPLAY2TEXTURE['cobblestone_mossy'] = ['cobblestone_mossy']*6
DISPLAY2TEXTURE['grass_side'] = ['grass_top','gravel','grass_side','grass_side','grass_side','grass_side']
DISPLAY2TEXTURE['gravel'] = ['gravel']*6
DISPLAY2TEXTURE['diamond'] = ['diamond']*6
DISPLAY2TEXTURE['cactus'] = ['cactus_top','gravel','cactus','cactus','cactus','cactus']


#-------------------------------------------------------------#

BLOCK_RESIST = {} # tough level of a block