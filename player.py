from math import cos, sin, atan2, radians, acos, pi, sqrt
import random

from util import *
from texture_lib import *
from block import Block

class Player(object):
    local_player = True

    def __init__(self,ground_position):
        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]
        
        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = (ground_position[0], PLAYER_HEIGHT, ground_position[1])
        
        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # block type in hand
        self.inhand = None
        self.inhand_display = None

        # When flying gravity has no effect and speed is increased.
        self.flying = False
       
        # walk speed
        self.walkspeed = 10
        
        # Velocity in the y (upward) direction.
        self.dy = 0
        
        # tool
        self.tool=0
        # tool max distance
        self.tool_range=3
        
        # bag, contains several blocks to put or throw
        self.bag={"diamond":100}
        self.block_keys=list(self.bag.keys())
        self.block_index=0

        # total count of blocks in bag
        self.bag_total = 0
        for key,num in self.bag.items():
            self.bag_total +=num
               
        self.health = 100
              
        self.item_select=None
        
        # grab and store token
        self.auto_store=False

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.

        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)
    
    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)
    
    def close_sight_vector(self,position,vector):
        x,y,z=position
        dx,dy,dz= vector
        dx,dy,dz=(round(dx),round(dy),round(dz))
        return ((x+dx,y+dy,z+dz))
    
    def collide(self, position, height, model):
        """ Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.

        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.05
        p = list(position)       
        np = normalize(position)
        for face in FACES:  # check all surrounding blocks
            for i in xrange(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in xrange(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) not in model.world:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) and self.dy<-8:
                        print  ("fall and hurt")
                        self.health -= 10
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0                                      
                    break
        return tuple(p)
    
    def put_block(self,model,vector,end_pos,start_pos):
        blk = Block(start_pos,self.inhand,model,vector,speed=JUMP_SPEED)
        blk.add_pinpoint(end_pos)
        model.move_set.append(blk)                       
        model.add_block(start_pos, self.inhand)
        self._consume_block_from_bag()

        
    def take_block(self,model,block):
        if model.world[block][-2] == 'stonebrick_carved':
            return
        self.inhand = model.world[block]
        self.inhand_display = self.inhand[-2]
        self._gain_block_to_bag()
        self.block_keys = list(self.bag.keys())                       
        model.remove_block(block)                      
        
        if self.auto_store:
            self.inhand_display = None
            self.inhand = None
            
    def throw_block(self,model,vector,start_pos):
        blk = Block(start_pos,self.inhand,model,vector,speed=20)
        blk.add_pinpoint(None)
        model.move_set.append(blk)                       
        model.add_block(start_pos, self.inhand)
        self._consume_block_from_bag()        
        
    def _consume_block_from_bag(self):
        if self.bag[self.inhand_display] > 1:
            self.bag[self.inhand_display]-=1
        else:
            del self.bag[self.inhand_display]
            self.block_keys=list(self.bag.keys())

            if self.block_keys: # prevent index out of range for block in bag
                if self.bag_total and self.block_keys[self._next_block_index()] in self.bag.keys():                            
                    self.inhand_display = self.block_keys[self.block_index]
                    self.inhand = DISPLAY2TEXTURE[self.inhand_display]
                else:
                    self.inhand_display = None
                    self.inhand = None 
            else:
                self.inhand_display = None
                self.inhand = None                                                       
        self.bag_total-=1
        
    def _gain_block_to_bag(self):
        if self.bag_total < BAG_LIMIT:
            if self.inhand_display not in self.bag.keys() and len(self.bag.keys())<=56: # block kind in bag must be less than 56
                self.bag[self.inhand_display]=1
            else:
                self.bag[self.inhand_display]+=1
        self.bag_total+=1        


    def _next_block_index(self):
        if self.block_index==0:               
            self.block_index=len(self.block_keys)-1
        else:
            self.block_index-=1
        return self.block_index 
