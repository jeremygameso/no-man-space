import sys
import os
import math
import random
import time

from pyglet import clock
from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

from util import *
from texture_lib import *

class Menu(object):
    
    def __init__(self, width, height):
        
        #self.batch = pyglet.graphics.Batch()
        
        self.width = width
        self.height = height
             
        #exit label in menu
        self.exit_label = pyglet.text.Label('EXIT', font_name='Comic Sans MS', font_size=18,x=self.width//2,y=self.height//2-180,
                                            anchor_x='center', anchor_y='center',
                                            color=(0, 0, 0, 255))
        # full screen label in menu
        self.fullscreen_label = pyglet.text.Label('', font_name='Comic Sans MS', font_size=18,x=self.width//2,y=self.height//2-130,
                                            anchor_x='center', anchor_y='center',
                                            color=(0, 0, 0, 255))
        
        # save game lablel
        self.save_label = pyglet.text.Label('SAVE SETTING', font_name='Comic Sans MS', font_size=18,x=self.width//2,y=self.height//2-30,
                                            anchor_x='center', anchor_y='center',
                                            color=(0, 0, 0, 255))        
        # load game label
        self.load_label = pyglet.text.Label('LOAD SETTING', font_name='Comic Sans MS', font_size=18,x=self.width//2,y=self.height//2-80,
                                            anchor_x='center', anchor_y='center',
                                            color=(0, 0, 0, 255)) 
    
    def reload_menu_content(self, width, height):
        
        self.width = width
        self.height = height
        
        self.exit_label = pyglet.text.Label('EXIT', font_name='Comic Sans MS', font_size=18,x=self.width//2,y=self.height//2-180,
                                            anchor_x='center', anchor_y='center',
                                            color=(0, 0, 0, 255))

        self.fullscreen_label = pyglet.text.Label('', font_name='Comic Sans MS', font_size=18,x=self.width//2,y=self.height//2-130,
                                            anchor_x='center', anchor_y='center',
                                            color=(0, 0, 0, 255))
        
        self.save_label = pyglet.text.Label('SAVE SETTING', font_name='Comic Sans MS', font_size=18,x=self.width//2,y=self.height//2-30,
                                            anchor_x='center', anchor_y='center',
                                            color=(0, 0, 0, 255))        

        self.load_label = pyglet.text.Label('LOAD SETTING', font_name='Comic Sans MS', font_size=18,x=self.width//2,y=self.height//2-80,
                                            anchor_x='center', anchor_y='center',
                                            color=(0, 0, 0, 255))

    def adjust_menu_content(self,mouse_pos,fullscreen):
        
        # change color to red when cursor approaching menu option
        x, y = mouse_pos
        if (x < self.width//2 + 100 and x > self.width//2 - 100 and y < self.height//2-120 and y > self.height//2-140):
            self.fullscreen_label.color=(255,0,0,255)
        else:
            self.fullscreen_label.color=(0,0,0,255)
                        
        if (x < self.width//2 + 40 and x > self.width//2 - 40 and y < self.height//2-170 and y > self.height//2-190):
            self.exit_label.color=(255,0,0,255)
        else:
            self.exit_label.color=(0,0,0,255)
            
        if (x < self.width//2 + 80 and x > self.width//2 - 80 and y < self.height//2-20 and y > self.height//2-40):
            self.save_label.color=(255,0,0,255)
        else:
            self.save_label.color=(0,0,0,255)
            
        if (x < self.width//2 + 80 and x > self.width//2 - 80 and y < self.height//2-70 and y > self.height//2-90):
            self.load_label.color=(255,0,0,255)
        else:
            self.load_label.color=(0,0,0,255)
            
        # change text based on full-screen status           
        if fullscreen:
            self.fullscreen_label.text='EXIT FULL SCREEN'
        else:
            self.fullscreen_label.text='ENTER FULL SCREEN'