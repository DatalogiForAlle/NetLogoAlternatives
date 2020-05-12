import agents as ag

class Electron(ag.Agent):
    def __init__(self):
        super().__init__()
        self.size = 5
        self.set_color(0,0,255)
        self.speed=modello.get("speed")
        self.set("charged",False)

class Nucleon(ag.Agent):
    def __init__(self):
        super().__init__()
        self.size = 10
        self.set_color(255,0,0)
        self.set("charged",False)

def setup(model):
    model.reset()
    modello.set("speed",2)
    modello.set("charge-flow",0)
    electrons = set([Electron() for i in range(200)])
    model.add_agents(electrons)
    nucleons = set([Nucleon() for i in range(200)])
    model.add_agents(nucleons)
    for x in range(model.get_tile_n()):
        for y in range(model.get_tile_n()):
            model.get_tile(x,y).set_color(100,100,100)

def go(agent):
    agent.speed=modello.get("speed")
    agent.direction=180
    if isinstance(agent,Electron):
        if agent.x < agent.speed :
            modello.set("charge-flow",1+modello.get("charge-flow"))
            agent.set("charged",True)
        elif agent.get("charged"):
            modello.set("charge-flow",modello.get("charge-flow")-1)
            agent.set("charged",False)
        for b in agent.in_range(10):
            if isinstance(b,Nucleon):
                agent.point_to(b.x,b.y)
                agent.direction -= 180
        agent.move()

modello = ag.Model(50)
modello.add_setup_button(setup)
modello.add_run_button(go)
modello.add_slider_button("speed",0.1,10)
modello.plot_variable("charge-flow",100,100,250)
ag.Start()
