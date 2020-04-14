import math
from mesa import Agent, Model
from collections import defaultdict
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector

class EpidemicAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.infection = 0
        self.immune = False
        self.direction = self.random.randrange(361)
        self.speed = model.movespeed

    def move(self):
        new_x = math.cos(self.direction*(2*math.pi)/360)*self.speed + self.pos[0]
        new_y = math.sin(self.direction*(2*math.pi)/360)*self.speed + self.pos[1]
        self.direction += self.random.randrange(21) - 10
        self.model.space.move_agent(self, (new_x,new_y))

    def infect(self):
        for a in self.model.space.get_neighbors(self.pos, 15, include_center=False):
            if (not a.immune and a.infection == 0) and (self.infection > 0):
                a.infection = 100

    def heal(self):
        if (self.infection == 1):
            self.infection = 0
            self.immune = True
        elif (self.infection > 1):
            self.infection -= 1

    def step(self):
        self.move()
        self.heal()
        if (self.infection > 0):
            self.infect()

class EpidemicModel(Model):
    """A model with some number of agents."""
    def __init__(self, N, width, height, infection_rate, movespeed):
        self.num_agents = N
        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(width, height, True)
        self.running = True
        self.infection_rate = infection_rate
        self.movespeed = movespeed

        # Create agents
        for i in range(self.num_agents):
            a = EpidemicAgent(i, self)
            if self.random.randrange(100) < self.infection_rate:
                a.infection = 100
            self.schedule.add(a)

            x = self.random.randrange(self.space.width)
            y = self.random.randrange(self.space.height)
            self.space.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            model_reporters={"People": "num_agents"},  # `compute_gini` defined above
            agent_reporters={})

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
