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
from block import Block

BOUND = 40  # 1/2 width and height of world
STEP = 1 # world step size

class Model(object):

    def __init__(self,mode="init",world=None):

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}
        self.world_zoom = {}

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()
        
        # moving set of object
        self.move_set = []

        if mode == "init":
            self._initialize()
        elif mode == "load":
            self._loading(world)

    def _initialize(self):
        """ Initialize the world by placing all the blocks.

        """
        y = 0  # initial y height
        for x in xrange(-BOUND, BOUND + 1, STEP):
            for z in xrange(-BOUND, BOUND + 1, STEP):
                # create a layer stone an grass everywhere.
                self.add_block((x, y - 3, z), DISPLAY2TEXTURE['stonebrick_carved'], immediate=False)
                self.add_block((x, y - 2, z), DISPLAY2TEXTURE['redstone_ore'], immediate=False)
                self.add_block((x, y - 1, z), DISPLAY2TEXTURE['gravel'], immediate=False)
                self.add_block((x, y - 0, z), DISPLAY2TEXTURE['grass_side'], immediate=False)
                if x in (-BOUND, BOUND) or z in (-BOUND, BOUND):
                    # create outer walls.
                    for dy in xrange(-3, 8):
                        self.add_block((x, y + dy, z), ['stonebrick_carved']*6, immediate=False)
                        
        """ #add random walking block
        for i in range(5):
            x, y, z = random.randint(-50, 50),1,random.randint(-50, 50)
            block = Block((x, y, z),DISPLAY2TEXTURE['brick'],speed=5)
            ex, ey, ez = random.randint(-50, 50),1,random.randint(-50, 50)
            block.add_pinpoint((ex,ey,ez))
            self.move_set.append(block)
            self.add_block((x, y, z), DISPLAY2TEXTURE['brick'], immediate=False,zoom=0.5)"""
                   
        """
        for i in range(30):
            x, y, z = random.randint(-50, 50),random.randint(0, 20),random.randint(-50, 50)
            block = Block((x, y, z),DISPLAY2TEXTURE['brick'],speed=0,acceleration_y=GRAVITY)      
            end_point=self.check_below((x,y,z))
            if end_point:
                block.add_pinpoint(end_point)
                self.move_set.append(block)
            self.add_block((x, y, z), DISPLAY2TEXTURE['brick'], immediate=False,zoom=0.5)"""
        
        #self._show_block ((5, 2, 0), DISPLAY2TEXTURE['diamond'])
        #self.add_destroy_stage((5, 2, 0), 'destroy_stage_5')
        #self._show_tri((5, 3, 5),'diamond')

    def _loading(self,world):
        if world:
            for pos, tex in world.items():
                self.add_block(pos, tex, immediate=True)
        print ("file loaded")

    def _update_block(self,position,texture):
        block = Block(position,texture,speed=0,acceleration_y=GRAVITY)
        if not self.has_attach(position):
            end_point=self.check_below(position)
        else:
            end_point=None
        if end_point:
            block.add_pinpoint(end_point)
            self.move_set.append(block)
                            
    def hit_test(self, position, vector, max_distance=8):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                if not previous:
                    x,y,z =key
                    previous = (x,y+1,z) 
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def hit_test_focus(self, position, vector, max_distance=8):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, self.world_zoom[key]
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False
    
    def has_attach(self,position):
        x, y, z =position
        attaches = [(x+1, y, z),(x-1, y, z),(x, y, z+1),(x, y, z-1)]
        for attach in attaches:
            if attach in self.world:
                return True
        return False
    
    def has_base(self,position):
        
        x,y,z = position
        left = (x-1,y,z)
        right = (x-1,y,z)
        front = (x,y,z+1)
        back = (x,y,z-1)
        if y <= 0:
            return True
              
        if x in (-BOUND, BOUND) or z in (-BOUND, BOUND):
            return False      
        if left not in self.world.keys() and right not in self.world.keys() and front not in self.world.keys() and back not in self.world.keys():
            return False
                
        if ((x,y-1,z) not in self.world.keys()):
            return True
        else:
            return self.has_base(left) or self.has_base(right) or self.has_base(front) or self.has_base(back)
        
    def has_below(self,position):
        
        x,y,z = position
        below = (x,y-1,z)
        if below in self.world:
            return True
        else:
            return False
             
    def check_below(self,position):
        x, y, z =position
        if position in self.world:
            return (x,y+1,z)
        if (x, y-1, z) in self.world:
            return None
        y = round(y)
        for h in range (y-1,-3,-1):
            if (x,h,z) in self.world and y>h+1:
                return (x,h+1,z)
        return None

    def create_block(self, position, texture, immediate=True, zoom=0.5):
        if not self.has_base(position):
            self._update_block(position,texture)
        self.add_block(position, texture, immediate, zoom)                

    def add_block(self, position, texture, immediate=True, zoom=0.5):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.

        """      
        x, y, z = position
        
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.world_zoom[position] = zoom
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        del self.world[position]
        del self.world_zoom[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    def show_block(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)
            
    def add_destroy_stage(self,position,destroy_stage_tex):
        x, y, z = position
        #zoom = self.world_zoom[position]
        zoom=0.5
        vertex_data = cube_vertices(x, y, z, zoom)
        top = vertex_data[0:12]
        bottom = vertex_data[12:24]
        left = vertex_data[24:36]
        right = vertex_data[36:48]
        front = vertex_data[48:60]
        back = vertex_data[60:72]
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[destroy_stage_tex],
            ('v3f/static', top),
            ('t2f/static', list(MATERIAL_SQUARE))))
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[destroy_stage_tex],
            ('v3f/static', bottom),
            ('t2f/static', list(MATERIAL_SQUARE))))   
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[destroy_stage_tex],
            ('v3f/static', left),
            ('t2f/static', list(MATERIAL_SQUARE))))
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[destroy_stage_tex],
            ('v3f/static', right),
            ('t2f/static', list(MATERIAL_SQUARE))))
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[destroy_stage_tex],
            ('v3f/static', front),
            ('t2f/static', list(MATERIAL_SQUARE))))
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[destroy_stage_tex],
            ('v3f/static', back),
            ('t2f/static', list(MATERIAL_SQUARE))))
        
    def _show_tri(self,position,texture):
        x, y, z = position
        #zoom = self.world_zoom[position]
        zoom = 0.5
        x,y,z=position
        
        n=0.5
        
        bottom=(x-n,y,z-n,x+n,y,z-n,x+n,y,z+n,x-n,y,z+n)
        
        face1=(x-n,y,z-n,x+n,y,z-n, x,y+1,z)
        
        face2=(x+n,y,z-n,x+n,y,z+n, x,y+1,z)
                
        face3=(x+n,y,z+n,x-n,y,z+n, x,y+1,z)
        
        face4=(x-n,y,z+n,x-n,y,z-n, x,y+1,z)
        
        self._shown[position] = []

        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[texture],
            ('v3f/static', bottom),
            ('t2f/static', list(MATERIAL_SQUARE))))         
           
        self._shown[position].append(self.batch.add(3, GL_TRIANGLES, TEXTURE_MAP[texture],
            ('v3f/static', face1),
            ('t2f/static', list(MATERIAL_TRI))))
        
        self._shown[position].append(self.batch.add(3, GL_TRIANGLES, TEXTURE_MAP[texture],
            ('v3f/static', face2),
            ('t2f/static', list(MATERIAL_TRI))))
            
        
        self._shown[position].append(self.batch.add(3, GL_TRIANGLES, TEXTURE_MAP[texture],
            ('v3f/static', face3),
            ('t2f/static', list(MATERIAL_TRI))))
        
        self._shown[position].append(self.batch.add(3, GL_TRIANGLES, TEXTURE_MAP[texture],
            ('v3f/static', face4),
            ('t2f/static', list(MATERIAL_TRI))))       

    def _show_block (self, position, texture):
        texture_top, texture_bottom, texture_left, texture_right, texture_front, texture_back = texture
        x, y, z = position
        #zoom = self.world_zoom[position]
        zoom=0.5       
        vertex_data = cube_vertices(x, y, z, zoom)
        top = vertex_data[0:12]
        bottom = vertex_data[12:24]
        left = vertex_data[24:36]
        right = vertex_data[36:48]
        front = vertex_data[48:60]
        back = vertex_data[60:72]
        self._shown[position] = []
        
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[texture_top],
            ('v3f/static', top),
            ('t2f/static', list(MATERIAL_SQUARE))))
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[texture_bottom],
            ('v3f/static', bottom),
            ('t2f/static', list(MATERIAL_SQUARE))))   
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[texture_left],
            ('v3f/static', left),
            ('t2f/static', list(MATERIAL_SQUARE))))
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[texture_right],
            ('v3f/static', right),
            ('t2f/static', list(MATERIAL_SQUARE))))
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[texture_front],
            ('v3f/static', front),
            ('t2f/static', list(MATERIAL_SQUARE))))
        self._shown[position].append(self.batch.add(4, GL_QUADS, TEXTURE_MAP[texture_back],
            ('v3f/static', back),
            ('t2f/static', list(MATERIAL_SQUARE))))

    def hide_block(self, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.

        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        """ Private implementation of the 'hide_block()` method.

        """
        for face in self._shown.pop(position):
            face.delete()

    def show_sector(self, sector):
        """ Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector):
        """ Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.

        """
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before, after):
        """ Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.

        """
        before_set = set()
        after_set = set()
        pad = 4
        for dx in xrange(-pad, pad + 1):
            for dy in [0]:  # xrange(-pad, pad + 1):
                for dz in xrange(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.

        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.

        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.clock()
        while self.queue and time.clock() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.

        """
        while self.queue:
            self._dequeue()
            