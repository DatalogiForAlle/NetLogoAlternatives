import random
import Agents as ag

def EpidemicRenderer(agents):
    for a in agents:
        if (a.info["infection"] > 0):
            fill(255, 255, 0)
        elif a.info["immune"]:
            fill(50,50,255)
        else:
            fill(0, 175, 0)
        ellipse(a.x, a.y, 10, 10)

def infect(model):
    for a in model.agents:
        a.speed = 0.2
        a.info["immune"] = False
        a.info["infection"] = 0
        if (random.randint(0,100) < 5):
            a.info["infection"] = 1000 
    
def action(model):
    for a in model.agents:
        a.direction += random.randint(0,20)-10
        a.move()
        if (a.info["infection"] > 1):
            for b in model.agents:
                if (a.distanceTo(b.x,b.y) < 15) and (not b.info["immune"]) and (b.info["infection"] == 0):
                    b.info["infection"] = 1000
            a.info["infection"] -= 1
        elif a.info["infection"] == 1:
            a.info["infection"] = 0
            a.info["immune"] = True

modello = ag.Model(100, infect, EpidemicRenderer)
modello.addToggleButton("go",action)
modello.addSliderButton()

def setup():
    global modello
    size(800,400)
    print("hej2")
    
def draw():
    global modello
    modello.render()
