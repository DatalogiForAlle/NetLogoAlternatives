#!/usr/bin/env python3
import agents as ag
import math
import random

class Bug(ag.Agent):
    def draw_color(self):
        c = max(0,math.floor((10-self.grow_size)/10*255))
        self.set_color(255,c,c)

    def setup(self, model):
        self.size = 2
        self.grow_size = 0
        self.draw_color()
        self.align()

    def step(self, model):
        t = self.current_tile()
        self.grow_size += min(1.0,t.info["food"])
        t.info["food"] = max(0,t.info["food"]-1.0)
        (new_x,new_y) = self.current_tile_index()
        new_x += ag.RNG(8) - 4
        new_y += ag.RNG(8) - 4
        new_t = model.get_tile_index(new_x,new_y)
        while len(new_t.get_agents()) > 0:
            (x,y) = self.current_tile_index()
            new_x += ag.RNG(8) - 4
            new_y += ag.RNG(8) - 4
            new_t = model.get_tile_index(new_x,new_y)
        self.draw_color()
        self.jump_to_tile(new_t)

def setup(model):
    model.reset()
    model["max_food_prod"] = 0.01
    model.set_update_interval(1)
    people = set([Bug() for i in range(100)])
    model.add_agents(people)
    for a in model.get_agents():
        a.setup(model)
    for t in model.get_tiles():
        t.info["food"] = 0.0
        t.set_color(0,0,0)

def step(model):
    for a in model.get_agents():
        a.step(model)
    for t in model.get_tiles():
        food_prod = random.random() * model["max_food_prod"]
        t.info["food"] += food_prod
        c = math.floor(max(0,t.info["food"] * 255))
        t.set_color(c,c,c)

epidemic_model = ag.Model(400,400,100,100)
epidemic_model.add_single_button("setup", setup)
epidemic_model.add_single_button("step", step)
epidemic_model.add_toggle_button("go", step)
ag.Start()
