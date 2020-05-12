#!/usr/bin/env python3
import agents as ag
import math

def action(agent):
    agent.direction += ag.RNG(20)-10
    agent.speed = modello.get("movespeed")
    agent.move()
    if (agent.get("infection") > 1):
        for b in agent.in_range(15):
            if (not b.get("immune")) and (b.get("infection") == 0):
                b.set("infection",1000)
                modello.set("infected", modello.get("infected")+1)
        agent.set("infection",agent.get("infection")-1)
    elif agent.get("infection") == 1:
        agent.set("infection",0)
        modello.set("infected",modello.get("infected")+1)
        modello.set("immune",modello.get("infected")+1)
        agent.set("immune",True)
    if (agent.get("infection") > 0):
        agent.set_color(200,200,0)
    elif agent.get("immune"):
        agent.set_color(0,0,250)
    else:
        agent.set_color(50,200,50)
    modello.update_plot()


def infect(agent):
    #for a in model.get_agents():
    agent.set_color(50,200,50)
    agent.set("immune",False)
    agent.set("infection",0)
    if (ag.RNG(100) < 5):
        agent.set_color(200,200,0)
        agent.set("infection",1000)
        modello.set("infected",modello.get("infected")+1)

modello = ag.Model(50)
people = set([ag.Agent() for i in range(100)])
modello.add_agents(people)
for x in range(modello.get_tile_n()):
    for y in range(modello.get_tile_n()):
        modello.get_tile(x,y).set_color(0,50,0)
        modello.get_tile(x,y).set("infection",0)
modello.add_single_button("setup", infect)
modello.add_toggle_button("go", action)
modello.add_toggle_button("go", action)
modello.add_toggle_button("go", action)
modello.add_toggle_button("go", action)
modello.add_slider_button("movespeed", 0, 200)

modello.set("movespeed", 0.2)
modello.set("infected", 0)
modello.set("immune", 0)
modello.plot_variable("infected", 255, 0, 0)
ag.Start()
