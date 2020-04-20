import pyglet.graphics
import random
import math
from pyglet.window import mouse

class Agent():
    def __init__(self, x, y, model):
        self.model = model
        self.info = {}
        self.__x = x
        self.__y = y
        self.size = 100
        self.direction = random.randint(0,359)
        self.speed = 1
        self.__destroyed = False
        self.__resolution = 5
        vertices = [self.__x,self.__y]
        colors = [255,255,255]
        indices = []
        for i in range(self.__resolution):
            a = i * (2 * math.pi) / self.__resolution
            vertices.append(self.__x + math.cos(a) * self.size)
            vertices.append(self.__y + math.sin(a) * self.size)
            colors.extend([255, 255, 255])
            if i < (self.__resolution-1):
                indices.extend([0, i+1, i+2])
            else:
                indices.extend([0, i+1, 1])
        self.__vertex_list = self.model.batch.add_indexed(
            self.__resolution+1, pyglet.gl.GL_TRIANGLES, self.model.getForeground(),
            indices,
            ('v2f', vertices),
            ('c3B', colors)
        )

    def wraparound(self):
        self.x = self.x % self.model.width
        self.y = self.y % self.model.height

    def jumpTo(self, x, y):
        self.x = x
        self.y = y
        self.wraparound()

    def pointTo(self, other_x, other_y):
        dist = sqrt(((self.x-other_x)**2 + (self.y-other_y)**2)**0.5)
        self.direction = math.acos((self.x - other_x) / dist) * 360 / math.pi

    def move(self):
        self.x += cos(self.direction * 2 * PI / 360) * self.speed
        self.y += sin(self.direction * 2 * PI / 360) * self.speed
        self.wraparound()

    def distanceTo(self, other_x, other_y):
        return ((self.x-other_x)**2 + (self.y-other_y)**2)**0.5

    def currentTile(self):
        x = floor(len(self.model.tiles) * self.x / 400)
        y = floor(len(self.model.tiles) * self.y / 400)
        return (x,y)

    def isDestroyed(self):
        return self.__destroyed

    def destroy(self):
        self.__destroyed = True

    def render(self):
        self.__vertex_list.vertices = [
            self.__x,self.__y,
            self.__x,self.__y+self.size,
            self.__x+self.size*0.75,self.__y+self.size*0.75,
            self.__x+self.size,self.__y,
            self.__x+self.size*0.75,self.__y-self.size*0.75,
            self.__x,self.__y-self.size,
            self.__x-self.size*0.75,self.__y-self.size*0.75,
            self.__x-self.size,self.__y,
            self.__x-self.size*0.75,self.__y+self.size*0.75
        ]

class Tile():
    def __init__(self,x,y,w,h,model):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.model = model
        self.info = {}
        self.color = (0,0,0)

    def render(self):
        pass
        #fill(self.color[0],self.color[1],self.color[2])
        #rect(self.x,self.y,self.w,self.h)

    def setColor(self, r, g, b):
        self.color = (r, g, b)

