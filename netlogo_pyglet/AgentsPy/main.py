#!/usr/bin/env python3
import agents as ag
import math

def action(model):
    for a in model.get_agents():
        a.direction += ag.RNG(20)-10
        a.speed = model.get("movespeed")
        a.move()
        if (a.get("infection") > 1):
            for b in model.get_agents():
                if (a.distance_to(b.x,b.y) < 15) and (not b.get("immune")) and (b.get("infection") == 0):
                    b.set("infection",1000)
                    model.set("infected", model.get("infected")+1)
            a.set("infection",a.get("infection")-1)
        elif a.get("infection") == 1:
            a.set("infection",0)
            model.set("infected",model.get("infected")+1)
            model.set("immune",model.get("infected")+1)
            a.set("immune",True)
        if (a.get("infection") > 0):
            a.set_color(200,200,0)
        elif a.get("immune"):
            a.set_color(0,0,250)
        else:
            a.set_color(50,200,50)
    #model.tick()


def infect(model):
    model.reset()
    model.set("movespeed", 0.2)
    model.set("infected", 0)
    model.set("immune", 0)
    for a in model.get_agents():
        a.set_color(50,200,50)
        a.set("immune",False)
        a.set("infection",0)
        if (ag.RNG(100) < 5):
            a.set_color(200,200,0)
            a.set("infection",1000)
            model.set("infected",model.get("infected")+1)
    for x in range(model.get_tile_n()):
        for y in range(model.get_tile_n()):
            model.get_tile(x,y).set_color(0,50,0)
            model.get_tile(x,y).set("infection",0)

modello = ag.Model(100, 50)
modello.add_single_button("setup", infect)
modello.add_toggle_button("go", action)
modello.add_slider_button("movespeed", 0, 2)

ag.Start()
