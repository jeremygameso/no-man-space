import pyglet

class Test(object):
    def setUp(self):
        self.window = pyglet.window.Window()

    def tearDown(self):
        self.window.close()
        del self.window

    def wtf(self):
        self.setUp()
        #self.tearDown()
        self.setUp()
        pyglet.app.run()

#test = Test()
#test.wtf()

print (True or False or False)