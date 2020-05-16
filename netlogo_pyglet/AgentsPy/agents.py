import pyglet.graphics
import random
import math
from pyglet.window import mouse

def RNG(maximum):
    return random.randint(0,maximum)

class Agent(dict):
    def __init__(self):
        # Associated simulation area.
        self.__area = None

        # Destroyed agents are not drawn and are removed from their area.
        self.__destroyed = False

        # Number of edges in the regular polygon representing the agent.
        self.__resolution = 10

        # Color of the agent in RGB.
        self.__color = [RNG(255),RNG(255),RNG(255)]

        self.x = 0
        self.y = 0
        self.size = 1
        self.direction = random.randint(0,359)
        self.speed = 1

    def __render_x(self):
        return self.__area.x + self.x

    def __render_y(self):
        return self.__area.y + self.y

    # Ensures that the agent stays inside the simulation area.
    def __wraparound(self):
        self.x = self.x % self.__area.w
        self.y = self.y % self.__area.h

    # Sets up the internal vertex list used for drawing
    # (part of the pyglet library).
    def init_render(self):
        rx = self.__render_x()
        ry = self.__render_y()
        vertices = [rx,ry]
        indices = []
        for i in range(self.__resolution):
            a = i * (2 * math.pi) / self.__resolution
            vertices.append(rx + math.cos(a) * self.size)
            vertices.append(ry + math.sin(a) * self.size)
            if i < (self.__resolution-1):
                indices.extend([0, i+1, i+2])
            else:
                indices.extend([0, i+1, 1])
        self.__vertex_list = self.__area.batch.add_indexed(
            self.__resolution+1, pyglet.gl.GL_TRIANGLES, self.__area.agent_group,
            indices,
            ('v2f', vertices),
            ('c3B', self.__color * (self.__resolution+1))
        )

    def render(self):
        x = self.__render_x()
        y = self.__render_y()
        vertices = [x,y]
        for i in range(self.__resolution):
            a = i * (2 * math.pi) / self.__resolution
            vertices.append(x + math.cos(a) * self.size)
            vertices.append(y + math.sin(a) * self.size)
        self.__vertex_list.vertices = vertices
        self.__vertex_list.colors = self.__color * (self.__resolution+1)

    def jump_to(self, x, y):
        self.x = x
        self.y = y
        self.__wraparound()

    def set_area(self, area):
        self.__area = area

    def point_towards(self, other_x, other_y):
        dist = self.distance_to(other_x,other_y)
        if dist > 0:
            self.direction = math.degrees(math.acos((other_x - self.x) / dist))
            if (self.y - other_y) > 0:
                self.direction = 360 - self.direction

    def forward(self):
        self.x += math.cos(math.radians(self.direction)) * self.speed
        self.y += math.sin(math.radians(self.direction)) * self.speed
        self.__wraparound()

    def distance_to(self, other_x, other_y):
        return ((self.x-other_x)**2 + (self.y-other_y)**2)**0.5

    def agents_nearby(self, distance, agent_type=None):
        nearby = set()
        for a in self.__area.agents:
            if self.distance_to(a.x,a.y) <= distance:
                if type == None or type(a) is agent_type:
                    nearby.add(a)
        return nearby

    def current_tile(self):
        x = floor(len(self.model.tiles) * self.x / self.__area.w)
        y = floor(len(self.model.tiles) * self.y / self.__area.h)
        return self.__area.tiles[x][y]

    def is_destroyed(self):
        return self.__destroyed

    def destroy(self):
        if not self.__destroyed:
            self.__destroyed = True
            self.__vertex_list.delete()

    def set_color(self, r, g, b):
        self.__color = [r,g,b]

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
    def __init__(self, x, y, w, h, x_tiles, y_tiles, batch):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.agents = set()
        self.x_tiles = x_tiles
        self.y_tiles = y_tiles
        self.tiles = [[None for x in range(x_tiles)] for y in range(y_tiles)]
        self.batch = batch
        self.agent_group = pyglet.graphics.OrderedGroup(2)
        self.tile_group = pyglet.graphics.OrderedGroup(1)

    def add_agent(self, agent):
        agent.set_area(self)
        agent.x = RNG(self.w)
        agent.y = RNG(self.h)
        agent.init_render()
        self.agents.add(agent)

    def add_agents(self, agents):
        for a in agents:
            self.add_agent(a)

    def reset(self):
        for a in self.agents:
            a.destroy()
        self.agents.clear()
        tile_w = self.w / self.x_tiles
        tile_h = self.h / self.y_tiles
        for y in range(0,self.y_tiles):
            for x in range(0,self.x_tiles):
                self.tiles[y][x] = Tile(self.x+x*tile_w,
                                        self.y+y*tile_h,
                                        tile_w,tile_h,self)

    def render(self):
        for a in self.agents:
            a.render()
        self.batch.draw()

