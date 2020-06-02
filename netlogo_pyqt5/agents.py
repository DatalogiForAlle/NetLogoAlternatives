import sys
import math
import random
from PyQt5 import QtCore, QtWidgets, QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

def RNG(maximum):
    return random.randint(0,maximum)

class Agent():
    def __init__(self):
        # Associated simulation area.
        self.__model = None

        # Destroyed agents are not drawn and are removed from their area.
        self.__destroyed = False

        # Number of edges in the regular polygon representing the agent.
        self.__resolution = 10

        # Color of the agent in RGB.
        self.__color = [RNG(255), RNG(255), RNG(255)]

        self.x = 0
        self.y = 0
        self.size = 1
        self.direction = RNG(359)
        self.speed = 1

    # Ensures that the agent stays inside the simulation area.
    def __wraparound(self):
        """
        self.x = self.x % self.__model.w
        self.y = self.y % self.__model.h
        """
        self.x = ((self.x - self.size) % (self.__model.width - self.size * 2)) + self.size
        self.y = ((self.y - self.size) % (self.__model.height - self.size * 2)) + self.size

    def jump_to(self, x, y):
        self.x = x
        self.y = y

    def set_model(self, model):
        self.__model = model

    def point_towards(self, other_x, other_y):
        dist = self.distance_to(other_x,other_y)
        if dist > 0:
            self.direction = math.degrees(math.acos((other_x - self.x) / dist))
            if (self.y - other_y) > 0:
                self.direction = 360 - self.direction

    def forward(self):
        self.x += math.cos(math.radians(self.direction)) * self.speed
        self.y += math.sin(math.radians(self.direction)) * self.speed
        self.__wraparound()

    def distance_to(self, other_x, other_y):
        return ((self.x-other_x)**2 + (self.y-other_y)**2)**0.5

    # Returns a list of nearby agents.
    # May take a type as argument and only return agents of that type.
    def agents_nearby(self, distance, agent_type=None):
        nearby = set()
        for a in self.__model.agents:
            if self.distance_to(a.x,a.y) <= distance and not (a is self):
                if agent_type == None or type(a) is agent_type:
                    nearby.add(a)
        return nearby

    def current_tile(self):
        x = math.floor(self.__model.x_tiles * self.x / self.__model.w)
        y = math.floor(self.__model.y_tiles * self.y / self.__model.h)
        try:
            return self.__model.tiles[x][y]
        except:
            print(self.x,self.y,x,y)

    # Returns the surrounding tiles as a 3x3 grid. Includes the current tile.
    def neighbor_tiles(self):
        tileset = [[None for y in range(3)] for x in range(3)]
        (tx,ty) = self.model.get_tiles_xy()
        for y in range(3):
            for x in range(3):
                x = (floor(tx * self.x / self.__model.w)+x-1) % tx
                y = (floor(ty * self.y / self.__model.h)+y-1) % ty
                tileset[x][y] = self.__model.tiles[x][y]
        return tileset

    def is_destroyed(self):
        return self.__destroyed

    def destroy(self):
        if not self.__destroyed:
            self.__destroyed = True

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, color):
        r, g, b = color
        self.__color = [r, g, b]


class Tile():
    def __init__(self,x, y, model):
        self.x = x
        self.y = y
        self.info = {}
        self.color = (0, 0, 0)

        # Associated model.
        self.__model = model


class Model:
    def __init__(self, title, x_tiles, y_tiles, tile_size=8):
        # Title of model, shown in window title
        self.title = title

        # Number of tiles on the x/y axis.
        self.x_tiles = x_tiles
        self.y_tiles = y_tiles

        # Pixel sizes
        self.tile_size = tile_size
        self.width = x_tiles * tile_size
        self.height = y_tiles * tile_size

        # Internal set of agents.
        self.agents = set()

        # Initial tileset (empty).
        self.tiles = [Tile(x, y, self)
                      for y in range(y_tiles)
                      for x in range(x_tiles)]

        # Initialize application
        self.qapp = QtWidgets.QApplication(sys.argv)
        self.myapp = Application(self.title)

        self.variables = {}


    def add_agent(self, agent):
        agent.set_model(self)
        agent.x = RNG(self.width)
        agent.y = RNG(self.height)
        self.agents.add(agent)

    def add_agents(self, agents):
        for a in agents:
            self.add_agent(a)

    # Destroys all agents, clears the agent set, and resets all tiles.
    def reset(self):
        for a in self.agents:
            a.destroy()
        self.agents.clear()
        for x in range(self.x_tiles):
            for y in range(self.y_tiles):
                i = y*self.x_tiles + x
                self.tiles[i].color = (0,0,0)
                self.tiles[i].info = {}

    def add_button(self, label, func):
        self.myapp.add_button(label, func, self)

    def add_toggle_button(self, label, func):
        self.myapp.add_toggle(label, func, self)

    def add_slider(self, variable, minval, maxval, initial):
        self.myapp.add_slider(variable, minval, maxval, initial, self)

    def run(self):
        # TODO: move run function to a module-level agents.run(model)
        # method to separate UI and model completely
        self.myapp.simulation_area.model = self

        # Launch the application
        self.qapp.exec_()

        # Application was closed, clean up and exit
        sys.exit(0)

    def __setitem__(self, key, item):
        self.variables[key] = item

    def __getitem__(self, key):
        return self.variables[key]

    def __delitem__(self, key):
        del self.variables[key]


