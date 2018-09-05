import sys
import os
import math
import random
import time
import re

from util import *
from texture_lib import *

from textwidget import TextWidget
from textwidget import Rectangle
from model import Model

class File(object):
    
    def __init__(self):
        pass
    
    def save_file(self,model):
        
        f = open("auto_save.sav","w")
        for position,texture in model.world.items():
            pos = ','.join(str(e) for e in position)
            tex = ','.join(str(e) for e in texture)
            f.write("p({});({})\n".format(pos,tex))
        f.close()
        print ("file saved")
    
    def load_file(self,model):       
        f = open("auto_save.sav","r")
        self.world ={}
        for line in f:
            m = re.search('p\((.*)\);\((.*)\)', line)
            pos=m.group(1).split(",")
            tex=m.group(2).split(",")
            pos=[float(i) for i in pos]
            self.world[tuple(pos)]=tuple(tex)
            #print(pos)
            #print (tex)
            #model.add_block(pos, tex, immediate=False)
        f.close()
        
        del model
        return Model(mode="load",world=self.world)
            