class Model(dict):
    def __init__(self, width, height, x_tiles, y_tiles):
        global AgentWindow
        self._buttons = set()
        self._bg_group = pyglet.graphics.OrderedGroup(0)
        self._button_group = pyglet.graphics.OrderedGroup(3)
        self._label_group = pyglet.graphics.OrderedGroup(4)
        self._render_batch = pyglet.graphics.Batch()
        self.__area = SimulationArea(0,100,width,height,x_tiles,y_tiles,self._render_batch)
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
        self._graph = Graph(440,248,300,132,self)
        self.reset()
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

    def add_agent(self, agent):
        self.__area.add_agent(agent)

    def add_agents(self, agents):
        self.__area.add_agents(agents)

    def get_agents(self):
        return self.__area.agents

    def get_tile(self, x, y):
        return self.__area.tiles[x][y]

    def get_tile_n(self):
        return self.__area.n_tiles

    def get_all_tiles(self):
        tileset = set()
        for y in range(self.__area.y_tiles):
            for x in range(self.__area.x_tiles):
                tileset.add(self.__area.tiles[y][x])
        return tileset

    def reset(self):
        self.__area.reset()
        self._graph.reset()

    def plot_variable(self, label, r, g, b):
        self._graph.add_variable(label, r, g, b)

    def update_plot(self):
        pass
        #self.__update_graph_flag = True

    def update(self, dt):
        for b in self._buttons:
            b.update()
            if type(b) is ButtonToggle:
                if b.active:
                    b.func(self)
            if type(b) is ButtonSlider:
                self[b.variable] = b.get_value()
        self._graph.update()

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
        for a in self.__area.agents:
            a.render()
        self._graph.render()

    def add_single_button(self, label, func):
        button_count = len(self._buttons)
        self._buttons.add(
            Button(
                440+(button_count%2)*180,
                16+math.floor(button_count/2)*76,
                140,56,label,self,func))

    def add_toggle_button(self, label, func):
        button_count = len(self._buttons)
        self._buttons.add(
            ButtonToggle(
                440+(button_count%2)*180,
                16+math.floor(button_count/2)*76,
                140,56,label,self,func))

    def add_slider_button(self, label, min, max):
        button_count = len(self._buttons)
        self._buttons.add(
            ButtonSlider(
                440+(button_count%2)*180,
                16+math.floor(button_count/2)*76,
                140,56,label,self,min,max))

class Button():
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
            [0,1,2,0,2,3,0,3,4,0,4,1],
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
            4, pyglet.gl.GL_TRIANGLES, model.get_label_group(),
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
        pyglet.text.Label(
            str(self.min),
            font_name='Courier New',
            font_size=8,
            x=self._x+10, y=self._y+3*self._h/4-5,
            anchor_x='center', anchor_y='center',
            batch=model.get_render_batch(),
            color=(0,0,0,255),
            group=model.get_label_group()
        )
        pyglet.text.Label(
            str(self.max),
            font_name='Courier New',
            font_size=8,
            x=self._x+self._w-10, y=self._y+3*self._h/4-5,
            anchor_x='center', anchor_y='center',
            batch=model.get_render_batch(),
            color=(0,0,0,255),
            group=model.get_label_group()
        )
        model.get_render_batch().add_indexed(
            2, pyglet.gl.GL_LINES, model.get_button_group(),
            [0,1],
            ('v2f', [self._x+5, self._y+15,
                     self._x+self._w-5, self._y+15]),
            ('c3B', (255,255,255,
                     255,255,255))
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

class Graph():
    def __init__(self, x, y, w, h, model):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._variables = []
        self._colors = {}
        self._values = {}
        self._vertex_lists = {}
        self._model = model
        self._ticks = 0
        self._batch = pyglet.graphics.Batch()

        self._batch.add_indexed(
            4, pyglet.gl.GL_TRIANGLES, self._model.get_button_group(),
            [0,1,2,0,2,3],
            ('v2f', (self._x,self._y,
                     self._x+self._w, self._y,
                     self._x+self._w, self._y+self._h,
                     self._x,self._y+self._h)),
            ('c3B', (0,0,0,
                     0,0,0,
                     0,0,0,
                     0,0,0))
        )
        self._batch.add_indexed(
            3, pyglet.gl.GL_LINES, self._model.get_label_group(),
            [0,1,1,2],
            ('v2f', [self._x+5, self._y+self._h-5,
                     self._x+5, self._y+5,
                     self._x+self._w-5, self._y+5]),
            ('c3B', (255,255,255,
                     255,255,255,
                     255,255,255))
        )

    def add_variable(self, label, r, g, b):
        self._variables.append(label)
        self._values[label] = []
        self._colors[label] = (r,g,b)
        self._vertex_lists[label] = self._batch.add_indexed(
            1, pyglet.gl.GL_LINE_STRIP, self._model.get_label_group(),
            [0],
            ('v2f', [0,0]),
            ('c3B', [0,0,0]))

    def update(self):
        mn = self.minimum()
        mx = self.maximum()
        self._ticks += 1
        for var in self._variables:
            if var in self._model:
                self._values[var].append(self._model.get(var))
                if len(self._values[var]) > 1:
                    delta = (self._w-10) / (len(self._values[var])-1)
                    diff = mx - mn
                    if diff == 0:
                        diff = 0.5
                    c = self._colors[var]
                    vertices=[
                        self._x+5, self._y+5 + (self._h-10) * (self._values[var][0] - mn) / diff
                    ]
                    indices=[0]
                    colors=[c[0],c[1],c[2]]
                    for i in range(len(self._values[var][1:])):
                        vertices.extend(
                            [self._x+5 + delta*(i+1),
                             self._y+5 + (self._h-10) * (self._values[var][i+1] - mn) / diff])
                        colors.extend([c[0],c[1],c[2]])
                        indices.extend([i+1])
                    self._vertex_lists[var].resize(len(vertices)//2,len(indices))
                    self._vertex_lists[var].vertices = vertices
                    self._vertex_lists[var].indices = indices
                    self._vertex_lists[var].colors = colors

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
        self._batch.draw()

AgentWindow = pyglet.window.Window(width=800,height=400)

def Start():
    pyglet.app.run()