class SimulationArea(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__model = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000/60)

    @property
    def model(self):
        return self.__model

    @model.setter
    def model(self, model):
        self.__model = model
        self.setFixedSize(model.width, model.height)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Default to a white background
        white = QtGui.QColor('white')
        painter.setBrush(white)
        painter.drawRect(0, 0, painter.device().width(), painter.device().height())

        if self.model:
            # Draw tiles
            for tile in self.model.tiles:
                self.paintTile(painter, tile)
            # Draw agents
            for agent in self.model.agents:
                self.paintAgent(painter, agent)

    def paintAgent(self, painter, agent):
        r, g, b = agent.color
        painter.setBrush(QtGui.QColor(r, g, b))
        painter.drawEllipse(agent.x, agent.y, agent.size, agent.size)

    def paintTile(self, painter, tile):
        r, g, b = tile.color
        color = QtGui.QColor(r, g, b)
        painter.setBrush(color)
        x = self.model.tile_size * tile.x
        y = self.model.tile_size * tile.y
        painter.drawRect(x, y, self.model.tile_size, self.model.tile_size)

class Plot(FigureCanvasQTAgg):
    # TODO: Connect with data, just shows random data
    def __init__(self, parent=None):
        self.figure = Figure()
        super(Plot, self).__init__(self.figure)
        self.setParent(parent)
        self.setMinimumWidth(400)
        self.setMinimumHeight(230)

    def plot(self):
        ''' plot some random stuff '''
        # random data
        data = [random.random() for i in range(10)]

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.clear()

        # plot data
        ax.plot(data, '*-')

        # refresh canvas
        self.draw()


class ToggleButton(QtWidgets.QPushButton):
    def __init__(self, text, func, model):
        super().__init__(text)
        self.toggled.connect(self.on_toggle)
        self.setCheckable(True)
        self.model = model
        self.func = func
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.func(model))

    def on_toggle(self, checked):
        if checked:
            self.timer.start(1000/60)
        else:
            self.timer.stop()

class Slider(QtWidgets.QSlider):
    def __init__(self, variable, minval, maxval, initial):
        super().__init__(QtCore.Qt.Horizontal)
        self.setMinimum(minval)
        self.setMaximum(maxval)
        self.setValue(initial)

    # TODO: Support floats. See https://stackoverflow.com/a/50300848/


class Application():
    def __init__(self, title):
        self.controller_rows = []
        self.plots = []
        self.initializeUI(title)
        self.add_controller_row()
        self.add_plot()

    def add_controller_row(self):
        self.current_row = QtWidgets.QHBoxLayout()
        self.controller_box.addLayout(self.current_row)
        self.controller_rows.append(self.current_row)

    def add_button(self, text, func, model):
        btn = QtWidgets.QPushButton(text)
        btn.clicked.connect(lambda x: func(model))
        self.current_row.addWidget(btn)

    def add_toggle(self, text, func, model):
        btn = ToggleButton(text, func, model)
        #btn.clicked.connect(lambda x: func(model))
        self.current_row.addWidget(btn)

    def add_slider(self, variable, minval, maxval, initial, model):
        slider = Slider(variable, minval, maxval, initial)
        def update_variable(v):
            model[variable] = v
        slider.valueChanged.connect(update_variable)
        self.current_row.addWidget(slider)

    def add_plot(self):
        plot = Plot()
        plot.plot()
        self.plots.append(plot)
        self.plots_box.addWidget(plot)

    def initializeUI(self, title):
        # Initialize main window and central widget
        self.mainwindow = QtWidgets.QMainWindow()
        self.mainwindow.setWindowTitle(title)
        self.centralwidget = QtWidgets.QWidget(self.mainwindow)
        self.mainwindow.setCentralWidget(self.centralwidget)

        # Add horizontal divider
        self.horizontal_divider = QtWidgets.QHBoxLayout(self.centralwidget)
        self.centralwidget.setLayout(self.horizontal_divider)

        # Box for left side (simulation area + controllers)
        self.left_box = QtWidgets.QVBoxLayout()
        self.horizontal_divider.addLayout(self.left_box)

        # Box for right side (plots)
        self.right_box = QtWidgets.QVBoxLayout()
        self.plots_box = QtWidgets.QVBoxLayout()
        self.horizontal_divider.addLayout(self.right_box)
        self.right_box.addLayout(self.plots_box)
        self.right_box.addStretch(1)

        # Simulation area
        self.simulation_area = SimulationArea()
        self.left_box.addWidget(self.simulation_area)

        # Controller box (bottom left)
        self.controller_box = QtWidgets.QVBoxLayout()
        self.left_box.addLayout(self.controller_box)
        self.left_box.addStretch(1)

        self.mainwindow.show()
