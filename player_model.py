from math import pi
import math

# Third-party packages
import pyglet
from pyglet.gl import *

# Modules from this project
from util import load_image

__all__ = (
    'BoxModel',
)


def get_texture_coordinates(x, y, height, width, texture_height, texture_width):
    if x == -1 and y == -1:
        return ()
    x /= float(texture_width)
    y /= float(texture_height)
    height /= float(texture_height)
    width /= float(texture_width)
    return x, y, x + width, y, x + width, y + height, x, y + height

# not good at calculating coordinate things...there may be something wrong...
class BoxModel(object):
    # top bottom left right front back
    textures = [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)]
    texture_data = None
    display = None
    position = (0,0,0)
    rotate_angle = (0, 0, 0)

    def __init__(self, length, width, height, texture, pixel_length, pixel_width, pixel_height):
        self.image = texture

        self.length, self.width, self.height = length, width, height
        self.pixel_length, self.pixel_width, self.pixel_height = pixel_length, pixel_width, pixel_height
        self.texture_height = self.image.height
        self.texture_width = self.image.width

    def get_texture_data(self):
        texture_data = []
        texture_data += get_texture_coordinates(self.textures[0][0], self.textures[0][-1], self.pixel_width, self.pixel_length, self.texture_height, self.texture_width)
        texture_data += get_texture_coordinates(self.textures[1][0], self.textures[1][-1], self.pixel_width, self.pixel_length, self.texture_height, self.texture_width)
        texture_data += get_texture_coordinates(self.textures[2][0], self.textures[2][-1], self.pixel_height, self.pixel_width, self.texture_height, self.texture_width)
        texture_data += get_texture_coordinates(self.textures[3][0], self.textures[3][-1], self.pixel_height, self.pixel_width, self.texture_height, self.texture_width)
        texture_data += get_texture_coordinates(self.textures[4][0], self.textures[4][-1], self.pixel_height, self.pixel_length, self.texture_height, self.texture_width)
        texture_data += get_texture_coordinates(self.textures[-1][0], self.textures[-1][-1], self.pixel_height, self.pixel_length, self.texture_height, self.texture_width)
        return texture_data

    def update_texture_data(self, textures):
        self.textures = textures
        self.texture_data = self.get_texture_data()

        self.display = pyglet.graphics.vertex_list(24,
            ('v3f/static', self.get_vertices()),
            ('t2f/static', self.texture_data),
        )

    def get_vertices(self):
        xm = -self.length/2
        xp = self.length/2
        ym = -self.height/2
        yp = self.height/2
        zm = -self.width/2
        zp = self.width/2

        vertices = (
            xm, yp, zm,   xm, yp, zp,   xp, yp, zp,   xp, yp, zm,  # top
            xm, ym, zm,   xp, ym, zm,   xp, ym, zp,   xm, ym, zp,  # bottom
            xm, ym, zm,   xm, ym, zp,   xm, yp, zp,   xm, yp, zm,  # left
            xp, ym, zp,   xp, ym, zm,   xp, yp, zm,   xp, yp, zp,  # right
            xm, ym, zp,   xp, ym, zp,   xp, yp, zp,   xm, yp, zp,  # front
            xp, ym, zm,   xm, ym, zm,   xm, yp, zm,   xp, yp, zm,  # back
        )
        return vertices

    def draw(self,rotate=True):
        glPushMatrix()
        glBindTexture(self.image.texture.target, self.image.texture.id)
        glEnable(self.image.texture.target)
        glTranslatef(*self.position)
        glRotatef(pi * (180 / float(pi)), 0.0, 1.0, 0.0)
        
        x,y = self.rotation
        if rotate:
            glRotatef(-x, 0, 1, 0)
        #glRotatef(x, 0, 0, 1)
        #glRotatef(x, 1, 0, 0)
        self.display.draw(GL_QUADS)
        glPopMatrix()

BODY_HEIGHT = 2.0 / 3.0
BODY_LENGTH = BODY_HEIGHT * (2.0 / 3.0) 
BODY_WIDTH = BODY_LENGTH / 2
HEAD_LENGTH = BODY_LENGTH
HEAD_WIDTH = HEAD_LENGTH
HEAD_HEIGHT = HEAD_LENGTH
ARM_HEIGHT = BODY_HEIGHT
ARM_LENGTH = BODY_WIDTH
ARM_WIDTH = BODY_WIDTH
LEG_HEIGHT = BODY_HEIGHT
LEG_LENGTH = BODY_WIDTH
LEG_WIDTH = BODY_WIDTH

