import random

class Agent():
    def __init__(self, x, y, model):
        self.model = model
        self.info = {}
        self.x = x
        self.y = y
        self.direction = random.randint(0,359)
        self.speed = 1

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

class Model():
    def __init__(self, N, initf, rf):
        self.width = 400
        self.height = 400
        self.maxcount = N
        self.agents = set()
        self.__buttons = set()
        self.initFunc = initf
        self.renderFunc = rf
        self.globals = {}
        self.__paused = False
        self.addSingleButton("setup",self.reset)
    
    def reset(self, model):
        self.agents.clear()
        for i in range(self.maxcount):
            a = Agent(random.randint(0,self.width),
                      random.randint(0,self.height),
                      self)
            self.agents.add(a)
        self.initFunc(self)
        

    def render(self):
        background(0,0,0)
        self.renderFunc(self.agents)
        for b in self.__buttons:
            b.render()
            if type(b) is ButtonToggle:
                if b.active:
                    b.func(self)

    def apply(self, f):
        print("hej8")
        if not self.__paused:
            print("hej40")
            f(self)
    
    def addSingleButton(self, label, func):
        buttonCount = len(self.__buttons)
        button = Button(440+(buttonCount%2)*160,
                        16+floor(buttonCount/2)*76,
                        140,56,label,func)
        button.model = self
        self.__buttons.add(button)
    
    def addToggleButton(self, label, func):
        buttonCount = len(self.__buttons)
        button = ButtonToggle(440+(buttonCount%2)*160,
                              16+floor(buttonCount/2)*76,
                              140,56,label,func)
        button.model = self
        self.__buttons.add(button)
    
    def addSliderButton(self):
        buttonCount = len(self.__buttons)
        button = SliderHandle(500,300,100)
        button.model = self
        self.__buttons.add(button)

class Button(object):
    def __init__(self, x, y, w, h, label, f):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.pressed = False
        self.func = f
        self.state = 0 # 0=default | 1=mouse_hovering | 2=mouse_clicking
        self.counter = 0
        self.model = None
    
    def mouseHovering(self):
        return (self.x < mouseX) and (mouseX < self.x + self.w) and (self.y < mouseY) and (mouseY < self.y + self.h)
    
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
    
    def renderDefault(self):
        fill(200,200,200)
        rect(self.x,self.y,self.w,self.h)
        fill(0, 0, 0)
        textAlign(CENTER,CENTER)
        text(self.label,self.x,self.y,self.w,self.h)
    
    def renderHover(self):
        fill(150,150,150)
        rect(self.x,self.y,self.w,self.h)
        fill(0, 0, 0)
        textAlign(CENTER,CENTER)
        text(self.label,self.x,self.y,self.w,self.h)
    
    def renderClick(self):
        fill(100,100,100)
        rect(self.x,self.y,self.w,self.h)
        fill(0, 0, 0)
        textAlign(CENTER,CENTER)
        text(self.label,self.x,self.y,self.w,self.h)
    
    def onClick(self):
        self.func(self.model)

class ButtonToggle(Button):
    def __init__(self, x, y, w, h, label, f):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
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
        self.h = 20
        self.w = 10
        self.sliderW = w
        self.r = 50
        self.state = 0 # 0=default | 1=mouse_hovering | 2=mouse_clicking
    
    def mouseHovering(self):
        return (self.x+(self.sliderW*self.r/100)-self.w/2 < mouseX) and (mouseX < self.x+(self.sliderW*self.r/100) + self.w/2) and (self.y < mouseY) and (mouseY < self.y + self.h)

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
