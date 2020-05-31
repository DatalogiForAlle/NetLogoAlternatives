import pyglet.graphics
import random
import math
from pyglet.window import mouse
from pyglet import clock
import time

# Inefficient drawing primitives, we'll optimize when necessary
def triangle(x1, y1, x2, y2, x3, y3, color=(0, 0, 0)):
    vertices = (x1, y1, x2, y2, x3, y3)
    pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES,
                         ('v2i', vertices),
                         ('c3B', color*3))


def line(x1, y1, x2, y2, color=(0, 0, 0)):
    vertices = (x1, y1, x2, y2)
    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                         ('v2i', vertices),
                         ('c3B', color*2))

def point(x, y, color=(0, 0, 0)):
    vertices = (x, y)
    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
                         ('v2i', vertices),
                         ('c3B', color))

def rect(x, y, width, height, color=(0, 0, 0)):
    vertices = (x, y,
                x+width, y,
                x+width, y+height,
                x, y + height)
    pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES,
                                 [0, 1, 2, 0, 2, 3],
                                 ('v2i', vertices),
                                 ('c3B', color * 4))
    
def circle(x, y, radius, color=(0, 0, 0), resolution=500):
    # TODO: Rewrite to use pyglet.gl.gluDisk for drawing
    # the circle
    vertices = [x, y]
    indices = []
    step = 360 / resolution
    for i in range(resolution):
        v = math.radians(step*i)
        cosvr = math.cos(v)*radius
        sinvr = math.sin(v)*radius
        vx = int(x + cosvr - sinvr)
        vy = int(y + sinvr + cosvr)
        vertices.extend([vx, vy])
        if i < resolution - 1:
            indices.extend([0, i+1, i+2])
        else:
            indices.extend([0, i+1, 1])
    pyglet.graphics.draw_indexed(resolution + 1,
                                 pyglet.gl.GL_TRIANGLES,
                                 indices,
                                 ('v2f', vertices),
                                 ('c3B', color * (resolution + 1)))


def text(label, x, y, color=(255, 255, 255), font_size=12):
    label_ = pyglet.text.Label(
        label,
        font_name='Tahoma',
        font_size=font_size,
        x=x, y=y,
        anchor_x='center', anchor_y='center',
        color=(255, 255, 255 ,255)
    )
    label_.draw()

def diamond(x, y, width, height, color):
    # TODO: Specify in terms of a polygon primitive
    halfw = width//2
    halfh = height//2
    vertices = (x, y,
                x, y+halfh,
                x+halfw, y,
                x,y-halfh,
                x-halfw,y)
    pyglet.graphics.draw_indexed(5,
                                 pyglet.gl.GL_TRIANGLES,
                                 [0,1,2,0,2,3,0,3,4,0,4,1],
                                 ('v2f', vertices),
                                 ('c3B', color * 5))


def remap(value, start1, stop1, start2, stop2):
    """Map a value from one range to another"""
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))
    
