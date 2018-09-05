
import pyglet
# Disable error checking for increased performance
# pyglet.options['debug_gl'] = False
from pyglet.gl import *
from window import Window
#from textwidget import Window as SaveWindow
    
def main():
    # choose platform
    platform = pyglet.window.get_platform()
    # get represent computer
    display = platform.get_default_display()
    # choose the first screen (default screen)
    screen=display.get_default_screen()
    #template = pyglet.gl.Config()
    #config = screen.get_best_config(template)
    #context =  config.create_context(None)
    window = Window(width=1280,height=856,resizable=True,caption = "no man space") 
    window.config.alpha_size = 8
     # ... perform some additional initialisation
    window.set_exclusive_mouse(True)
    
    # setup gl environment
    window.setup_gl()
    #window.set_fullscreen(fullscreen=True)
              
    pyglet.app.event_loop.run()
    
if __name__ == '__main__':
    main()