class Model():
    def __init__(self, N, nTiles, initf, rf):
        self.batch = pyglet.graphics.Batch()
        self.__buttons = set()
        self.__backgroundGroup = pyglet.graphics.OrderedGroup(0)
        self.__foregroundGroup = pyglet.graphics.OrderedGroup(1)
        self.__labelGroup = pyglet.graphics.OrderedGroup(2)
        self.zepto = Agent(400,200,self)
        """
        self.width = 400
        self.height = 400
        self.__initcount = N
        self.agents = set()
        self.tiles = [[None for x in range(nTiles)] for y in range(nTiles)]
        tileSize = 400 / nTiles
        for x in range(0,nTiles):
            for y in range(0,nTiles):
                self.tiles[x][y] = Tile(x*tileSize,y*tileSize,tileSize,tileSize,self)
                self.tiles[x][y].setColor(0,0,0)
        self.__buttons = set()
        self.__initFunc = initf
        self.__renderFunc = rf
        self.globals = {}
        self.__paused = False
        self.addSingleButton("setup",self.reset)
        self.__graph = Graph(450,200,300,150,self)
        """

        pyglet.clock.schedule_interval(self.update, 0.02)

        @window.event
        def on_mouse_motion(x, y, dx, dy):
            for b in self.__buttons:
                b.mouseMoved(x,y)

        @window.event
        def on_mouse_press(x, y, button, modifiers):
            if button == mouse.LEFT:
                for b in self.__buttons:
                    b.mousePressed = True

        @window.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            for b in self.__buttons:
                b.mouseMoved(x,y)

        @window.event
        def on_mouse_release(x, y, button, modifiers):
            if button == mouse.LEFT:
                for b in self.__buttons:
                    b.mousePressed = False

    def reset(self, model):
        pass
        """
        self.agents.clear()
        for i in range(self.__initcount):
            a = Agent(random.randint(0,self.width),
                      random.randint(0,self.height),
                      self)
            self.agents.add(a)
        self.__initFunc(self)
        self.__graph.reset()
        """

    def tick(self):
        pass
        #self.__graph.update()

    def plotVariable(self, label, r, g, b):
        pass
        #self.__graph.addVariable(label, r, g, b)

    def update(self, dt):
        for b in self.__buttons:
            b.update()

    def getBackground(self):
        return self.__backgroundGroup

    def getForeground(self):
        return self.__foregroundGroup

    def getLabelGroup(self):
        return self.__labelGroup

    def render(self):
        self.batch.draw()
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
        self.__renderFunc(self.agents)
        for b in self.__buttons:
            b.render()
            if type(b) is ButtonToggle:
                if b.active:
                    b.func(self)
            if type(b) is ButtonSlider:
                self.globals[b.label] = b.getValue()
        self.__graph.render()
        """

    def addSingleButton(self, label, func):
        buttonCount = len(self.__buttons)
        self.__buttons.add(
            Button(
                16+(buttonCount%2)*160,
                16+math.floor(buttonCount/2)*76,
                150,80,label,self,None))
        """
        buttonCount = len(self.__buttons)
        button = Button(440+(buttonCount%2)*160,
                        16+floor(buttonCount/2)*76,
                        140,56,label,func)
        button.model = self
        self.__buttons.add(button)
        """

    def addToggleButton(self, label, func):
        buttonCount = len(self.__buttons)
        button = ButtonToggle(440+(buttonCount%2)*160,
                              16+floor(buttonCount/2)*76,
                              140,56,label,func)
        button.model = self
        self.__buttons.add(button)

    def addSliderButton(self, label, min, max):
        buttonCount = len(self.__buttons)
        button = ButtonSlider(440+(buttonCount%2)*160,
                              16+floor(buttonCount/2)*76,
                              140,56,label,min,max)
        button.model = self
        self.__buttons.add(button)

class Button(object):
    def __init__(self, x, y, w, h, label, model, f):
        self.__x = x
        self.__y = y
        self.__w = w
        self.__h = h
        self.label = label
        self.func = f
        self.state = 0 # 0=default | 1=mouse_hovering | 2=mouse_clicking
        self.counter = 0
        self.model = model
        self.mouseHover = False
        self.mousePressed = False
        self.vertex_list = self.model.batch.add_indexed(
            4, pyglet.gl.GL_TRIANGLES, self.model.getForeground(),
            [0, 1, 2, 0, 2, 3],
            ('v2i', (self.__x, self.__y,
                     self.__x+self.__w, self.__y,
                     self.__x+self.__w, self.__y+self.__h,
                     self.__x, self.__y+self.__h)),
            ('c3B', (150, 150, 150,
                     100, 100, 100,
                     150, 150, 150,
                     200, 200, 200))
        )
        pyglet.text.Label(label,
                          font_name='Courier New',
                          font_size=12,
                          x=self.__x+self.__w/2, y=self.__y+self.__h/2,
                          anchor_x='center', anchor_y='center',
                          batch=model.batch,
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
        self.mouseHover = ((self.__x < mx)
                           and (mx < self.__x + self.__w)
                           and (self.__y < my)
                           and (my < self.__y + self.__h))

    def onClick(self):
        print(self.label)
        #self.func(self.model)

class ButtonToggle(Button):
    def __init__(self, x, y, w, h, label, f):
        self.label = label
        self.pressed = False
        self.func = f
        self.state = 0 # 0=default | 1=mouse_hovering | 2=mouse_clicking
        self.counter = 0
        self.model = None
        self.active=False

    def render(self):
        if self.state == 0 and self.mouseHovering():
            self.state = 1
            self.renderHover()
        elif self.state == 1 and self.mouseHovering():
            if mousePressed:
                self.state = 2
                self.onClick()
                self.renderClick()
            else:
                self.renderHover()
        elif self.state == 2 and self.mouseHovering():
            if mousePressed:
                self.renderClick()
            else:
                self.state = 0
                self.renderHover()
        else:
            self.state = 0
            self.renderDefault()
        if self.active:
            fill(50,255,50)
        else:
            fill(40,40,40)
        ellipse(self.x+self.w-10,self.y+10,10,10)

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

    def mouseHovering(self):
        return (self.x+(self.sliderW*self.r/100)-self.w/2 < mouseX) and (mouseX < self.x+(self.sliderW*self.r/100) + self.w/2) and (self.y-self.h/2 < mouseY) and (mouseY < self.y + self.h/2)

    def render(self):
        fill(255,255,255)
        rect(self.x,self.y,self.sliderW,3)
        if self.state == 0 and self.mouseHovering():
            self.state = 1
            self.renderHover()
        elif self.state == 1 and self.mouseHovering():
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
        fill(200,200,200)
        rect(self.x+(self.sliderW*self.r/100)-self.w/2,self.y-self.h/2,self.w,self.h)

    def renderHover(self):
        fill(150,150,150)
        rect(self.x+(self.sliderW*self.r/100)-self.w/2,self.y-self.h/2,self.w,self.h)

    def renderClick(self):
        fill(100,100,100)
        rect(self.x+(self.sliderW*self.r/100)-self.w/2,self.y-self.h/2,self.w,self.h)

    def followMouse(self):
        if mouseX < self.x:
            self.r = 0
        elif mouseX > self.x + self.sliderW:
            self.r = 100
        else:
            self.r = (mouseX - self.x) * 100 / self.sliderW

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

class Graph():
    def __init__(self, x, y, w, h, model):
        self.__x = x
        self.__y = y
        self.__w = w
        self.__h = h
        self.__variables = []
        self.__colors = {}
        self.__values = {}
        self.__model = model
        self.__ticks = 0

    def addVariable(self, label, r, g, b):
        self.__variables.append(label)
        self.__values[label] = []
        self.__colors[label] = (r,g,b)

    def update(self):
        self.__ticks += 1
        for v in self.__variables:
            if v in self.__model.globals:
                self.__values[v].append(self.__model.globals[v])

    def reset(self):
        self.__ticks = 0
        for v in self.__variables:
            self.__values[v] = []

    def minimum(self):
        mn = None
        for var in self.__variables:
            for val in self.__values[var]:
                if mn == None or val < mn:
                    mn = val
        return mn

    def maximum(self):
        mx = None
        for var in self.__variables:
            for val in self.__values[var]:
                if mx == None or val > mx:
                    mx = val
        return mx

    def render(self):
        stroke(255,255,255)
        line(self.__x, self.__y, self.__x, self.__y+self.__h)
        line(self.__x, self.__y+self.__h, self.__x+self.__w, self.__y+self.__h)
        mn = self.minimum()
        mx = self.maximum()
        for var in self.__variables:
            if len(self.__values[var]) > 0:
                delta = self.__w / len(self.__values[var])
                fill(255,255,255)
                textAlign(CENTER,CENTER)
                text(str(mx),self.__x-20,self.__y-40,40,40)
                text(str(mn),self.__x-20,self.__y+self.__h,40,40)
                diff = mx - mn
                if diff == 0:
                    diff = 0.5
                c = self.__colors[var]
                stroke(c[0],c[1],c[2])
                for i in range(len(self.__values[var][1:])):
                    line(self.__x + delta*i,
                         self.__y + self.__h * (1 - (self.__values[var][i] - mn) / diff),
                         self.__x + delta*(i+1),
                         self.__y + self.__h * (1 - (self.__values[var][i+1] - mn) / diff))

window = pyglet.window.Window(width=800,height=400)
modello = Model(100, 50, None, None)
modello.addSingleButton("hej", None)
modello.addSingleButton("hej2", None)
modello.addSingleButton("hej3", None)

@window.event
def on_draw():
    window.clear()
    modello.render()

def testo():
    pyglet.app.run()
