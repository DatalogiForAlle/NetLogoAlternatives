#!/usr/bin/env python3
import agents as ag
import math

class Person(ag.Agent):
    def setup(self, model):
        self.set_color(50,150,50)
        self.immune = False
        self.size = 5
        self.infection = 0
        if (ag.RNG(100) < 5):
            self.set_color(200,200,0)
            self.infection = 1000
            model["infected"] += 1

    def step(self, model):
        self.direction += ag.RNG(20)-10
        self.speed = model["movespeed"]
        self.forward()
        if self.infection > 1:
            for b in self.agents_nearby(15):
                if (not b.immune) and (b.infection == 0):
                    b.infection = 1000
                    model["infected"] += 1
            self.infection -= 1
        elif self.infection == 1:
            self.infection = 0
            model["infected"] -= 1
            model["immune"] += 1
            self.immune = True
        if self.infection > 0:
            self.set_color(200,200,0)
        elif self.immune:
            self.set_color(0,0,250)
        else:
            self.set_color(50,150,50)

def setup(model):
    model.reset()
    model["movespeed"] = 0.2
    model["infected"] = 0
    model["immune"] = 0
    people = set([Person() for i in range(100)])
    model.add_agents(people)
    for a in model.get_agents():
        a.setup(model)
    for t in model.get_all_tiles():
        t.set_color(0,50,0)
        t.info["infection"] = 0

def step(model):
    for a in model.get_agents():
        a.step(model)
    model.update_plot()

epidemic_model = ag.Model(400,400,50,50)
epidemic_model.add_single_button("setup", setup)
epidemic_model.add_toggle_button("go", step)
epidemic_model.add_slider_button("movespeed", 0, 1)
epidemic_model.plot_variable("immune", 0, 0, 255)
#epidemic_model.plot_variable("infected", 255, 255, 0)
ag.Start()
