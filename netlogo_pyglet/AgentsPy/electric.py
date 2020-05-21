import agents as ag

class Electron(ag.Agent):
    def setup(self, model):
        self.size = 5
        self.set_color(0,0,255)
        self.speed=model["speed"]
        self.direction = 180
        self.charged = False

    def step(self, model):
        self.speed=model["speed"]
        self.direction=180
        if self.x < self.speed+self.size:
            model["charge_flow"] += 1
        for b in self.agents_nearby(distance=10,agent_type=Nucleon):
            self.point_towards(b.x,b.y)
            self.direction -= 180
        self.forward()

class Nucleon(ag.Agent):
    def setup(self, model):
        self.size = 10
        self.set_color(255,0,0)

    def step(self, model):
        pass

def setup(model):
    model.reset()
    model["speed"] = 2
    model["charge_flow"] = 0
    electrons = set([Electron() for i in range(200)])
    model.add_agents(electrons)
    nucleons = set([Nucleon() for i in range(50)])
    model.add_agents(nucleons)
    for agent in model.get_agents():
        agent.setup(model)
    for tile in model.get_all_tiles():
        tile.set_color(100,100,100)

def step(model):
    old_charge_flow = model["charge_flow"]
    model["charge_flow"] = 0
    for agent in model.get_agents():
        agent.step(model)
    model["charge_flow"] = model["charge_flow"] * 0.01 + old_charge_flow * 0.99 
    model.update_plot()

modello = ag.Model(400,200,50,25)
modello.add_single_button("Setup", setup)
modello.add_toggle_button("Go", step)
modello.add_slider_button("speed",0.1,3)
modello.plot_variable("charge_flow",100,100,250)
ag.Start()