class Widget:
    def __init__(self):
        pass

    def on_mouse_move(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass


class Button(Widget):
    def __init__(self, x, y, w, h, label, f, obj=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.callback = f
        self.label = label
        self.obj = obj
        self.mouse_hover = False
        self.mouse_down = False
        self.color = (122, 164, 214)
        self.color_hover = (95, 130, 173)

    def render(self):
        if self.mouse_hover and not self.mouse_down:
            color = self.color_hover
        else :
            color = self.color
        rect(self.x, self.y, self.w, self.h, color)
        text(self.label, self.x+self.w/2, self.y+self.h/2)

    def on_mouse_move(self, mx, my, dx, dy):
        self.mouse_hover = ((self.x < mx)
                           and (mx < self.x + self.w)
                           and (self.y < my)
                           and (my < self.y + self.h))

    def on_mouse_press(self, x, y, button, modifiers):
        if self.mouse_hover:
            self.mouse_down = True
            self.callback(self.obj)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_down = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_move(x, y, dx, dy)


class ButtonToggle(Button):
    def __init__(self, x, y, w, h, label, f, obj=None):
        self.active = False
        super().__init__(x, y, w, h, label, lambda w: None, obj)
        self.callback = f

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        if self.mouse_hover and self.mouse_down:
            self.active = not self.active
            if self.active:
                pyglet.clock.schedule_interval(self.callback, 1.0/60)
            else:
                pyglet.clock.unschedule(self.callback)
        
    def render(self):
        super().render()
        if self.active:
            color = (0, 240, 0)
        else:
            color = (0, 100, 0)
        diamond(self.x+20, self.y+16, 20, 20, color)


class Slider(Widget):
    def __init__(self, x, y, w, h, label, minval, maxval, initial_value):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.minval = minval
        self.maxval = maxval
        self.v = initial_value
        self.variable = label
        self.color = (122, 164, 214)

    def render(self):
        rect(self.x, self.y, self.w, self.h, self.color)
        text(str(self.variable), self.x+self.w/2, self.y+3*self.h/4, font_size=10)
        text(str(self.minval), self.x+10, self.y+3*self.h/4-5, font_size=8)
        text(str(self.maxval), self.x+self.w-10, self.y+3*self.h/4-5, font_size=8)
        # Slider
        sliderWidth=self.w-14
        line(self.x+7, self.y+8, self.x+self.w-7, self.y+8)
        handleWidth = 4
        handleHeight = 12
        offset = int(remap(self.v, self.minval, self.maxval, 0, sliderWidth))
        rect(self.x+7+offset-handleWidth//2, self.y+8-handleHeight//2, handleWidth, handleHeight, color=(255, 255, 255))

    def on_mouse_move(self, mx, my, dx, dy):
        self.mouse_hover = ((self.x < mx)
                           and (mx < self.x + self.w)
                           and (self.y < my)
                           and (my < self.y + self.h))
        
    def on_mouse_press(self, x, y, button, modifiers):
        if self.mouse_hover:
            self.mouse_down = True
            if x - self.x < 7:
                self.v = self.minval
            elif x - self.x > self.w-7:
                self.v = self.maxval
            else:
                self.v = remap(x - self.x - 7, 0, self.w-14, self.minval, self.maxval)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_down = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_move(x, y, dx, dy)
        if self.mouse_down:
            self.on_mouse_press(x, y, buttons, modifiers)
        
        
class AgentWindow(pyglet.window.Window):            
    def __init__(self, width, height, config=None):
        if not config:
            config = self.defaultConfig()
        super().__init__(width, height, resizable=True, config=config)

        pyglet.gl.glLineWidth(0.5)
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        pyglet.gl.glHint(pyglet.gl.GL_LINE_SMOOTH_HINT, pyglet.gl.GL_NICEST)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        # Displays the framerate in the bottom right corner
        self.fps_display = pyglet.window.FPSDisplay(self)

        # TODO only change cursor when over interactive controller
        # hand = self.get_system_mouse_cursor(self.CURSOR_HAND)
        # self.set_mouse_cursor(hand)

        self.widgets = []

    def defaultConfig(self):
        try:
	    # Try and create a window config with multisampling (antialiasing)
            config = pyglet.graphics.Config(sample_buffers=1, samples=4,
                            depth_size=16, double_buffer=True)
        except pyglet.window.NoSuchConfigException:
            config = None

        return config

    def main_loop(self, dt):
        pass
        
    def on_draw(self):
        self.clear()
        for widget in self.widgets:
            widget.render()
        self.fps_display.draw()

    def add_widget(self, widget):
        self.widgets.append(widget)

    def on_mouse_motion(self, x, y, dx, dy):
        for widget in self.widgets:
            widget.on_mouse_move(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        for widget in self.widgets:
            widget.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        for widget in self.widgets:
            widget.on_mouse_release(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for widget in self.widgets:
            widget.on_mouse_drag(x, y, dx, dy, button, modifiers)





class TestWindow(AgentWindow):
    def on_draw(self):
        super().on_draw()
        rect(10, 200, 300, 20, color=(255, 255, 0))
        circle(400, 300, 10, color=(255, 255, 0))
        text("Hello, world", self.width//2, self.height//2)
        triangle(20, 20, 100, 100, 200, 300, color=(255, 0, 255))
        point(10, 10, color=(255, 255, 0))
        line(20, 300, 500, 200, color=(255, 0, 255))

            
def main():
    window = AgentWindow(800, 400)

    def callback(window):
        print("Hello world")
    
    window.add_widget(Button(240, 30, 140, 36, "Step", callback))
    window.add_widget(ButtonToggle(400, 30, 140, 36, "Go", callback))
    window.add_widget(Slider(560, 30, 140, 36, "Speed", 0, 10, 5))

    #window = TestWindow(800, 400)
    pyglet.clock.schedule_interval(window.main_loop, 1.0/60)
    pyglet.app.run()
    


if __name__ == "__main__":
    main()
