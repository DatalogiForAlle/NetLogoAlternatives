#!/usr/bin/env python3
import numpy as np
from EpidemicModel import *
import matplotlib.pyplot as plt
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import ModularServer,VisualizationElement

def agent_portrayal(agent):
    portrayal = {"Layer":0}
    if agent.immune:
        portrayal["Color"] = "#3399ff"
    elif agent.infection > 0:
        portrayal["Color"] = "#ffff66"
    else:
        portrayal["Color"] = "#009933"
    return portrayal

class FreeRoamModule(VisualizationElement):
    local_includes = ["FreeCanvas.js"]

    def __init__(self, portrayal_method, canvas_height, canvas_width):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.portrayal_method = portrayal_method
        new_element = "new FreeCanvas({}, {})"
        new_element = new_element.format(canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        space_state = defaultdict(list)
        for agent in model.schedule.agents:
            portrayal = self.portrayal_method(agent)
            if portrayal:
                portrayal["x"] = agent.pos[0]
                portrayal["y"] = agent.pos[1]
                space_state[portrayal["Layer"]].append(portrayal)
        return space_state

freeroam = FreeRoamModule(agent_portrayal, 500, 500)
server = ModularServer(EpidemicModel,
                       [freeroam],
                       "Epidemic Model",
                       {"N":100,
                        "width":500,
                        "height":500,
                        "infection_rate": UserSettableParameter('slider', 'Initial infection rate', 5, 1, 20),
                        "movespeed": UserSettableParameter('slider', 'Movement per tick', 1, 0.2, 2, 0.2)})
server.port = 8521
server.launch()
