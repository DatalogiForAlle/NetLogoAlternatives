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
        self._initRender()

    def _initRender(self):
        rx = self._renderX()
        ry = self._renderY()
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
            self._resolution+1, pyglet.gl.GL_TRIANGLES, self._area.agentGroup,
            indices,
            ('v2f', vertices),
            ('c3B', colors)
        )

    def _wraparound(self):
        self.x = self.x % self._area.w
        self.y = self.y % self._area.h

    def jumpTo(self, x, y):
        self.x = x
        self.y = y
        self._wraparound()

    def get(self, var):
        return self._info[var]

    def set(self, var, val):
        self._info[var] = val

    def pointTo(self, other_x, other_y):
        dist = sqrt(((self.x-other_x)**2 + (self.y-other_y)**2)**0.5)
        self.direction = math.acos((self.x - other_x) / dist) * 360 / math.pi

    def move(self):
        self.x += math.cos(self.direction * 2 * math.pi / 360) * self.speed
        self.y += math.sin(self.direction * 2 * math.pi / 360) * self.speed
        self._wraparound()

    def distanceTo(self, other_x, other_y):
        return ((self.x-other_x)**2 + (self.y-other_y)**2)**0.5

    def currentTile(self):
        x = floor(len(self.model.tiles) * self.x / 400)
        y = floor(len(self.model.tiles) * self.y / 400)
        return (x,y)

    def isDestroyed(self):
        return self._destroyed

    def destroy(self):
        self._destroyed = True
        self._vertex_list.delete()

    def _renderX(self):
        return self._area.x + self.x

    def _renderY(self):
        return self._area.y + self.y

    def setColor(self, r, g, b):
        for i in range(len(self._vertex_list.colors)//3):
            self._vertex_list.colors[i*3] = r
            self._vertex_list.colors[i*3+1] = g
            self._vertex_list.colors[i*3+2] = b

    def render(self):
        x = self._renderX()
        y = self._renderY()
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
            4, pyglet.gl.GL_TRIANGLES, self._area.tileGroup,
            [0,1,2,0,2,3],
            ('v2f', [self.x,self.y,
                     self.x+self._w,self.y,
                     self.x+self._w,self.y+self._h,
                     self.x,self.y+self._h]),
            ('c3B', [255,0,0,
                     255,0,0,
                     255,0,0,
                     255,0,0])
        )

    def get(self, var):
        return self._info[var]

    def set(self, var, val):
        self._info[var] = val

    def render(self):
        pass

    def setColor(self, r, g, b):
        for i in range(4):
            self._vertex_list.colors[i*3] = r
            self._vertex_list.colors[i*3+1] = g
            self._vertex_list.colors[i*3+2] = b

class SimulationArea():
    def __init__(self, x, y, w, h, nAgents, nTiles, batch):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.nAgents = nAgents
        self.agents = set()
        self.nTiles = nTiles
        self.tiles = [[None for x in range(nTiles)] for y in range(nTiles)]
        self.batch = batch
        self.agentGroup = pyglet.graphics.OrderedGroup(2)
        self.tileGroup = pyglet.graphics.OrderedGroup(1)

    def reset(self):
        for a in self.agents:
            a.destroy()
        self.agents.clear()
        for i in range(self.nAgents):
            self.agents.add(Agent(random.randint(0,self.w),
                                  random.randint(0,self.h),
                                  self))
        tileW = self.w / self.nTiles
        tileH = self.h / self.nTiles
        for x in range(0,self.nTiles):
            for y in range(0,self.nTiles):
                self.tiles[x][y] = Tile(x*tileW,y*tileH,tileW,tileH,self)

    def render(self):
        for a in self.agents:
            a.render()
        self.batch.draw()