class PlayerModel(object):
    def __init__(self, position,rotation):
        self.position = None
        image = load_image('resources', 'mob', 'char.png')
        # arm move
        self.arm_dir = True
        self.arm_move = 0
        
        # head
        self.head = BoxModel(HEAD_LENGTH, HEAD_WIDTH, HEAD_HEIGHT, image, 32, 32, 32)
        self.head.update_texture_data([(32, 96), (64, 96), (0, 64), (64, 64), (32, 64), (96, 64)])
        # body
        self.body = BoxModel(BODY_LENGTH, BODY_WIDTH, BODY_HEIGHT, image, 32, 16, 48)
        self.body.update_texture_data([(80, 48), (112, 48), (64, 0), (112, 0), (80, 0), (128, 0)])
        # left/right arm
        self.left_arm = BoxModel(ARM_LENGTH, ARM_WIDTH, ARM_HEIGHT, image, 16, 16, 48)
        self.left_arm.update_texture_data([(176, 48), (176 + 16, 48), (176, 0), (176 + 32, 0), (176 - 16, 0), (176 + 16, 0)])
        self.right_arm = BoxModel(ARM_LENGTH, ARM_WIDTH, ARM_HEIGHT, image, 16, 16, 48)
        self.right_arm.update_texture_data([(176, 48), (176 + 16, 48), (176, 0), (176 + 32, 0), (176 - 16, 0), (176 + 16, 0)])
        # left/right leg
        self.left_leg = BoxModel(LEG_LENGTH, LEG_WIDTH, LEG_HEIGHT, image, 16, 16, 48)
        self.left_leg.update_texture_data([(16, 48), (16 + 16, 48), (0, 0), (32, 0), (16, 0), (48, 0)])
        self.right_leg = BoxModel(LEG_LENGTH, LEG_WIDTH, LEG_HEIGHT, image, 16, 16, 48)
        self.right_leg.update_texture_data([(16, 48), (16 + 16, 48), (0, 0), (32, 0), (16, 0), (48, 0)])

        self.update_position(position,rotation)

    def update_position(self, position, rotation, init=False):
        if self.position:
            pos_diff = math.sqrt((position[0]-self.position[0])**2+(position[1]-self.position[1])**2+(position[1]-self.position[1])**2)
        else:
            pos_diff = 0      
        self.position = position
        x,y,z = position
        alpha = rotation[0]
        foot_height = y - 1.25
        
        arm_to_center = BODY_LENGTH/2 + ARM_LENGTH/2
        leg_to_center = LEG_LENGTH/2
        
        rdx=math.cos(math.radians(alpha))
        rdz=math.sin(math.radians(alpha))
        
        dx = math.cos(math.radians(alpha - 90))
        dz = math.sin(math.radians(alpha - 90))
        
        if pos_diff:     
            if self.arm_dir:
                self.arm_move +=0.01
            else:
                self.arm_move -=0.01             
            if self.arm_move >0.2 or self.arm_move < -0.2:
                self.arm_dir = not self.arm_dir
                         
        self.head.position =    (x,              foot_height + LEG_HEIGHT + BODY_HEIGHT, z)
        self.body.position =    (x,              foot_height + LEG_HEIGHT              , z)
        self.left_arm.position =(x - arm_to_center*rdx-self.arm_move*dx,foot_height + LEG_HEIGHT, z - arm_to_center*rdz-self.arm_move*dz)
        self.right_arm.position=(x + arm_to_center*rdx+self.arm_move*dx,foot_height + LEG_HEIGHT, z + arm_to_center*rdz+self.arm_move*dz)
        self.left_leg.position =(x - leg_to_center*rdx+self.arm_move*dx, foot_height, z - leg_to_center*rdz+self.arm_move*dz)
        self.right_leg.position=(x + leg_to_center*rdx-self.arm_move*dx, foot_height, z + leg_to_center*rdz-self.arm_move*dz)
        self.head.rotation=rotation
        self.body.rotation=rotation
        self.left_arm.rotation=rotation
        self.right_arm.rotation=rotation
        self.left_leg.rotation=rotation
        self.right_leg.rotation=rotation

    def draw(self):
        self.head.draw()
        self.body.draw()
        self.left_arm.draw()
        self.right_arm.draw()
        self.left_leg.draw()
        self.right_leg.draw()