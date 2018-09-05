from __future__ import division

import sys
import math
import random
import time

from pyglet import clock
from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse
from model import Model
from menu import Menu

from util import *
from texture_lib import *
from block import Block
from file import File
from player import Player

from player_model import PlayerModel, BoxModel

MODE = ['pick/put','throw','destroy','self-explode']
BOMB_TYPE = ['timer bomb','remote bomb']


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        
        # init file system
        self.file = File()

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False

        # create player
        self.player = Player((0,0))
                      
        # create player model
        dx,dy,dz = self.player.get_sight_vector()
        x,y,z = self.player.position         
        self.player_model = PlayerModel((x+ND*dx,y-VIEW_DIFF,z+ND*dz),self.player.rotation)
        
        # Which sector the player is currently in.
        self.sector = None

        # The crosshairs at the center of the screen.
        self.reticle = None

        # The current block the user can place. Hit num keys to cycle.
        self.block = None

        # Convenience list of num keys.
        self.num_keys = [
            key._1, key._2, key._3, key._4]

        # Instance of the model that handles the world.
        self.model = Model()

        #label
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,x=self.width,y=self.height,
            anchor_x='right', anchor_y='top',
            color=(0, 0, 0, 255)) 
        
        #tool label
        self.tool_label = pyglet.text.Label('', font_name='Arial', font_size=18,x=0,y=self.height,
                                            anchor_x='left', anchor_y='top',
                                            color=(0, 0, 0, 255))
        
        #block zoom label
        self.zoom_label = pyglet.text.Label('', font_name='Arial', font_size=18,x=self.width//2,y=0,
                                            anchor_x='center', anchor_y='bottom',
                                            color=(0, 0, 0, 255))
        
        #create menu
        self.menu = Menu(self.width,self.height)
             
        # The crosshairs at the center of the screen.
        self.crosshair = None        
        self.crosshair_loc = [self.width//2 ,self.height//2,0]
                        
        #mouse postion
        self.mouse_pos = (0,0)
        
        self.freeze=False      
        self.open_bag=False
        self.open_menu=False
        self.open_map=False

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)
      
        #pyglet.clock.schedule_interval(self.incident, 5)

    def setup_gl(self):
        """ Basic OpenGL configuration.
    
        """
        # Set the color of "clear", i.e. the sky, in rgba.
        glClearColor(128/255, 192/255, 250/255, 0.8)
        
        # Enable culling (not rendering) of back-facing facets -- facets that aren't
        # visible to you.
        #glEnable(GL_CULL_FACE)
            
        # Set the texture minification/magnification function to GL_NEAREST (nearest
        # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
        # "is generally faster than GL_LINEAR, but it can produce textured images
        # with sharper edges because the transition between texture elements is not
        # as smooth."
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.setup_fog()

    def setup_fog(self):
        """ Configure the OpenGL fog properties.
    
        """
        # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
        # post-texturing color."
        glEnable(GL_FOG)
        # Set the fog color.
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(128/255, 192/255, 255/255, 0.8))
        # Say we have no preference between rendering speed and quality.
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        # Specify the equation used to compute the blending factor.
        glFogi(GL_FOG_MODE, GL_LINEAR)
        # How close and far away fog starts and ends. The closer the start and end,
        # the denser the fog in the fog range.
        glFogf(GL_FOG_START, 20.0)
        glFogf(GL_FOG_END, 60.0)
        
    def disableFog(self):
        glDisable(GL_FOG)

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive
        
    def incident(self,dt):
        for i in range(30):
            key,texture=random.choice(list(DISPLAY2TEXTURE.items()))
            position = (random.randint(-50, 50),random.randint(0, 20),random.randint(-50, 50))           
            self.model._update_block(position,texture)
            self.model.add_block(position,texture) 
            #self.model.create_block(position,texture,speed=0,acceleration_y=GRAVITY)             

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        if self.freeze:
            return
               
        cx,cy,i = self.crosshair_loc
        if self.crosshair:
            self.crosshair.delete()              
        self.crosshair = pyglet.graphics.vertex_list(4,('v2i', (cx - 5, cy, cx + 5, cy, cx, cy - 5, cx, cy + 5)),
                                                       ('c3B', (0, 255, 0, 0, 255, 0, 0, 255, 0, 0, 255, 0)))
        
        self.model.process_queue()
        sector = sectorize(self.player.position)
        if sector != self.sector:
            self.model.change_sectors(self.sector, sector)
            if self.sector is None:
                self.model.process_entire_queue()
            self.sector = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in range(m):
            self._update(dt / m)          
            dx,dy,dz = self.player.get_sight_vector()
            x,y,z = self.player.position                    
            self.player_model.update_position((x+ND*dx,y-VIEW_DIFF,z+ND*dz),self.player.rotation)          
            self._update_world(dt / m)
        

    def _update_world(self, dt):
        if self.model.move_set:                
            for block in self.model.move_set:            
                if block.end_position:
                    texture = block.texture
                    position = block.current_position
                    self.model.remove_block(position)
                    if block.end_position[0]:  
                        new_position=block.update_position_constant(dt)
                    else:
                        new_position=block.update_position_parabola(dt)
                    self.model.add_block(new_position, texture)
                else:
                    if block.remove_self:
                        self.model.remove_block(block.current_position)
                        if block.remove_range==2:
                            x,y,z=block.current_position
                            for pos in [(x-1,y,z),(x,y,z+1),(x,y,z-1),(x+1,y,z)]:
                                if pos in self.model.world.keys():
                                    tex = self.model.world[pos]
                                    if tex != DISPLAY2TEXTURE['stonebrick_carved']:
                                        self.model.remove_block(pos) 
                        
                    #print (block.current_position)
                    self.model.move_set.remove(block)

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # update tool range
        if self.player.tool == 0: 
            if self.player.inhand:
                self.player.tool_range = 10
            else:
                self.player.tool_range = 10
        elif self.player.tool == 1:
            self.player.tool_range = 0
        elif self.player.tool == 0:
            self.player.tool_range = 2
        else:
            self.player.tool_range = 0
        
        # walking
        speed = self.player.walkspeed
        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.player.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        # Update your vertical speed: if you are falling, speed up until you
        # hit terminal velocity; if you are jumping, slow down until you
        # start falling.
        self.player.dy -= dt * GRAVITY
        self.player.dy = max(self.player.dy, -TERMINAL_VELOCITY)
        dy += self.player.dy * dt
        # collisions
        x, y, z = self.player.position     
        #x, y, z = self.player.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT,self.model)
                
        vx,vy,vz = self.player.get_sight_vector()
        px, py, pz = x+ND*vx,y-VIEW_DIFF,z+ND*vz              
        px, py, pz = self.player.collide((px + dx, py + dy, pz + dz), PLAYER_HEIGHT-VIEW_DIFF,self.model)
        
        x, y, z = px-ND*vx,py+VIEW_DIFF,pz-ND*vz
               
        self.player.position = (x, y, z) 

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.

        """         
        if self.menu.fullscreen_label.color == (255,0,0,255):
            self.set_fullscreen(not self.fullscreen)
                   
        if self.menu.exit_label.color == (255,0,0,255):
            self.close()
            pyglet.app.event_loop.exit()     

        if self.freeze:
            if self.open_bag:
                if self.item_select:
                    self.player.inhand_display = self.item_select
                    self.player.inhand=DISPLAY2TEXTURE[self.player.inhand_display]
                    self.open_bag = False
                    self.freeze = False
                    self.set_exclusive_mouse(True)
            if self.open_menu:
                if self.menu.save_label.color == (255,0,0,255):
                    self.file.save_file(self.model)
                
                if self.menu.load_label.color == (255,0,0,255):
                    self.set_exclusive_mouse(not self.exclusive)
                    self.open_menu = not self.open_menu
                    self.freeze = not self.freeze                  
                    self.model=self.file.load_file(self.model)                                    
            return
        
        vector = self.player.get_sight_vector()
        block, previous = self.model.hit_test(self.player_model.position, vector,self.player.tool_range)
        start_pos = self.player.close_sight_vector(self.player_model.position,vector)      
        if self.exclusive:         
            if self.player.tool == 0:          
                if button == pyglet.window.mouse.LEFT and block:
                    if self.player.inhand:                       
                        self.player.put_block(self.model,vector,previous,start_pos)          
                    else:
                        self.player.take_block(self.model,block)                                                            
            elif self.player.tool == 1: # throw
                if button == pyglet.window.mouse.LEFT:
                    if self.player.inhand:                       
                        self.player.throw_block(self.model,vector,start_pos)                                          
            elif self.player.tool == 2: # destroy
                if button == pyglet.window.mouse.LEFT and block:
                    if self.model.world[block][-2] == 'stonebrick_carved':
                        return
                    self.model.remove_block(block)
            elif self.player.tool == 3:
                pass
            
            else: # do same as tool 0
                pass                      
  
    """
    def on_mouse_release(self, x, y, button, modifiers):       
        self.crosshair_loc[2]=0
        pass"""

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        
        self.mouse_pos = x,y
        
        if self.freeze:
            return
        
        if ( x > self.width//4 and x < self.width//4 * 3) and ( y > self.height//4 and y < self.height//4 * 3):
            if (x - self.width//2) * dx > 0 or (y - self.height//2) * dy > 0:
                m = 0.1
            else:
                m = 0.05
        else:
            if (x - self.width//2) * dx > 0 or (y - self.height//2) * dy > 0:
                m = 0.2
            else:
                m = 0.15

        if self.exclusive:
            x, y = self.player.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            self.player.rotation = (x, y)

    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        
        if symbol == key.B and not self.open_menu and not self.open_map: # open/close bag
            self.set_exclusive_mouse(not self.exclusive)
            self.open_bag = not self.open_bag
            self.freeze = not self.freeze
        
        if  symbol == key.M and not self.open_menu and not self.open_bag: # open/close map
            self.set_exclusive_mouse(not self.exclusive)           
            self.open_map = not self.open_map
            self.freeze = not self.freeze

        if  symbol == key.ESCAPE and not self.open_map and not self.open_bag:          
            self.set_exclusive_mouse(not self.exclusive)
            self.open_menu = not self.open_menu
            self.freeze = not self.freeze
           
        # test if shift is held down
        #if modifiers ==  key.MOD_CTRL and symbol == key.F:S              
                    
        if self.freeze:
            return
                              
        if symbol in self.num_keys:
            self.player.tool = (symbol - self.num_keys[0]) % len(MODE) 
        elif symbol == key.TAB:
            if self.player.tool < len(MODE)-1:
                self.player.tool+=1
            else:
                self.player.tool=0
                
        if symbol == key.F:                           
            self.player.inhand = None
            self.player.inhand_display = None
            
        if symbol == key.G:
            self.player.auto_store = not self.player.auto_store
                       
        if symbol == key.Q:
            if self.player.block_index==0:               
                self.player.block_index=len(self.player.block_keys)-1
            else:
                self.player.block_index-=1
            if len(self.player.block_keys)==1:
                self.player.block_index=0
            if len(self.player.block_keys)==0:
                self.player.inhand_display = None
                self.player.inhand = None
                return                       
            self.player.inhand_display = self.player.block_keys[self.player.block_index]
            self.player.inhand = DISPLAY2TEXTURE[self.player.inhand_display]
        
        if symbol == key.E:
            if self.player.block_index==(len(self.player.block_keys)-1):               
                self.player.block_index=0
            else:
                self.player.block_index+=1
            if len(self.player.block_keys)==1:
                self.player.block_index=0
            if len(self.player.block_keys)==0:
                self.player.inhand_display = None
                self.player.inhand = None
                return 
            self.player.inhand_display = self.player.block_keys[self.player.block_index]
            self.player.inhand = DISPLAY2TEXTURE[self.player.inhand_display]
           
        if symbol == key.Z:
            if self.walkspeed ==10:
                self.walkspeed=5
            else:
                self.walkspeed=10
                                              
        if symbol == key.W:
            self.player.strafe[0] -= 1
        elif symbol == key.S:
            self.player.strafe[0] += 1
        elif symbol == key.A:
            self.player.strafe[1] -= 1
        elif symbol == key.D:
            self.player.strafe[1] += 1
        elif symbol == key.SPACE:
            if self.player.dy == 0:
                self.player.dy = JUMP_SPEED               
        

    def on_key_release(self, symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """        
              
        if self.freeze:
            return      
        
        if symbol == key.W:
            self.player.strafe[0] = 0
        elif symbol == key.S:
            self.player.strafe[0] = 0
        elif symbol == key.A:
            self.player.strafe[1] = 0
        elif symbol == key.D:
            self.player.strafe[1] = 0

    def on_resize(self, width, height):
        pyglet.window.Window.on_resize(self, width, height)
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,x=width,y=height,
                                        anchor_x='right', anchor_y='top',
                                        color=(0, 0, 0, 255))        
        self.tool_label = pyglet.text.Label('', font_name='Arial', font_size=18,x=0,y=self.height,
            anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))      
        self.zoom_label = pyglet.text.Label('', font_name='Arial', font_size=18,x=self.width//2,y=0,
                                            anchor_x='center', anchor_y='bottom',
                                            color=(0, 0, 0, 255))
        
        self.menu.reload_menu_content(self.width,self.height)
             
        self.crosshair_loc = [self.width//2 ,self.height//2,0]

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width*2, height*2)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.

        """
        width, height = self.get_size()        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glViewport(0, 0, width*2, height*2)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.player.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.player.position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        """ Called by pyglet to draw the canvas.

        """          
        self.clear()
        
        self.set_3d()
        glColor3d(1, 1, 1)
        self.player_model.draw()
        #self.draw_view_spot()     
        self.model.batch.draw()
        self.draw_focused_block()
                            
        self.set_2d()
        self.draw_label()
        self.draw_tool_label()           
        #self.draw_crosshair()
        self.draw_inhand_block()
        
        if self.freeze:
            if self.open_bag:
                self.draw_bag_content()
            if self.open_menu:
                self.draw_menu_content()
            if self.open_map:
                self.draw_map_content()
 
    def draw_map_content(self):
        glColor3d(255, 255, 255)
        if self.fullscreen:
            MAP_EXPAND.blit(x=0,y=0)
        else:
            MAP_EXPAND.get_region(100, 100, 1280, 856).blit(x=0,y=0)    
        
    
    def draw_menu_content(self):
        glColor3d(255, 255, 255)
        menu = pyglet.sprite.Sprite( img=MENU_EXPAND, x=self.width//2-224,y=self.height//2-320)
        menu.draw()

        self.menu.adjust_menu_content(self.mouse_pos,self.fullscreen)
        self.menu.exit_label.draw()
        self.menu.fullscreen_label.draw()
        self.menu.save_label.draw()
        self.menu.load_label.draw()      
        pass
            
    def draw_bag_content(self):
        glColor3d(255, 255, 255)
        BAG_EXPAND.blit(x=0,y=0)       
        index = 0
        x,y = self.mouse_pos
        in_item=0
        for block_kind in self.player.bag.keys():
            quant = self.player.bag[block_kind]
            quant_label = pyglet.text.Label(str(quant), font_name='Arial', font_size=18,x=IMG_BLIT[index][0]+75,y=IMG_BLIT[index][1]+32,
                                           anchor_x='center', anchor_y='center',
                                           color=(0, 0, 0, 255))
            quant_label.draw()                         
            if x > IMG_BLIT[index][0] and y > IMG_BLIT[index][1] and x < IMG_BLIT[index][0]+64 and y < IMG_BLIT[index][1]+64:
                self.item_select = block_kind
                in_item=1
                BLOCK_MAP[block_kind].get_region(0, 0, 48, 48).blit(IMG_BLIT[index][0], IMG_BLIT[index][1])
            else:
                BLOCK_MAP[block_kind].blit(IMG_BLIT[index][0], IMG_BLIT[index][1])
            index+=1
        
        if not in_item:
            self.item_select = None
            
    def draw_view_spot(self):
        
        x,y,z=self.player.position
        dx, dy, dz=self.player.get_sight_vector()              
        ex,ey,ez=x+VIEW_END*dx,y+VIEW_END*dy,z+VIEW_END*dz
        
        #glPushMatrix()
        #glBindTexture(self.image.texture.target, self.image.texture.id)
        #glEnable(self.image.texture.target)
        #glTranslatef(*(ex,ey,ez))
        #pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES, TEXTURE_MAP['diamond'],
        #                    ('v3f', spot_vertices(ex,ey,ez,dx,dy,dz)),('t2f/static', list(MATERIAL_TRI)))
        pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,('v3f', spot_vertices(ex,ey,ez,dx,dy,dz)))
        #glPopMatrix()        

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = self.player.get_sight_vector()
        block, previous = self.model.hit_test(self.player_model.position, vector,self.player.tool_range)
        if block:
            x, y, z = block
            px,py,pz = previous
            zoom = self.model.world_zoom[block]          
            vertex_data = cube_vertices(x, y, z, zoom+0.01)
            
            # find attach side            
            a, b, c = self.player.position
            top = vertex_data[0:12]
            bottom = vertex_data[12:24]
            left = vertex_data[24:36]
            right = vertex_data[36:48]
            front = vertex_data[48:60]
            back = vertex_data[60:72]         
            face_list=(left,right,top,bottom,front,back)
            diff_list=(x-px,px-x,py-y,y-py,pz-z,z-pz)                     
            for idx,diff in enumerate(diff_list):
                if diff > 0:
                    vertex_plane = face_list[idx]
                    
            # draw attach side contour
                                                
            glColor3d(0, 255, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(4, GL_QUADS, ('v3f/static', vertex_plane))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glColor3d(255, 255, 255)
            
    def draw_inhand_block(self):
        glColor3d(255, 255, 255)
        if self.player.inhand_display:
            BLOCK_MAP[self.player.inhand_display].blit(x=0,y=self.height-128)
        else:
            pass

    def draw_label(self):
        """ Draw the label in the top left of the screen.

        """
        x, y, z = self.player.position
        dx, dy, dz = self.player.get_sight_vector()
        alpha, beta = self.player.rotation
        posx, posy = self.mouse_pos
        self.label.text = '%f (%d, %d, %d) (%f, %f ,%f) (%d, %d)' % (clock.get_fps(),x, y, z, dx, dy, dz, alpha, beta)
        self.label.draw()
        self.zoom_label.text = str(self.player.health)
        self.zoom_label.draw()
        pass
    
    def draw_tool_label(self):
        self.tool_label.text = '%s' % (MODE[self.player.tool])
        if self.player.auto_store and self.player.tool == 0:
            self.tool_label.text = '%s (auto store)' % (MODE[self.player.tool])
        self.tool_label.draw()        

    def draw_crosshair(self):
        """ Draw the crosshairs in the center of the screen.

        """
        glColor3d(0, 255, 0)
        self.crosshair.draw(GL_LINES)
        
        