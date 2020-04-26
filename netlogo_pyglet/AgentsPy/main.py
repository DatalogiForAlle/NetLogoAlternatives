#!/usr/bin/env python3
import Agents as ag
import math

def action(model):
    for a in model.getAgents():
        a.direction += ag.RNG(20)-10
        a.speed = model.get("movespeed")
        a.move()
        if (a.get("infection") > 1):
            for b in model.getAgents():
                if (a.distanceTo(b.x,b.y) < 15) and (not b.get("immune")) and (b.get("infection") == 0):
                    b.set("infection",1000)
                    model.set("infected", model.get("infected")+1)
            a.set("infection",a.get("infection")-1)
        elif a.get("infection") == 1:
            a.set("infection",0)
            model.set("infected",model.get("infected")+1)
            model.set("immune",model.get("infected")+1)
            a.set("immune",True)
        if (a.get("infection") > 0):
            a.setColor(200,200,0)
        elif a.get("immune"):
            a.setColor(0,0,250)
        else:
            a.setColor(50,200,50)
    #model.tick()


def infect(model):
    model.reset()
    model.set("movespeed", 0.2)
    model.set("infected", 0)
    model.set("immune", 0)
    for a in model.getAgents():
        a.setColor(50,200,50)
        a.set("immune",False)
        a.set("infection",0)
        if (ag.RNG(100) < 5):
            a.setColor(200,200,0)
            a.set("infection",1000)
            model.set("infected",model.get("infected")+1)
    for x in range(model.getTileN()):
        for y in range(model.getTileN()):
            model.getTile(x,y).setColor(0,50,0)
            model.getTile(x,y).set("infection",0)

modello = ag.Model(100, 50)
modello.addSingleButton("setup", infect)
modello.addToggleButton("go", action)

ag.Start()
