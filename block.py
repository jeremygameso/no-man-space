from __future__ import division

import sys
import math
import random
import time

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

from util import *
from texture_lib import *
from pyexpat import model


class Block(object):
    
    def __init__(self,position,texture,model,vector,speed=5,zoom=0.5):       
        self.texture=texture      
        self.current_position=position
        self.model=model
        self.vector=vector
        self.end_position=[]
        self.speed=speed
        
        self.remove_self=False
        
        self.remove_range=2
        
        dx,dy,dz = self.vector    
        self.speed_y = self.speed*dy
        
        self.zoom=zoom
        
    def add_pinpoint(self,end_position):
        self.end_position.append(end_position)
        
    def update_position_parabola(self,dt):
        
        x, y, z =self.current_position
        
        dx,dy,dz = self.vector
        
        self.speed_y -= GRAVITY*dt
        
        dx = self.speed*dx*dt
        dy = self.speed_y*dt
        dz = self.speed*dz*dt
        
        self.current_position=(x+dx,y+dy,z+dz)         
        
        np=normalize(self.current_position)
        
        if np in self.model.world.keys():
            if self.model.world[np] != DISPLAY2TEXTURE["stonebrick_carved"]:
            
                self.remove_self=True
                self.end_position.pop(0)
                self.current_position=np
            
            else:                      
                nx,ny,nz=np
                while np in self.model.world.keys():
                    #print ("stuck")
                    #print (np)
                    n=1
                    new_np=normalize((nx-n*dx,ny-n*dy,nz-n*dz))
                    while new_np == np:
                        n+=1
                        new_np=normalize((nx-n*dx,ny-n*dy,nz-n*dz))
                        #print ("stucky")
                        #print (new_np)             
                    np=new_np
                np=self.model.check_below(np)
                self.end_position.pop(0)
                self.end_position.insert(0,np)
        
        return self.current_position
       
    def update_position_constant(self,dt):
        
        x, y, z =self.current_position
        ex, ey, ez = self.end_position[0]
                    
        dx = (self.speed)*dt*(ex-x)/ math.sqrt((ex-x)**2+(ey-y)**2+(ez-z)**2)
        dy = (self.speed)*dt*(ey-y)/ math.sqrt((ex-x)**2+(ey-y)**2+(ez-z)**2)
        dz = (self.speed)*dt*(ez-z)/ math.sqrt((ex-x)**2+(ey-y)**2+(ez-z)**2)       
        self.current_position=(x+dx,y+dy,z+dz)
                  
        if abs(x+dx-ex) < 0.05 and abs(y+dy-ey) < 0.05 and abs(z+dz-ez) < 0.05:
            self.current_position=self.end_position[0]
            last=self.end_position.pop(0)           
            return last
            
        return self.current_position
    
    def update_position_fall(self,dt):
        pass
    
class Bomb(Block):
    
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        
    def arm_timer(self,timer):
        self.timer = timer
        pass
    
    def time_elapse(self,dt):
        if self.timer > 0:
            self.timer -= dt
            
        else:
            self.timer = 0
        if self. timer  == 0:
            self.explode()
                    
    def explode(self):
        pass
        