class Model():
    def __init__(self, nAgents, nTiles):
        global AgentWindow
        self._buttons = set()
        self._bgGroup = pyglet.graphics.OrderedGroup(0)
        self._buttonGroup = pyglet.graphics.OrderedGroup(3)
        self._labelGroup = pyglet.graphics.OrderedGroup(4)
        self._renderBatch = pyglet.graphics.Batch()
        self._area = SimulationArea(0,0,400,400,nAgents,nTiles,self._renderBatch)
        self._globals = {}
        win_size = AgentWindow.get_size()
        self._renderBatch.add_indexed(
            4, pyglet.gl.GL_TRIANGLES, self._bgGroup,
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
                b.mouseMoved(x,y)

        @AgentWindow.event
        def on_mouse_press(x, y, button, modifiers):
            if button == mouse.LEFT:
                for b in self._buttons:
                    b.mousePressed = True

        @AgentWindow.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            for b in self._buttons:
                b.mouseMoved(x,y)

        @AgentWindow.event
        def on_mouse_release(x, y, button, modifiers):
            if button == mouse.LEFT:
                for b in self._buttons:
                    b.mousePressed = False

    def get(self, var):
        return self._globals[var]

    def set(self, var, val):
        self._globals[var] = val

    def getAgents(self):
        return self._area.agents

    def getTile(self, x, y):
        return self._area.tiles[x][y]

    def getTileN(self):
        return self._area.nTiles

    def reset(self):
        self._area.reset()
        pass

    def plotVariable(self, label, r, g, b):
        pass
        #self._graph.addVariable(label, r, g, b)

    def update(self, dt):
        for b in self._buttons:
            b.update()
            if type(b) is ButtonToggle:
                if b.active:
                    b.func(self)

    def getRenderBatch(self):
        return self._renderBatch

    def getBackgroundGroup(self):
        return self._bgGroup

    def getButtonGroup(self):
        return self._buttonGroup

    def getLabelGroup(self):
        return self._labelGroup

    def render(self):
        self._renderBatch.draw()
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

    def addSingleButton(self, label, func):
        buttonCount = len(self._buttons)
        self._buttons.add(
            Button(
                440+(buttonCount%2)*160,
                16+math.floor(buttonCount/2)*76,
                140,56,label,self,func))

    def addToggleButton(self, label, func):
        buttonCount = len(self._buttons)
        self._buttons.add(
            ButtonToggle(
                440+(buttonCount%2)*160,
                16+math.floor(buttonCount/2)*76,
                140,56,label,self,func))

    def addSliderButton(self, label, min, max):
        buttonCount = len(self._buttons)
        button = ButtonSlider(440+(buttonCount%2)*160,
                              16+floor(buttonCount/2)*76,
                              140,56,label,min,max)
        button.model = self
        self._buttons.add(button)

class Button(object):
    def __init__(self, x, y, w, h, label, model, f):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self.label = label
        self.func = f
        self.state = 0 # 0=default | 1=mouse_hovering | 2=mouse_clicking
        self.counter = 0
        self.model = model
        self.mouseHover = False
        self.mousePressed = False
        self.vertex_list = model.getRenderBatch().add_indexed(
            4, pyglet.gl.GL_TRIANGLES, model.getButtonGroup(),
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
        pyglet.text.Label(label,
                          font_name='Courier New',
                          font_size=12,
                          x=self._x+self._w/2, y=self._y+self._h/2,
                          anchor_x='center', anchor_y='center',
                          batch=model.getRenderBatch(),
                          color=(0,0,0,255),
                          group=model.getLabelGroup())

    def update(self):
        if self.state == 0 and self.mouseHover:
            self.state = 1
            self.renderHover()
        elif self.state == 1 and self.mouseHover:
            if self.mousePressed:
                self.state = 2
                self.renderClick()
            else:
                self.renderHover()
        elif self.state == 2 and self.mouseHover:
            if self.mousePressed:
                self.renderClick()
            else:
                self.state = 0
                self.onClick()
                self.renderHover()
        else:
            self.state = 0
            self.renderDefault()

    def renderDefault(self):
        self.vertex_list.colors = [150, 150, 150,
                                   100, 100, 100,
                                   150, 150, 150,
                                   200, 200, 200]

    def renderHover(self):
        self.vertex_list.colors = [150, 150, 150,
                                   200, 200, 200,
                                   150, 150, 150,
                                   100, 100, 100]

    def renderClick(self):
        self.vertex_list.colors = [100, 100, 100,
                                   150, 150, 150,
                                   100, 100, 100,
                                   50, 50, 50]

    def mouseMoved(self,mx,my):
        self.mouseHover = ((self._x < mx)
                           and (mx < self._x + self._w)
                           and (self._y < my)
                           and (my < self._y + self._h))

    def onClick(self):
        self.func(self.model)

class ButtonToggle(Button):
    def __init__(self, x, y, w, h, label, model, f):
        super().__init__(x, y, w, h, label, model, f)
        self.active=False
        self._led_vertex_list = model.getRenderBatch().add_indexed(
            5, pyglet.gl.GL_TRIANGLES, model.getLabelGroup(),
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
        if self.state == 0 and self.mouseHover:
            self.state = 1
            self.renderHover()
        elif self.state == 1 and self.mouseHover:
            if self.mousePressed:
                self.state = 2
                self.renderClick()
            else:
                self.renderHover()
        elif self.state == 2 and self.mouseHover:
            if self.mousePressed:
                self.renderClick()
            else:
                self.state = 0
                self.onClick()
                self.renderHover()
        else:
            self.state = 0
            self.renderDefault()
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

    def onClick(self):
        self.active = not self.active

class SliderHandle(Button):
    def __init__(self, x, y, w):
        self.x = x
        self.y = y
        self.h = 18
        self.w = 6
        self.sliderW = w
        self.r = 50
        self.state = 0 # 0=default | 1=mouse_hovering | 2=mouse_clicking
        rect(self.x+(self.sliderW*self.r/100)-self.w/2,self.y-self.h/2,self.w,self.h)
        self._vertex_list = model.getRenderBatch().add_indexed(
            4, pyglet.gl.GL_TRIANGLES, model.getButtonGroup(),
            [0, 1, 2, 0, 2, 3],
            ('v2i', (self.x+(self.sliderW*self.r/100)-self.w/2, self.y+self.h/2,
                     self.x+(self.sliderW*self.r/100)+self.w/2, self.y+self.h/2,
                     self.x+(self.sliderW*self.r/100)+self.w/2, self.y-self.h/2,
                     self.x+(self.sliderW*self.r/100)-self.w/2, self.y-self.h/2)),
            ('c3B', (150, 150, 150,
                     150, 150, 150,
                     150, 150, 150,
                     150, 150, 150))
        )

    def mouseMoved(self,mx,my):
        self.mouseHover = (self.x+(self.sliderW*self.r/100)-self.w/2 < mx) and (mx < self.x+(self.sliderW*self.r/100) + self.w/2) and (self.y-self.h/2 < my) and (my < self.y + self.h/2)
        if mx < self.x:
            self.r = 0
        elif mx > self.x + self.sliderW:
            self.r = 100
        else:
            self.r = (mx - self.x) * 100 / self.sliderW
        self._vertex_list.vertices = [
            self.x+(self.sliderW*self.r/100)-self.w/2, self.y+self.h/2,
            self.x+(self.sliderW*self.r/100)+self.w/2, self.y+self.h/2,
            self.x+(self.sliderW*self.r/100)+self.w/2, self.y-self.h/2,
            self.x+(self.sliderW*self.r/100)-self.w/2, self.y-self.h/2
        ]

    def update(self):
        if self.state == 0 and self.mouseHover:
            self.state = 1
            self.renderHover()
        elif self.state == 1 and self.mouseHover:
            if mousePressed:
                self.state = 2
                self.followMouse()
                self.renderClick()
            else:
                self.renderHover()
        elif self.state == 2:
            if mousePressed:
                self.followMouse()
                self.renderClick()
            else:
                self.state = 0
                self.renderHover()
        else:
            self.state = 0
            self.renderDefault()

    def renderDefault(self):
        self._vertex_list.colors = [
            150,150,150,
            150,150,150,
            150,150,150,
            150,150,150
        ]

    def renderHover(self):
        self._vertex_list.colors = [
            100,100,100,
            100,100,100,
            100,100,100,
            100,100,100
        ]

    def renderClick(self):
        self._vertex_list.colors = [
            50,50,50,
            50,50,50,
            50,50,50,
            50,50,50
        ]
"""
class ButtonSlider(Button):
    def __init__(self, x, y, w, h, label, min, max):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.slider = SliderHandle(self.x+5, self.y+self.h-15, self.w-10)
        self.label = label
        self.min = min
        self.max = max

    def render(self):
        self.renderDefault()
        self.slider.render()

    def renderDefault(self):
        fill(200,200,200)
        rect(self.x,self.y,self.w,self.h)
        fill(0, 0, 0)
        textAlign(CENTER,TOP)
        text(self.label,self.x,self.y+5,self.w,self.h)
        textAlign(LEFT,TOP)
        text(str(self.min),self.x+10,self.y+15,self.w,self.h)
        textAlign(RIGHT,TOP)
        text(str(self.max),self.x-10,self.y+15,self.w,self.h)

    def getValue(self):
        return self.min + (self.max - self.min) * self.slider.r / 100

    def onClick(self):
        self.active = not self.active
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

AgentWindow = pyglet.window.Window(width=800,height=400)

def Start():
    pyglet.app.run()
