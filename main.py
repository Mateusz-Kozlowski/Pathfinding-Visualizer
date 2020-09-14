from queue import Queue
from queue import PriorityQueue
import random
import os
import pygame as pg

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30)
pg.init()

WHITE = (255, 255, 255)
GREY240 = (240, 240, 240)
GREY224 = (224, 224, 224)
GREY192 = (192, 192, 192)
GREY160 = (160, 160, 160)
GREY128 = (128, 128, 128)
GREY96 = (96, 96, 96)
GREY64 = (64, 64, 64)
GREY32 = (32, 32, 32)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (245, 245, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
TURQUOISE = (64, 224, 208)
DARK_BLUE = (0, 100, 200)
PINK = (255, 0, 150)
AQUA = (0, 255, 255)
LIGHT_BLUE = (50, 220, 255)
GREEN_AQUA = (0, 255, 200)

BACKGROUND_COLOR = GREY240

FPS = 30
GRAPH_WIDTH = 736
GRAPH_HEIGHT = 736
COLUMNS = 23
ROWS = 23
NODE_WIDTH = 32
TOP_MARGIN = 16
LEFT_MARGIN = 16
WIDTH = 3 * LEFT_MARGIN + GRAPH_WIDTH + 160
HEIGHT = 768

ALGORITHMS = ['BFS', 'DFS', 'A*', 'DIJKSTRA']
NODE_TYPES = ['DEFAULT', 'BARRIER', 'START', 'END']
STATES_COLORS = {
    "DEFAULT": GREY224,
    "BARRIER": BLACK,
    "START": ORANGE,
    "IN QUEUE": AQUA,
    "ACTIVE": AQUA,
    "CLOSED": LIGHT_BLUE,
    "END": RED,
    "PATH ELEMENT": YELLOW
}

window = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("PATHFINDING VISUALIZER")
clock = pg.time.Clock()


class Button:
    def __init__(
        self, x_pos, y_pos, width, height,
        idle_color, hover_color, pressed_color,
        outline_thickness, text_color,
        char_size, text='', font='arial'
    ):
        self.xPos = int(x_pos)
        self.yPos = int(y_pos)
        self.width = int(width)
        self.height = int(height)
        self.idleColor = idle_color
        self.hoverColor = hover_color
        self.pressedColor = pressed_color
        self.lightOutlineColor = WHITE
        self.darkOutlineColor = BLACK
        self.outlineThickness = outline_thickness
        self.textColor = text_color
        self.charSize = char_size
        self.text = text
        self.font = font
        self.over = False
        self.clicked = False
        self.pressed = False

    def update(self, pos):
        self.clicked = False
        if self.xPos < pos[0] < self.xPos + self.width and self.yPos < pos[1] < self.yPos + self.height:
            self.over = True
            if pg.mouse.get_pressed()[0]:
                if not self.pressed:
                    self.clicked = True
                self.pressed = True
            else:
                self.pressed = False
        else:
            self.over = False
            self.pressed = False

    def get_clicked(self):
        return self.clicked

    def get_text(self):
        return self.text

    def render(self):
        # DRAWING TOP-LEFT OUTLINE AS A RECTANGLE WHICH WILL BE ALMOST COMPLETELY COVERED:
        pg.draw.rect(window, self.lightOutlineColor, (self.xPos, self.yPos, self.width, self.height))

        # DRAWING BOTTOM-RIGHT OUTLINE AS RECTANGLE WHICH COVERS THE PREVIOUS ONE:
        t = self.outlineThickness
        pg.draw.rect(window, self.darkOutlineColor, (self.xPos + t, self.yPos + t, self.width - t, self.height - t))

        # DRAWING CENTER OF THE CHECK-BOX:
        if self.pressed:
            pg.draw.rect(
                window, self.pressedColor, (self.xPos + t, self.yPos + t, self.width - 2 * t, self.height - 2 * t)
            )
        elif self.over:
            pg.draw.rect(
                window, self.hoverColor, (self.xPos + t, self.yPos + t, self.width - 2 * t, self.height - 2 * t)
            )
        else:
            pg.draw.rect(
                window, self.idleColor, (self.xPos + t, self.yPos + t, self.width - 2 * t, self.height - 2 * t)
            )

        # DRAWING TEXT:
        if self.text != '':
            font = pg.font.SysFont(self.font, self.charSize)
            text = font.render(self.text, 1, self.textColor)
            window.blit(
                text,
                (
                    (self.xPos + (self.width - text.get_width()) // 2),
                    (self.yPos + (self.height - text.get_height()) // 2)
                )
            )


class ChoiceBox:
    def __init__(
        self, x_pos, y_pos, background_width, option_width, space_between_options,
        background_color, background_outline_color,
        options, default_option, title, text_color, font='arial'
    ):
        self.xPos = x_pos
        self.yPos = y_pos
        self.backgroundWidth = background_width
        self.optionWidth = option_width
        self.spaceBetweenOptions = space_between_options
        self.backgroundColor = background_color
        self.backgroundOutlineColor = background_outline_color
        self.options = options
        self.currentOption = default_option
        self.title = title
        self.textColor = text_color
        self.font = pg.font.SysFont(font, self.optionWidth)
        self.backgroundOutlineThickness = 1
        self.boxOutlineThickness = 1
        self.stateHasChanged = False

    def update(self, mouse_pos):
        self.stateHasChanged = False
        x, y = mouse_pos
        for i in range(len(self.options)):
            # IF MOUSE CURSOR IS AT THE CORRECT WIDTH:
            if self.xPos + self.spaceBetweenOptions <= x <= self.xPos + self.spaceBetweenOptions + self.optionWidth:
                # AND AT THE CORRECT HEIGHT:
                if self.yPos + self.spaceBetweenOptions * (2 + i) + self.optionWidth * (1 + i) <= y:
                    if y <= self.yPos + self.spaceBetweenOptions * (2 + i) + self.optionWidth * (2 + i):
                        # AND LEFT MOUSE BUTTON IS PRESSED:
                        if pg.mouse.get_pressed()[0]:
                            # AND WE'RE CHECKING AN OPTION OTHER THAN THE CURRENT ONE:
                            if self.currentOption != self.options[i]:
                                self.stateHasChanged = True
                                self.currentOption = self.options[i]
                            break

    def get_current_option(self):
        return self.currentOption

    def set_option(self, option):
        if self.currentOption != option:
            self.stateHasChanged = True
        self.currentOption = option

    def get_state_has_changed(self):
        return self.stateHasChanged

    def render(self):
        # DRAWING TITLE AND BACKGROUND:
        text = self.font.render(self.title, 1, self.textColor)
        t = self.backgroundOutlineThickness
        pg.draw.rect(
            window, self.backgroundOutlineColor,
            (
                self.xPos,
                self.yPos,
                self.backgroundWidth,
                (2 + len(self.options)) * self.spaceBetweenOptions + (1 + len(self.options)) * self.optionWidth
            )
        )
        pg.draw.rect(
            window, self.backgroundColor,
            (
                self.xPos + t,
                self.yPos + t,
                self.backgroundWidth - 2 * t,
                (2 + len(self.options)) * self.spaceBetweenOptions + (1 + len(self.options)) * self.optionWidth - 2 * t
            )
        )
        window.blit(text, (self.xPos + self.spaceBetweenOptions, self.yPos + self.spaceBetweenOptions - 2))

        # DRAWING OPTIONS:
        for i in range(len(self.options)):
            # DRAWING TOP-LEFT OUTLINE AS A RECTANGLE WHICH WILL BE ALMOST COMPLETELY COVERED:
            pg.draw.rect(
                window, GREY64,
                (
                    self.xPos + self.spaceBetweenOptions,
                    self.yPos + self.spaceBetweenOptions * (2 + i) + self.optionWidth * (1 + i),
                    self.optionWidth,
                    self.optionWidth
                )
            )

            # DRAWING BOTTOM-RIGHT OUTLINE AS RECTANGLE WHICH COVERS THE PREVIOUS ONE:
            t = self.boxOutlineThickness
            pg.draw.rect(
                window, GREY192,
                (
                    self.xPos + self.spaceBetweenOptions + t,
                    self.yPos + self.spaceBetweenOptions * (2 + i) + self.optionWidth * (1 + i) + t,
                    self.optionWidth - t,
                    self.optionWidth - t
                )
            )

            # DRAWING CENTER OF THE CHECK BOX (COLOR DEPENDS ON STATE)
            color = GREY128 if self.options[i] == self.currentOption else WHITE
            pg.draw.rect(
                window, color,
                (
                    self.xPos + self.spaceBetweenOptions + t,
                    self.yPos + self.spaceBetweenOptions * (2 + i) + self.optionWidth * (1 + i) + t,
                    self.optionWidth - 2 * t,
                    self.optionWidth - 2 * t
                )
            )

            # DRAWING TEXT:
            text = self.font.render(self.options[i], 1, self.textColor)
            window.blit(
                text,
                (
                    self.xPos + self.optionWidth + 2 * self.spaceBetweenOptions,
                    self.yPos + self.spaceBetweenOptions * (2 + i) + self.optionWidth * (1 + i) - 2
                )
            )


class Node:
    def __init__(self, col, row, outline_color, outline_thickness):
        self.col = col
        self.row = row
        self.outlineColor = outline_color
        self.outlineThickness = outline_thickness
        self.xPos = col * NODE_WIDTH + LEFT_MARGIN
        self.yPos = row * NODE_WIDTH + TOP_MARGIN
        self.color = STATES_COLORS['DEFAULT']
        self.neighbors = []
        self.visited = False

    def get_pos(self):
        return self.col, self.row

    def get_neighbors(self):
        return self.neighbors

    def get_visited(self):
        return self.visited

    def set_visited(self, visited):
        self.visited = visited

    def update_neighbors(self, graph):
        self.neighbors = []
        if self.row > 0 and not graph.get_node(self.col, self.row - 1).is_barrier():  # UP
            self.neighbors.append(graph.get_node(self.col, self.row - 1))

        if self.col > 0 and not graph.get_node(self.col - 1, self.row).is_barrier():  # LEFT
            self.neighbors.append(graph.get_node(self.col - 1, self.row))

        if self.row < ROWS - 1 and not graph.get_node(self.col, self.row + 1).is_barrier():  # DOWN
            self.neighbors.append(graph.get_node(self.col, self.row + 1))

        if self.col < COLUMNS - 1 and not graph.get_node(self.col + 1, self.row).is_barrier():  # RIGHT
            self.neighbors.append(graph.get_node(self.col + 1, self.row))

    def render(self):
        t = self.outlineThickness
        if t > 0:
            pg.draw.rect(
                window, self.outlineColor,
                (
                    self.xPos,
                    self.yPos,
                    NODE_WIDTH + t,
                    NODE_WIDTH + t
                )
            )
        pg.draw.rect(
            window, self.color,
            (
                self.xPos + t,
                self.yPos + t,
                NODE_WIDTH - t,
                NODE_WIDTH - t
            )
        )

    # STATE ACCESSORS:
    def is_default(self):
        return self.color == STATES_COLORS['DEFAULT']

    def is_barrier(self):
        return self.color == STATES_COLORS['BARRIER']

    def is_start(self):
        return self.color == STATES_COLORS['START']

    def is_in_queue(self):
        return self.color == STATES_COLORS['IN QUEUE']

    def is_active(self):
        return self.color == STATES_COLORS['ACTIVE']

    def is_closed(self):
        return self.color == STATES_COLORS['CLOSED']

    def is_end(self):
        return self.color == STATES_COLORS['END']

    def is_path_element(self):
        return self.color == STATES_COLORS['PATH ELEMENT']

    # STATE MUTATORS:
    def set_default(self):
        self.color = STATES_COLORS['DEFAULT']

    def set_barrier(self):
        self.color = STATES_COLORS['BARRIER']

    def set_start(self):
        self.color = STATES_COLORS['START']

    def set_in_queue(self):
        self.color = STATES_COLORS['IN QUEUE']

    def set_active(self):
        self.color = STATES_COLORS['ACTIVE']

    def set_closed(self):
        self.color = STATES_COLORS['CLOSED']

    def set_end(self):
        self.color = STATES_COLORS['END']

    def set_path_element(self):
        self.color = STATES_COLORS['PATH ELEMENT']


class Graph:
    def __init__(self):
        self.nodes = []
        self.fathersPos = []
        for x in range(int(COLUMNS)):
            temp1 = []
            temp2 = []
            for y in range(int(ROWS)):
                temp1.append(Node(x, y, BLACK, 1))
                temp2.append(None)
            self.nodes.append(temp1)
            self.fathersPos.append(temp2)
        x1 = random.randint(0, COLUMNS - 1)
        y1 = random.randint(0, ROWS - 1)
        self.startPos = x1, y1
        self.set_start(x1, y1)
        x2 = random.randint(0, COLUMNS - 1)
        y2 = random.randint(0, ROWS - 1)
        while x1 == x2 and y1 == y2:
            x2 = random.randint(0, COLUMNS - 1)
            y2 = random.randint(0, ROWS - 1)
        self.endPos = x2, y2
        self.set_end(x2, y2)
        self.currentlyConsideredPos = None
        self.progressStep = 0
        self.pathIsDone = False
        self.pathCurrentlyConsideredPos = None
        self.algorithm = 'BFS'
        self.endFound = False

        # BFS STUFF:
        self.bfsPosQueue = Queue(maxsize=ROWS * COLUMNS)

        # DFS STUFF:
        self.dfsPosStack = []

        # A* STUFF:
        self.openSet = PriorityQueue()
        self.gScore = {}
        self.fScore = {}
        for y in range(ROWS):
            for x in range(COLUMNS):
                self.gScore[x, y] = float('inf')
                self.fScore[x, y] = float('inf')
        self.openSetHash = {}

        # DIJKSTRA STUFF:
        self.distances = {}
        for y in range(ROWS):
            for x in range(COLUMNS):
                self.distances[x, y] = float('inf')
        self.q = PriorityQueue()

        self.load_from_file('graph template.txt')

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def get_node(self, col, row):
        return self.nodes[col][row]

    def get_done(self):
        if self.algorithm == 'BFS':
            return self.pathIsDone or (self.bfsPosQueue.empty() and self.progressStep > 0)
        elif self.algorithm == 'DFS':
            return self.pathIsDone or (not self.dfsPosStack and self.progressStep > 0)
        elif self.algorithm == 'DIJKSTRA':
            return self.pathIsDone or (self.q.empty() and self.progressStep > 0 and not self.endFound)
        elif self.algorithm == 'A*':
            return self.pathIsDone or (self.openSet.empty() and self.progressStep > 0)

    def reset(self):
        for x in self.nodes:
            for y in x:
                if not y.is_barrier() and not y.is_start() and not y.is_end():
                    y.set_default()
                y.set_visited(False)
        for x in self.fathersPos:
            for y in x:
                y = None
        self.currentlyConsideredPos = None
        self.progressStep = 0
        self.pathIsDone = False
        self.pathCurrentlyConsideredPos = None
        self.endFound = False
        while not self.bfsPosQueue.empty():
            self.bfsPosQueue.get()
        self.dfsPosStack.clear()
        while not self.openSet.empty():
            self.openSet.get()
        for y in range(ROWS):
            for x in range(COLUMNS):
                self.gScore[x, y] = float('inf')
                self.fScore[x, y] = float('inf')
        self.openSetHash.clear()
        for y in range(ROWS):
            for x in range(COLUMNS):
                self.distances[x, y] = float('inf')
        self.q = PriorityQueue()

    def clean_all(self):
        self.reset()
        for x in self.nodes:
            for y in x:
                if y.is_barrier():
                    y.set_default()

    def make_random(self):
        self.clean_all()

        x1 = random.randint(0, COLUMNS - 1)
        y1 = random.randint(0, ROWS - 1)
        x, y = self.startPos
        self.nodes[x][y].set_default()
        self.startPos = x1, y1
        self.nodes[x1][y1].set_start()

        x2 = random.randint(0, COLUMNS - 1)
        y2 = random.randint(0, ROWS - 1)
        x, y = self.endPos
        self.nodes[x][y].set_default()
        while x1 == x2 and y1 == y2:
            x2 = random.randint(0, COLUMNS - 1)
            y2 = random.randint(0, ROWS - 1)
        self.endPos = x2, y2
        self.nodes[x2][y2].set_end()

        barrier_chance = random.randint(1, 99)
        for x in self.nodes:
            for y in x:
                if not y.is_start() and not y.is_end():
                    if random.randint(0, 100) < barrier_chance // 4:
                        y.set_barrier()
                    else:
                        y.set_default()
                y.set_visited(False)

    def save_to_file(self, file_path):
        template = open(file_path, "w")
        for y in range(int(ROWS)):
            string = ""
            for x in range(int(COLUMNS)):
                if self.nodes[x][y].is_barrier():
                    string += '1'
                elif self.nodes[x][y].is_start():
                    string += 'S'
                elif self.nodes[x][y].is_end():
                    string += 'E'
                else:
                    string += '0'
            template.write(str(string))
            template.write('\n')
        template.close()

    def load_from_file(self, file_path):
        self.clean_all()
        x, y = self.startPos
        self.nodes[x][y].set_default()
        x, y = self.endPos
        self.nodes[x][y].set_default()
        template = open(file_path, "r")
        y = 0
        for line in template:
            x = 0
            for char in line:
                if char == '1':
                    self.nodes[x][y].set_barrier()
                elif char == 'S':
                    self.nodes[x][y].set_start()
                    self.startPos = x, y
                elif char == 'E':
                    self.nodes[x][y].set_end()
                    self.endPos = x, y
                x += 1
            y += 1
        template.close()
        pass

    def render(self):
        for x in self.nodes:
            for y in x:
                y.render()

    def make_path_step(self):
        if self.pathCurrentlyConsideredPos is None:
            self.pathCurrentlyConsideredPos = self.endPos
        x, y = self.pathCurrentlyConsideredPos
        self.pathCurrentlyConsideredPos = self.fathersPos[x][y]
        x, y = self.pathCurrentlyConsideredPos
        if self.pathCurrentlyConsideredPos == self.startPos:
            self.pathIsDone = True
            return
        self.nodes[x][y].set_path_element()

    def make_bfs_step(self):
        if self.progressStep == 0:
            self.bfsPosQueue.put(self.startPos)
        else:
            x, y = self.currentlyConsideredPos
            self.set_closed(x, y)

        if not self.bfsPosQueue.empty():
            self.currentlyConsideredPos = self.bfsPosQueue.get()
            x, y = self.currentlyConsideredPos
            self.nodes[x][y].set_visited(True)
            self.set_active(x, y)

            neighbors = self.nodes[x][y].get_neighbors()
            for neighbor in neighbors:
                if not neighbor.get_visited():
                    xx, yy = neighbor.get_pos()
                    self.nodes[xx][yy].set_visited(True)
                    self.bfsPosQueue.put(neighbor.get_pos())
                    self.fathersPos[xx][yy] = self.currentlyConsideredPos
                    if self.nodes[xx][yy].is_end():
                        self.endFound = True
                        return
                    self.set_in_queue(xx, yy)

            self.progressStep = self.progressStep + 1

    def make_dfs_step(self):
        if self.progressStep == 0:
            self.dfsPosStack.append(self.startPos)
        else:
            x, y = self.currentlyConsideredPos
            self.set_closed(x, y)

        if self.dfsPosStack:
            self.currentlyConsideredPos = self.dfsPosStack.pop()
            x, y = self.currentlyConsideredPos
            self.nodes[x][y].set_visited(True)
            self.set_active(x, y)

            neighbors = self.nodes[x][y].get_neighbors()
            for neighbor in neighbors:
                if not neighbor.get_visited():
                    xx, yy = neighbor.get_pos()
                    self.nodes[xx][yy].set_visited(True)
                    self.dfsPosStack.append(neighbor.get_pos())
                    self.fathersPos[xx][yy] = self.currentlyConsideredPos
                    if self.nodes[xx][yy].is_end():
                        self.endFound = True
                        return
                    self.set_in_queue(xx, yy)

            self.progressStep = self.progressStep + 1

    def make_a_star_step(self):
        def heuristic(a, b):
            (x1, y1) = a
            (x2, y2) = b
            return abs(x1 - x2) + abs(y1 - y2)

        if self.progressStep == 0:
            x, y = self.startPos
            self.openSet.put((0, self.progressStep, self.nodes[x][y]))
            self.gScore[x, y] = 0
            self.fScore[x, y] = heuristic(self.startPos, self.endPos)
            self.openSetHash = {self.nodes[x][y]}
        else:
            x, y = self.currentlyConsideredPos
            self.set_closed(x, y)

        if not self.openSet.empty():
            self.currentlyConsideredPos = self.openSet.get()[2].get_pos()
            x, y = self.currentlyConsideredPos
            self.openSetHash.remove(self.nodes[x][y])

            if not self.nodes[x][y].is_start():
                self.set_active(x, y)

            for neighbor in self.nodes[x][y].get_neighbors():
                temp_g_score = self.gScore[x, y] + 1

                if temp_g_score < self.gScore[neighbor.get_pos()]:
                    xx, yy = neighbor.get_pos()
                    self.fathersPos[xx][yy] = x, y
                    self.gScore[neighbor.get_pos()] = temp_g_score
                    self.fScore[neighbor.get_pos()] = temp_g_score + heuristic(neighbor.get_pos(), self.endPos)
                    if neighbor not in self.openSetHash:
                        self.progressStep += 1
                        self.openSet.put((self.fScore[neighbor.get_pos()], self.progressStep, neighbor))
                        self.openSetHash.add(neighbor)
                        if neighbor.get_pos() == self.endPos:
                            self.endFound = True
                            return
                        neighbor.set_in_queue()

    def make_dijkstra_step(self):
        if self.progressStep == 0:
            for i in self.distances:
                i = float('inf')
            self.distances[self.startPos] = 0
            self.q.put(([0, self.startPos]))
        else:
            x, y = self.currentlyConsideredPos
            self.set_closed(x, y)

        if not self.q.empty():
            v_tuple = self.q.get()
            v = v_tuple[1]
            self.currentlyConsideredPos = v_tuple[1]
            x, y = self.currentlyConsideredPos
            self.nodes[x][y].set_visited(True)
            if not self.nodes[x][y].is_start():
                self.set_active(x, y)

            neighbors = self.nodes[x][y].get_neighbors()
            for neighbor in neighbors:
                candidate_distance = self.distances[v] + 1  # ALL WEIGHTS ARE 1
                if self.distances[neighbor.get_pos()] > candidate_distance:
                    self.distances[neighbor.get_pos()] = candidate_distance
                    x, y = neighbor.get_pos()
                    self.fathersPos[x][y] = self.currentlyConsideredPos
                    self.q.put(([self.distances[neighbor.get_pos()], neighbor.get_pos()]))
                    if self.endPos != neighbor.get_pos():
                        x, y = neighbor.get_pos()
                        self.nodes[x][y].set_in_queue()
                    else:
                        self.endFound = True

            self.progressStep += 1

    def make_step(self):
        if self.algorithm != 'DIJKSTRA':
            if self.endFound and not self.pathIsDone:
                self.make_path_step()
                return
        else:
            if self.endFound and not self.pathIsDone:
                if self.q.empty():
                    self.make_path_step()
                    return

        if self.algorithm == 'BFS':
            self.make_bfs_step()
        elif self.algorithm == 'DFS':
            self.make_dfs_step()
        elif self.algorithm == 'DIJKSTRA':
            self.make_dijkstra_step()
        elif self.algorithm == 'A*':
            self.make_a_star_step()

    # NODES MUTATORS:
    def set_default(self, x_pos, y_pos):
        if not self.nodes[x_pos][y_pos].is_start() and not self.nodes[x_pos][y_pos].is_end():
            self.nodes[x_pos][y_pos].set_default()

    def set_barrier(self, x_pos, y_pos):
        if not self.nodes[x_pos][y_pos].is_start() and not self.nodes[x_pos][y_pos].is_end():
            self.nodes[x_pos][y_pos].set_barrier()

    def set_start(self, x_pos, y_pos):
        if not self.nodes[x_pos][y_pos].is_end():
            x, y = self.startPos
            if self.startPos:
                self.nodes[x][y].set_default()
            self.nodes[x_pos][y_pos].set_start()
            self.startPos = (x_pos, y_pos)

    def set_in_queue(self, x_pos, y_pos):
        if not self.nodes[x_pos][y_pos].is_start() and not self.nodes[x_pos][y_pos].is_end():
            self.nodes[x_pos][y_pos].set_in_queue()

    def set_active(self, x_pos, y_pos):
        if not self.nodes[x_pos][y_pos].is_start() and not self.nodes[x_pos][y_pos].is_end():
            self.nodes[x_pos][y_pos].set_active()

    def set_closed(self, x_pos, y_pos):
        if not self.nodes[x_pos][y_pos].is_start() and not self.nodes[x_pos][y_pos].is_end():
            self.nodes[x_pos][y_pos].set_closed()

    def set_end(self, x_pos, y_pos):
        if not self.nodes[x_pos][y_pos].is_start():
            x, y = self.endPos
            if self.endPos:
                self.nodes[x][y].set_default()
            self.nodes[x_pos][y_pos].set_end()
            self.endPos = (x_pos, y_pos)

    def set_path_element(self, x_pos, y_pos):
        if not self.nodes[x_pos][y_pos].is_start() and not self.nodes[x_pos][y_pos].is_end():
            self.nodes[x_pos][y_pos].set_path_element()


def get_node_mouse_pos(pos):
    x, y = pos
    col = (x - LEFT_MARGIN) // NODE_WIDTH
    row = (y - TOP_MARGIN) // NODE_WIDTH
    return col, row


def init_buttons():
    buttons = []
    x = 2 * LEFT_MARGIN + GRAPH_WIDTH + 30
    y = 4 * TOP_MARGIN + 324 + 4 * 12 + 3 * 18 + 10
    buttons.append(Button(x, y + 0 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "RESET"))
    buttons.append(Button(x, y + 1 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "CLEAN"))
    buttons.append(Button(x, y + 2 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "RANDOM"))
    buttons.append(Button(x, y + 3 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "LOAD"))
    buttons.append(Button(x, y + 4 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "SAVE"))
    buttons.append(Button(x, y + 5 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "MAZE"))
    return buttons


def render_buttons_background():
    pg.draw.rect(
        window, BLACK,
        (
            2 * LEFT_MARGIN + GRAPH_WIDTH,
            4 * TOP_MARGIN + 324 + 4 * 12 + 3 * 18,
            160,
            HEIGHT - (4 * TOP_MARGIN + 324 + 4 * 12 + 3 * 18) - TOP_MARGIN
        )
    )
    pg.draw.rect(
        window, GREY224,
        (
            2 * LEFT_MARGIN + GRAPH_WIDTH + 1,
            4 * TOP_MARGIN + 324 + 4 * 12 + 3 * 18 + 1,
            158,
            HEIGHT - (4 * TOP_MARGIN + 324 + 4 * 12 + 3 * 18) - TOP_MARGIN - 2
        )
    )


def main():
    graph = Graph()

    # "CHOICE BOXES":
    x = 2 * LEFT_MARGIN + GRAPH_WIDTH
    algorithm_choice_box = ChoiceBox(
        x, TOP_MARGIN, 160, 18, 12, GREY224, BLACK, ALGORITHMS, 'BFS', 'ALGORITHM:', BLACK
    )
    node_action_choice_box = ChoiceBox(
        x, 2 * TOP_MARGIN + 162, 160, 18, 12, GREY224, BLACK, NODE_TYPES, 'BARRIER', 'NODE TYPE:', BLACK
    )
    on_choice_box = ChoiceBox(
        x, 3 * TOP_MARGIN + 324, 160, 18, 12, GREY224, BLACK, ['ON', 'OFF'], 'OFF', 'STATE:', BLACK
    )

    buttons = init_buttons()
    run = True
    mouse_pos = None

    while run:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

            mouse_pos = pg.mouse.get_pos()

        for btn in buttons:
            btn.update(mouse_pos)

        # CHECKING IF ANY BUTTON HAS BEEN CLICKED:
        if pg.mouse.get_pressed()[0]:
            for btn in buttons:
                if btn.get_clicked():
                    text = btn.get_text()
                    if text == 'RESET':
                        graph.reset()
                    elif text == 'CLEAN':
                        graph.clean_all()
                    elif text == 'RANDOM':
                        graph.make_random()
                    elif text == 'SAVE':
                        graph.save_to_file('graph template.txt')
                    elif text == 'LOAD':
                        graph.load_from_file('graph template.txt')
                    elif text == 'MAZE':
                        graph.load_from_file('graph maze template.txt')
                    break

        # UPDATING CHECK BOXES:
        algorithm_choice_box.update(mouse_pos)
        node_action_choice_box.update(mouse_pos)
        on_choice_box.update(mouse_pos)

        node_type = node_action_choice_box.get_current_option()

        if algorithm_choice_box.get_state_has_changed():
            graph.set_algorithm(algorithm_choice_box.get_current_option())
            graph.reset()

        # CHANGING A NODE STATE:
        if pg.mouse.get_pressed()[0]:
            col, row = get_node_mouse_pos(mouse_pos)
            if 0 <= col < COLUMNS and 0 <= row < ROWS:
                if node_type == 'DEFAULT':
                    graph.set_default(col, row)
                elif node_type == 'BARRIER':
                    graph.set_barrier(col, row)
                elif node_type == 'START':
                    graph.set_start(col, row)
                elif node_type == 'END':
                    graph.set_end(col, row)
                graph.reset()

        # REMOVING BARRIERS USING RIGHT MOUSE BUTTON:
        if pg.mouse.get_pressed()[2]:
            col, row = get_node_mouse_pos(mouse_pos)
            if 0 <= col < COLUMNS and 0 <= row < ROWS:
                graph.set_default(col, row)
                graph.reset()

        # UPDATING NEIGHBORS:
        for x in range(int(COLUMNS)):
            for y in range(int(ROWS)):
                graph.get_node(x, y).update_neighbors(graph)

        if graph.get_done():
            on_choice_box.set_option('OFF')

        if on_choice_box.get_current_option() == 'ON':
            graph.make_step()

        # RENDERING:
        window.fill(BACKGROUND_COLOR)
        graph.render()
        render_buttons_background()
        for btn in buttons:
            btn.render()
        algorithm_choice_box.render()
        node_action_choice_box.render()
        on_choice_box.render()
        pg.display.update()

    pg.quit()


if __name__ == '__main__':
    main()

print('Code is done!')
