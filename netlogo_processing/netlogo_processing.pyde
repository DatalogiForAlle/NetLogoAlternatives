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

def infectPath(model):
    for a in model.agents:
        (x,y) = a.currentTile()
        if a.info["infection"] > 0:
            model.tiles[x][y].info["infection"] = 200
        elif not a.info["immune"] and model.tiles[x][y].info["infection"] > 0:
            a.info["infection"] = 100
            model.globals["infected"] += 1
    for x in range(20):
        for y in range(20):
            if model.tiles[x][y].info["infection"] > 0:
                model.tiles[x][y].setColor(150,150,0)
                model.tiles[x][y].info["infection"] -= 1
            else:
                model.tiles[x][y].setColor(0,50,0)

def infect(model):
    model.globals["movespeed"] = 0.2
    model.globals["infected"] = 0
    model.globals["immune"] = 0
    for a in model.agents:
        a.info["immune"] = False
        a.info["infection"] = 0
        if (random.randint(0,100) < 5):
            a.info["infection"] = 1000
            model.globals["infected"] += 1
    for x in range(20):
        for y in range(20):
            model.tiles[x][y].setColor(0,50,0)
            model.tiles[x][y].info["infection"] = 0
    
def action(model):
    for a in model.agents:
        a.direction += random.randint(0,20)-10
        a.speed = model.globals["movespeed"]
        a.move()
        if (a.info["infection"] > 1):
            for b in model.agents:
                if (a.distanceTo(b.x,b.y) < 15) and (not b.info["immune"]) and (b.info["infection"] == 0):
                    b.info["infection"] = 1000
                    model.globals["infected"] += 1
            a.info["infection"] -= 1
        elif a.info["infection"] == 1:
            a.info["infection"] = 0
            model.globals["infected"] -= 1
            model.globals["immune"] += 1
            a.info["immune"] = True
    infectPath(model)
    model.tick()

def printValue(model):
    print(model.globals["movespeed"])

modello = ag.Model(100, 20, infect, EpidemicRenderer)
modello.addToggleButton("go",action)
modello.addSliderButton("movespeed", 0.0, 1.0)
modello.plotVariable("infected",255,255,0)
modello.plotVariable("immune",100,100,255)

def setup():
    global modello
    size(800,400)
    
def draw():
    global modello
    modello.render()
