import pyglet.graphics
import random
import math
from pyglet.window import mouse

def RNG(maximum):
    return random.randint(0,maximum)

class Agent():
    def __init__(self, x, y, area):
        self._area = area
        self._info = {}
        self.x = x
        self.y = y
        self.size = 6
        self.direction = random.randint(0,359)
        self.speed = 1
        self._destroyed = False
        self._resolution = 10
        self._init_render()

    def _init_render(self):
        rx = self._render_x()
        ry = self._render_y()
        vertices = [rx,ry]
        colors = [255,255,255]
        indices = []
        for i in range(self._resolution):
            a = i * (2 * math.pi) / self._resolution
            vertices.append(rx + math.cos(a) * self.size)
            vertices.append(ry + math.sin(a) * self.size)
            colors.extend([255, 255, 255])
            if i < (self._resolution-1):
                indices.extend([0, i+1, i+2])
            else:
                indices.extend([0, i+1, 1])
        self._vertex_list = self._area.batch.add_indexed(
            self._resolution+1, pyglet.gl.GL_TRIANGLES, self._area.agent_group,
            indices,
            ('v2f', vertices),
            ('c3B', colors)
        )

    def _wraparound(self):
        self.x = self.x % self._area.w
        self.y = self.y % self._area.h

    def jump_to(self, x, y):
        self.x = x
        self.y = y
        self._wraparound()

    def get(self, var):
        return self._info[var]

    def set(self, var, val):
        self._info[var] = val

    def point_to(self, other_x, other_y):
        dist = self.distance_to(other_x,other_y)
        self.direction = math.degrees(math.acos((self.x - other_x) / dist))

    def move(self):
        self.x += math.cos(math.radians(self.direction)) * self.speed
        self.y += math.sin(math.radians(self.direction)) * self.speed
        self._wraparound()

    def distance_to(self, other_x, other_y):
        return ((self.x-other_x)**2 + (self.y-other_y)**2)**0.5

    def current_tile(self):
        x = floor(len(self.model.tiles) * self.x / self._area.w)
        y = floor(len(self.model.tiles) * self.y / self._area.h)
        return (x,y)

    def is_destroyed(self):
        return self._destroyed

    def destroy(self):
        self._destroyed = True
        self._vertex_list.delete()

    def _render_x(self):
        return self._area.x + self.x

    def _render_y(self):
        return self._area.y + self.y

    def set_color(self, r, g, b):
        for i in range(len(self._vertex_list.colors)//3):
            self._vertex_list.colors[i*3] = r
            self._vertex_list.colors[i*3+1] = g
            self._vertex_list.colors[i*3+2] = b

    def render(self):
        x = self._render_x()
        y = self._render_y()
        vertices = [x,y]
        for i in range(self._resolution):
            a = i * (2 * math.pi) / self._resolution
            vertices.append(x + math.cos(a) * self.size)
            vertices.append(y + math.sin(a) * self.size)
        self._vertex_list.vertices = vertices

class Tile():
    def __init__(self,x,y,w,h,area):
        self.x = x
        self.y = y
        self._w = w
        self._h = h
        self._area = area
        self._info = {}
        self.color = (0,0,0)
        self._vertex_list = self._area.batch.add_indexed(
            4, pyglet.gl.GL_TRIANGLES, self._area.tile_group,
            [0,1,2,0,2,3],
            ('v2f', [self.x,self.y,
                     self.x+self._w,self.y,
                     self.x+self._w,self.y+self._h,
                     self.x,self.y+self._h]),
            ('c3B', [0,0,0,
                     0,0,0,
                     0,0,0,
                     0,0,0])
        )

    def get(self, var):
        return self._info[var]

    def set(self, var, val):
        self._info[var] = val

    def render(self):
        pass

    def set_color(self, r, g, b):
        for i in range(4):
            self._vertex_list.colors[i*3] = r
            self._vertex_list.colors[i*3+1] = g
            self._vertex_list.colors[i*3+2] = b

class SimulationArea():
    def __init__(self, x, y, w, h, n_agents, n_tiles, batch):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.n_agents = n_agents
        self.agents = set()
        self.n_tiles = n_tiles
        self.tiles = [[None for x in range(n_tiles)] for y in range(n_tiles)]
        self.batch = batch
        self.agent_group = pyglet.graphics.OrderedGroup(2)
        self.tile_group = pyglet.graphics.OrderedGroup(1)

    def reset(self):
        for a in self.agents:
            a.destroy()
        self.agents.clear()
        for i in range(self.n_agents):
            self.agents.add(Agent(random.randint(0,self.w),
                                  random.randint(0,self.h),
                                  self))
        tile_w = self.w / self.n_tiles
        tile_h = self.h / self.n_tiles
        for x in range(0,self.n_tiles):
            for y in range(0,self.n_tiles):
                self.tiles[x][y] = Tile(x*tile_w,y*tile_h,tile_w,tile_h,self)

    def render(self):
        for a in self.agents:
            a.render()
        self.batch.draw()

class Model():
    def __init__(self, n_agents, n_tiles):
        global AgentWindow
        self._buttons = set()
        self._bg_group = pyglet.graphics.OrderedGroup(0)
        self._button_group = pyglet.graphics.OrderedGroup(3)
        self._label_group = pyglet.graphics.OrderedGroup(4)
        self._render_batch = pyglet.graphics.Batch()
        self._area = SimulationArea(0,0,400,400,n_agents,n_tiles,self._render_batch)
        self._globals = {}
        win_size = AgentWindow.get_size()
        self._render_batch.add_indexed(
            4, pyglet.gl.GL_TRIANGLES, self._bg_group,
            [0, 1, 2, 0, 2, 3],
            ('v2i', (0, 0,
                     win_size[0], 0,
                     win_size[0], win_size[1],
                     0, win_size[1])),
            ('c3B', (250, 240, 230,
                     250, 240, 230,
                     250, 240, 230,
                     250, 240, 230))
        )

        pyglet.clock.schedule_interval(self.update, 0.02)

        @AgentWindow.event
        def on_draw():
            AgentWindow.clear()
            self.render()

        @AgentWindow.event
        def on_mouse_motion(x, y, dx, dy):
            for b in self._buttons:
                b.mouse_moved(x,y)

        @AgentWindow.event
        def on_mouse_press(x, y, button, modifiers):
            if button == mouse.LEFT:
                for b in self._buttons:
                    b.mouse_pressed = True

        @AgentWindow.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            for b in self._buttons:
                b.mouse_moved(x,y)

        @AgentWindow.event
        def on_mouse_release(x, y, button, modifiers):
            if button == mouse.LEFT:
                for b in self._buttons:
                    b.mouse_pressed = False

    def get(self, var):
        return self._globals[var]

    def set(self, var, val):
        self._globals[var] = val

    def get_agents(self):
        return self._area.agents

    def get_tile(self, x, y):
        return self._area.tiles[x][y]

    def get_tile_n(self):
        return self._area.n_tiles

    def reset(self):
        self._area.reset()
        pass

    def plot_variable(self, label, r, g, b):
        pass
        #self._graph.addVariable(label, r, g, b)

    def update(self, dt):
        for b in self._buttons:
            b.update()
            if type(b) is ButtonToggle:
                if b.active:
                    b.func(self)
            if type(b) is ButtonSlider:
                self._globals[b.variable] = b.get_value()

    def get_render_batch(self):
        return self._render_batch

    def get_background_group(self):
        return self._bg_group

    def get_button_group(self):
        return self._button_group

    def get_label_group(self):
        return self._label_group

    def render(self):
        self._render_batch.draw()
        for a in self._area.agents:
            a.render()
        """
        background(0,0,0)
        noStroke()
        for x in range(len(self.tiles[0])):
            for y in range(len(self.tiles)):
                if self.tiles[x][y]:
                    self.tiles[x][y].render()
        stroke(0,0,0)
        for a in self.agents:
            if a.isDestroyed():
                self.agents.remove(a)
        self._renderFunc(self.agents)
        for b in self._buttons:
            b.render()
            if type(b) is ButtonToggle:
                if b.active:
                    b.func(self)
            if type(b) is ButtonSlider:
                self.globals[b.label] = b.getValue()
        self._graph.render()
        """

    def add_single_button(self, label, func):
        button_count = len(self._buttons)
        self._buttons.add(
            Button(
                440+(button_count%2)*160,
                16+math.floor(button_count/2)*76,
                140,56,label,self,func))

    def add_toggle_button(self, label, func):
        button_count = len(self._buttons)
        self._buttons.add(
            ButtonToggle(
                440+(button_count%2)*160,
                16+math.floor(button_count/2)*76,
                140,56,label,self,func))

    def add_slider_button(self, label, min, max):
        button_count = len(self._buttons)
        self._buttons.add(
            ButtonSlider(
                440+(button_count%2)*160,
                16+math.floor(button_count/2)*76,
                140,56,label,self,min,max))

class Button(object):
    def __init__(self, x, y, w, h, label, model, f):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self.func = f
        self.state = 0 # 0=default | 1=mouse_hovering | 2=mouse_clicking
        self.counter = 0
        self.model = model
        self.mouse_hover = False
        self.mouse_pressed = False
        self.vertex_list = model.get_render_batch().add_indexed(
            4, pyglet.gl.GL_TRIANGLES, model.get_button_group(),
            [0, 1, 2, 0, 2, 3],
            ('v2i', (self._x, self._y,
                     self._x+self._w, self._y,
                     self._x+self._w, self._y+self._h,
                     self._x, self._y+self._h)),
            ('c3B', (150, 150, 150,
                     100, 100, 100,
                     150, 150, 150,
                     200, 200, 200))
        )
        self._label = pyglet.text.Label(
            label,
            font_name='Courier New',
            font_size=12,
            x=self._x+self._w/2, y=self._y+self._h/2,
            anchor_x='center', anchor_y='center',
            batch=model.get_render_batch(),
            color=(0,0,0,255),
            group=model.get_label_group()
        )

    def update(self):
        if self.state == 0 and self.mouse_hover:
            self.state = 1
            self.render_hover()
        elif self.state == 1 and self.mouse_hover:
            if self.mouse_pressed:
                self.state = 2
                self.render_click()
            else:
                self.render_hover()
        elif self.state == 2 and self.mouse_hover:
            if self.mouse_pressed:
                self.render_click()
            else:
                self.state = 0
                self.on_click()
                self.render_hover()
        else:
            self.state = 0
            self.render_default()

    def render_default(self):
        self.vertex_list.colors = [150, 150, 150,
                                   100, 100, 100,
                                   150, 150, 150,
                                   200, 200, 200]

    def render_hover(self):
        self.vertex_list.colors = [150, 150, 150,
                                   200, 200, 200,
                                   150, 150, 150,
                                   100, 100, 100]

    def render_click(self):
        self.vertex_list.colors = [100, 100, 100,
                                   150, 150, 150,
                                   100, 100, 100,
                                   50, 50, 50]

    def mouse_moved(self,mx,my):
        self.mouse_hover = ((self._x < mx)
                           and (mx < self._x + self._w)
                           and (self._y < my)
                           and (my < self._y + self._h))

    def on_click(self):
        self.func(self.model)

class ButtonToggle(Button):
    def __init__(self, x, y, w, h, label, model, f):
        super().__init__(x, y, w, h, label, model, f)
        self.active=False
        self._led_vertex_list = model.get_render_batch().add_indexed(
            5, pyglet.gl.GL_TRIANGLES, model.get_label_group(),
            [0,1,2,0,2,3,0,3,4,0,4,1,0],
            ('v2f', (self._x+self._w-15, self._y+self._h-15,
                     self._x+self._w-15, self._y+self._h-5,
                     self._x+self._w-5, self._y+self._h-15,
                     self._x+self._w-15,self._y+self._h-25,
                     self._x+self._w-25,self._y+self._h-15)),
            ('c3B', (0,100,0,
                     0,25,0,
                     0,25,0,
                     0,25,0,
                     0,25,0))
        )

    def update(self):
        super().update()
        if self.active:
            self._led_vertex_list.colors = [
                0,250,0,
                0,50,0,
                0,50,0,
                0,50,0,
                0,50,0
            ]
        else:
            self._led_vertex_list.colors = [
                0,100,0,
                0,25,0,
                0,25,0,
                0,25,0,
                0,25,0
            ]

    def on_click(self):
        self.active = not self.active

class SliderHandle(Button):
    def __init__(self, x, y, w, model):
        self.x = x
        self.y = y
        self.h = 18
        self.w = 6
        self.mouse_hover = False
        self.follow_mouse = False
        self.sliderW = w
        self.r = 50
        self.state = 0 # 0=default | 1=mouse_hovering | 2=mouse_clicking
        self._vertex_list = model.get_render_batch().add_indexed(
            4, pyglet.gl.GL_TRIANGLES, model.get_button_group(),
            [0, 1, 2, 0, 2, 3],
            ('v2f', (self.x+(self.sliderW*self.r/100)-self.w/2, self.y+self.h/2,
                     self.x+(self.sliderW*self.r/100)+self.w/2, self.y+self.h/2,
                     self.x+(self.sliderW*self.r/100)+self.w/2, self.y-self.h/2,
                     self.x+(self.sliderW*self.r/100)-self.w/2, self.y-self.h/2)),
            ('c3B', (150, 150, 150,
                     150, 150, 150,
                     150, 150, 150,
                     150, 150, 150))
        )

    def mouse_moved(self,mx,my):
        self.mouse_hover = (self.x+(self.sliderW*self.r/100)-self.w/2 < mx) and (mx < self.x+(self.sliderW*self.r/100) + self.w/2) and (self.y-self.h/2 < my) and (my < self.y + self.h/2)
        if self.follow_mouse:
            if mx < self.x:
                self.r = 0
            elif mx > self.x + self.sliderW:
                self.r = 100
            else:
                self.r = (mx - self.x) * 100 / self.sliderW

    def update(self):
        self.follow_mouse = False
        if self.state == 0 and self.mouse_hover:
            self.state = 1
            self.render_hover()
        elif self.state == 1 and self.mouse_hover:
            if self.mouse_pressed:
                self.state = 2
                self.follow_mouse = True
                self.render_click()
            else:
                self.render_hover()
        elif self.state == 2:
            if self.mouse_pressed:
                self.follow_mouse = True
                self.render_click()
            else:
                self.state = 0
                self.render_hover()
        else:
            self.state = 0
            self.render_default()
        self._vertex_list.vertices = [
            self.x+(self.sliderW*self.r/100)-self.w/2, self.y+self.h/2,
            self.x+(self.sliderW*self.r/100)+self.w/2, self.y+self.h/2,
            self.x+(self.sliderW*self.r/100)+self.w/2, self.y-self.h/2,
            self.x+(self.sliderW*self.r/100)-self.w/2, self.y-self.h/2
        ]

    def render_default(self):
        self._vertex_list.colors = [
            250,250,250,
            200,200,200,
            150,150,150,
            200,200,200
        ]

    def render_hover(self):
        self._vertex_list.colors = [
            220,220,220,
            170,170,170,
            120,120,120,
            170,170,170
        ]

    def render_click(self):
        self._vertex_list.colors = [
            20,20,20,
            70,70,70,
            120,120,120,
            70,70,70
        ]

class ButtonSlider(Button):
    def __init__(self, x, y, w, h, label, model, min, max):
        super().__init__(x, y, w, h, label, model, None)
        self.slider = SliderHandle(self._x+5, self._y+15, self._w-10, model)
        self.min = min
        self.max = max
        self.variable = label
        self._label.delete()
        self._label = pyglet.text.Label(
            label,
            font_name='Courier New',
            font_size=10,
            x=self._x+self._w/2, y=self._y+3*self._h/4,
            anchor_x='center', anchor_y='center',
            batch=model.get_render_batch(),
            color=(0,0,0,255),
            group=model.get_label_group()
        )

    def mouse_moved(self,mx,my):
        self.slider.mouse_moved(mx,my)

    def update(self):
        self.slider.mouse_pressed = self.mouse_pressed
        self.render_default()
        self.slider.update()

    def get_value(self):
        return self.min + (self.max - self.min) * self.slider.r / 100

    def on_click(self):
        pass
"""
class Graph():
    def __init__(self, x, y, w, h, model):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._variables = []
        self._colors = {}
        self._values = {}
        self._model = model
        self._ticks = 0

    def addVariable(self, label, r, g, b):
        self._variables.append(label)
        self._values[label] = []
        self._colors[label] = (r,g,b)

    def update(self):
        self._ticks += 1
        for v in self._variables:
            if v in self._model.globals:
                self._values[v].append(self._model.globals[v])

    def reset(self):
        self._ticks = 0
        for v in self._variables:
            self._values[v] = []

    def minimum(self):
        mn = None
        for var in self._variables:
            for val in self._values[var]:
                if mn == None or val < mn:
                    mn = val
        return mn

    def maximum(self):
        mx = None
        for var in self._variables:
            for val in self._values[var]:
                if mx == None or val > mx:
                    mx = val
        return mx

    def render(self):
        stroke(255,255,255)
        line(self._x, self._y, self._x, self._y+self._h)
        line(self._x, self._y+self._h, self._x+self._w, self._y+self._h)
        mn = self.minimum()
        mx = self.maximum()
        for var in self._variables:
            if len(self._values[var]) > 0:
                delta = self._w / len(self._values[var])
                fill(255,255,255)
                textAlign(CENTER,CENTER)
                text(str(mx),self._x-20,self._y-40,40,40)
                text(str(mn),self._x-20,self._y+self._h,40,40)
                diff = mx - mn
                if diff == 0:
                    diff = 0.5
                c = self._colors[var]
                stroke(c[0],c[1],c[2])
                for i in range(len(self._values[var][1:])):
                    line(self._x + delta*i,
                         self._y + self._h * (1 - (self._values[var][i] - mn) / diff),
                         self._x + delta*(i+1),
                         self._y + self._h * (1 - (self._values[var][i+1] - mn) / diff))
"""
AgentWindow = pyglet.window.Window(width=800,height=400)

def Start():
    pyglet.app.run()
