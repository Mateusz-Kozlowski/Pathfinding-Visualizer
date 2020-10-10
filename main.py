from queue import Queue
from queue import PriorityQueue
import random
import os
import pygame as pg

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30)
pg.init()

# Colors:
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

# Some constants:
BACKGROUND_COLOR = GREY240
FPS = 60
LEFT_MARGIN = 16
TOP_MARGIN = 16
WIDTH = 944
HEIGHT = 768
TITLE = "Pathfinding Visualizer"

window = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(TITLE)


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
		self.outlineThickness = outline_thickness
		self.textColor = text_color
		self.charSize = char_size
		self.text = text
		self.font = font
		self.over = False
		self.clicked = False
		self.pressed = False
		self.lightOutlineColor = WHITE
		self.darkOutlineColor = BLACK

	def update(self, mouse_pos):
		"""
		CALL THE FUNCTION EVERY FRAME, BEFORE:
		- CHECKING IF THE BUTTON HAS BEEN CLICKED
		- CHECKING IF THE BUTTON IS PRESSED
		- RENDERING

		TAKES AS ARGUMENT THE LAST MOUSE POSITION
		"""
		self.clicked = False

		# CHECKING IF THE BUTTON IS CLICKED
		if self.xPos < mouse_pos[0] < self.xPos + self.width and self.yPos < mouse_pos[1] < self.yPos + self.height:
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
		"""
		RETURNS TRUE IF THE BUTTON WAS CLICKED DURING LAST update FUNCTION CALL, OTHERWISE RETURNS FALSE
		"""
		return self.clicked

	def get_text(self):
		"""
		RETURNS THE TEXT OF THE BUTTON
		"""
		return self.text

	def render(self):
		"""
		CALL THE FUNCTION AT THE END OF EVERY FRAME
		"""

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
		"""
		CALL THE FUNCTION EVERY FRAME, BEFORE:
		- CHECKING IF THE CHOICE BOX HAS BEEN CLICKED
		- CHECKING IF THE CHOICE BOX IS PRESSED
		- RENDERING

		TAKES AS ARGUMENT THE LAST MOUSE POSITION
		"""

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
		"""
		RETURNS CURRENTLY SELECTED OPTION
		"""
		return self.currentOption

	def set_option(self, option):
		"""
		CHANGES CURRENTLY SELECTED OPTION
		"""
		if self.currentOption != option:
			self.stateHasChanged = True
		self.currentOption = option

	def get_state_has_changed(self):
		"""
		RETURNS TRUE IF THE CHOICE BOX OPTION HAS CHANGED SINCE OR DURING LAST update FUNCTION CALL
		"""
		return self.stateHasChanged

	def render(self):
		"""
		CALL THE FUNCTION AT THE END OF EVERY FRAME
		"""

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
	"""
	THE NODE CLASS IS ADAPTED TO UDE IN GRAPHS IN THE FORM OF A RECTANGULAR GRID, WHERE EACH VERTEX HAS 4 NEIGHBORS
	"""

	statesColors = {
		'START': ORANGE,
		'END': RED,
		'ACTIVE': AQUA,
		'IN_QUEUE': AQUA,
		'CLOSED': LIGHT_BLUE,
		'IN_PATH': YELLOW
	}

	def __init__(self, x_pos, y_pos, col, row, size, outline_color, outline_thickness, min_weight, max_weight, weight):
		self.xPos = x_pos
		self.yPos = y_pos
		self.col = col
		self.row = row
		self.size = size
		self.outlineColor = outline_color
		self.outlineThickness = outline_thickness
		self.neighbors = list()
		self.visited = False
		self.state = None
		self.minWeight = min_weight
		self.maxWeight = max_weight
		self.__weight = weight
		info = "ERROR: class Node: __init__ function: following condition isn't met: min_weight <= weight <= max_weight"
		info += " (" + str(min_weight) + " <= " + str(weight) + " <= " + str(max_weight) + ")"
		assert min_weight <= weight <= max_weight, info

	# Accessors:
	def get_coordinates(self):
		"""
		RETURNS THE NODE COORDINATES (COLUMN AND ROW IN WHICH IT IS LOCATED)
		"""
		return self.col, self.row

	def get_neighbors(self):
		"""
		RETURNS ALL NEIGHBORS OF THE NODE
		"""
		return self.neighbors

	def has_been_visited(self):
		"""
		IF THE NODE IS MARKED AS VISITED RETURNS TRUE, OTHERWISE FALSE
		"""
		return self.visited

	def get_state(self):
		"""
		RETURNS CURRENT NODE STATE AS A STRING, BUT IF THE NODE HASN'T GOT ANY STATE, FUNCTION RETURNS PYTHONIC None
		"""
		return self.state

	def get_weight(self):
		"""
		RETURNS THE NODE WEIGHT, WHICH IS A NUMBER IN RANGE 1-255
		"""
		return self.__weight

	# Mutators:
	def set_visited(self, visited):
		"""
		MARKS THE NODE AS VISITED OR UNVISITED, TAKES AS THE ARGUMENT PYTHONIC True OR False
		"""
		self.visited = visited

	def change_state(self, state):
		"""
		TAKES AS THE ARGUMENT STRING OR PYTHONIC None
		"""
		self.state = state

	def set_weight(self, weight):
		"""
		TAKES AS THE ARGUMENT WEIGHT, WHICH IS A NUMBER IN RANGE 1-255
		"""

		info = "ERROR: class Node: __init__ function: following condition isn't met: min_weight <= weight <= max_weight"
		info += " (" + str(self.minWeight) + " <= " + str(weight) + " <= " + str(self.maxWeight) + ")"
		assert self.minWeight <= weight <= self.maxWeight, info
		self.__weight = weight

	# Others:
	def update_neighbors(self, graph):
		"""
		CALL THE FUNCTION AFTER ALL CHANGES OF ANY NODES OF THE GRAPH IN A FRAME
		"""
		self.neighbors = []

		# UP:
		if self.row > 0 and not graph.get_node(self.col, self.row - 1).get_weight() == self.maxWeight:
			self.neighbors.append(graph.get_node(self.col, self.row - 1))

		# LEFT:
		if self.col > 0 and not graph.get_node(self.col - 1, self.row).get_weight() == self.maxWeight:
			self.neighbors.append(graph.get_node(self.col - 1, self.row))

		# DOWN:
		if self.row < graph.rowsCount - 1 and not graph.get_node(self.col, self.row + 1).get_weight() == self.maxWeight:
			self.neighbors.append(graph.get_node(self.col, self.row + 1))

		# RIGHT:
		if self.col < graph.columnsCount - 1 and not graph.get_node(self.col + 1, self.row).get_weight() == self.maxWeight:
			self.neighbors.append(graph.get_node(self.col + 1, self.row))

	def render_with_state(self):
		"""
		RENDER THE NODE IN A COLOR DEPENDING ON ITS STATE
		IF THE NODE HAS NO STATE, IT IS RENDERED AS IN THE FUNCTION render_without_state
		"""

		if self.outlineThickness > 0:
			pg.draw.rect(
				window, self.outlineColor,
				(
					self.xPos,
					self.yPos,
					self.size + self.outlineThickness,
					self.size + self.outlineThickness
				)
			)

		if self.state is None:
			color_component = int(255 * (1 - (self.__weight - self.minWeight) / (self.maxWeight - self.minWeight)))
			pg.draw.rect(
				window, (color_component, color_component, color_component),
				(
					self.xPos + self.outlineThickness,
					self.yPos + self.outlineThickness,
					self.size - self.outlineThickness,
					self.size - self.outlineThickness
				)
			)
		else:
			pg.draw.rect(
				window, Node.statesColors[self.state],
				(
					self.xPos + self.outlineThickness,
					self.yPos + self.outlineThickness,
					self.size - self.outlineThickness,
					self.size - self.outlineThickness
				)
			)

	def render_without_state(self):
		"""
		RENDER THE NODE IN BLACK-AND-WHITE COLORS WITH A SHADE DEPENDING ON ITS WEIGHT
		THE GREATER THE WEIGHT, THE DARKER COLOR
		"""

		if self.outlineThickness > 0:
			pg.draw.rect(
				window, self.outlineColor,
				(
					self.xPos,
					self.yPos,
					self.size + self.outlineThickness,
					self.size + self.outlineThickness
				)
			)

		color_component = int(255 * (1 - (self.__weight - self.minWeight) / (self.maxWeight - self.minWeight)))
		pg.draw.rect(
			window, (color_component, color_component, color_component),
			(
				self.xPos + self.outlineThickness,
				self.yPos + self.outlineThickness,
				self.size - self.outlineThickness,
				self.size - self.outlineThickness
			)
		)


class BfsComponent:
	def __init__(self, columns_count, rows_count):
		self.queue = Queue(maxsize=rows_count * columns_count)


class DfsComponent:
	def __init__(self):
		self.stack = list()


class DijkstraComponent:
	def __init__(self, rows_count, columns_count):
		self.distances = {}
		for y in range(rows_count):
			for x in range(columns_count):
				self.distances[x, y] = float('inf')
		self.priorityQueue = PriorityQueue()


class AStarComponent:
	def __init__(self):
		self.count = None
		self.openSet = PriorityQueue()
		self.gScore = None
		self.fScore = None
		self.openSetHash = None


class AlgoComponents:
	def __init__(self, columns_count, rows_count):
		self.fathersPos = list()
		for i in range(columns_count):
			temp = list()
			for j in range(rows_count):
				temp.append(None)
			self.fathersPos.append(temp)
		self.bfs = BfsComponent(columns_count, rows_count)
		self.dfs = DfsComponent()
		self.dijkstra = DijkstraComponent(columns_count, rows_count)
		self.aStar = AStarComponent()


class Graph:
	def __init__(
			self, x_pos, y_pos, columns_count, rows_count,
			node_size, node_outline_color, node_outline_thickness,
			min_nodes_weight, max_node_weight, default_nodes_weights
	):
		self.xPos = x_pos
		self.yPos = y_pos
		self.columnsCount = columns_count
		self.rowsCount = rows_count
		self.minNodeWeight = min_nodes_weight
		self.maxNodeWeight = max_node_weight

		# constructing nodes:
		self.nodes = list()
		for x in range(int(columns_count)):
			temp = []
			for y in range(int(rows_count)):
				temp.append(
					Node(
						x_pos + x * node_size, y_pos + y * node_size, x, y,
						node_size, node_outline_color, node_outline_thickness,
						min_nodes_weight, max_node_weight, default_nodes_weights
					)
				)
			self.nodes.append(temp)

		# making random start position:
		x1_temp = random.randint(0, columns_count - 1)
		y1_temp = random.randint(0, rows_count - 1)
		self.startPos = x1_temp, y1_temp
		self.nodes[x1_temp][y1_temp].change_state('START')

		# making random end position:
		x2_temp = random.randint(0, columns_count - 1)
		y2_temp = random.randint(0, rows_count - 1)
		while x1_temp == x2_temp and y1_temp == y2_temp:
			x2_temp = random.randint(0, columns_count - 1)
			y2_temp = random.randint(0, rows_count - 1)
		self.endPos = x2_temp, y2_temp
		self.nodes[x2_temp][y2_temp].change_state('END')

		self.algorithm = 'BFS'
		self.sthHappened = False
		self.currentlyConsideredPos = None
		self.endFound = False
		self.currentlyConsideredPathPos = None
		self.pathIsDone = False

		self.algoComponents = AlgoComponents(columns_count, rows_count)

		self.load_from_file('Graph templates/start.txt')

	# "PRIVATE" METHODS (ARE USED ONLY BY OTHER METHODS OF THIS CLASS):
	def make_path_step(self):
		if self.currentlyConsideredPathPos is None:
			self.currentlyConsideredPathPos = self.endPos
		x, y = self.currentlyConsideredPathPos
		self.currentlyConsideredPathPos = self.algoComponents.fathersPos[x][y]
		x, y = self.currentlyConsideredPathPos
		if self.currentlyConsideredPathPos == self.startPos:
			self.pathIsDone = True
			return
		self.nodes[x][y].change_state('IN_PATH')

	def make_bfs_step(self):
		if not self.sthHappened:
			self.algoComponents.bfs.queue.put(self.startPos)
			self.sthHappened = True
		else:
			x, y = self.currentlyConsideredPos
			self.safely_change_node_state(x, y, 'CLOSED')

		if not self.algoComponents.bfs.queue.empty():
			self.currentlyConsideredPos = self.algoComponents.bfs.queue.get()
			x, y = self.currentlyConsideredPos
			self.nodes[x][y].set_visited(True)
			self.safely_change_node_state(x, y, 'ACTIVE')

			neighbors = self.nodes[x][y].get_neighbors()
			for neighbor in neighbors:
				if not neighbor.has_been_visited():
					xx, yy = neighbor.get_coordinates()
					self.nodes[xx][yy].set_visited(True)
					self.algoComponents.bfs.queue.put(neighbor.get_coordinates())
					self.algoComponents.fathersPos[xx][yy] = self.currentlyConsideredPos
					if self.nodes[xx][yy].get_state() == 'END':
						self.endFound = True
						return
					self.safely_change_node_state(xx, yy, 'IN_QUEUE')

	def make_dfs_step(self):
		if not self.sthHappened:
			self.algoComponents.dfs.stack.append(self.startPos)
			self.sthHappened = True
		else:
			x, y = self.currentlyConsideredPos
			self.safely_change_node_state(x, y, 'CLOSED')

		if self.algoComponents.dfs.stack:
			self.currentlyConsideredPos = self.algoComponents.dfs.stack.pop()
			x, y = self.currentlyConsideredPos
			self.nodes[x][y].set_visited(True)
			self.safely_change_node_state(x, y, 'ACTIVE')

			neighbors = self.nodes[x][y].get_neighbors()
			for neighbor in neighbors:
				if not neighbor.has_been_visited():
					xx, yy = neighbor.get_coordinates()
					self.nodes[xx][yy].set_visited(True)
					self.algoComponents.dfs.stack.append(neighbor.get_coordinates())
					self.algoComponents.fathersPos[xx][yy] = self.currentlyConsideredPos
					if self.nodes[xx][yy].get_state() == 'END':
						self.endFound = True
						return
					self.safely_change_node_state(xx, yy, 'IN_QUEUE')

	def make_dijkstra_step(self):
		if not self.sthHappened:
			self.sthHappened = True
			self.algoComponents.dijkstra.distances[self.startPos] = 0
			self.algoComponents.dijkstra.priorityQueue.put(([0, self.startPos]))
		else:
			x, y = self.currentlyConsideredPos
			self.safely_change_node_state(x, y, 'CLOSED')

		if not self.algoComponents.dijkstra.priorityQueue.empty():
			v_tuple = self.algoComponents.dijkstra.priorityQueue.get()
			v = v_tuple[1]
			self.currentlyConsideredPos = v_tuple[1]

			if self.currentlyConsideredPos == self.endPos:
				self.endFound = True
				return

			x, y = self.currentlyConsideredPos
			self.nodes[x][y].set_visited(True)
			self.safely_change_node_state(x, y, 'ACTIVE')

			neighbors = self.nodes[x][y].get_neighbors()
			for neighbor in neighbors:
				x, y = neighbor.get_coordinates()
				candidate_distance = self.algoComponents.dijkstra.distances[v] + self.nodes[x][y].get_weight()
				if self.algoComponents.dijkstra.distances[neighbor.get_coordinates()] > candidate_distance:
					self.algoComponents.dijkstra.distances[neighbor.get_coordinates()] = candidate_distance
					self.algoComponents.fathersPos[x][y] = self.currentlyConsideredPos
					self.algoComponents.dijkstra.priorityQueue.put(
						([self.algoComponents.dijkstra.distances[neighbor.get_coordinates()], neighbor.get_coordinates()])
					)
					x, y = neighbor.get_coordinates()
					self.safely_change_node_state(x, y, 'IN_QUEUE')

	def make_a_star_step(self):
		def heuristic(a, b):
			x1, y1 = a
			x2, y2 = b
			return abs(x1 - x2) + abs(y1 - y2)

		if not self.sthHappened:
			self.sthHappened = True
			self.algoComponents.aStar.count = 0
			self.algoComponents.aStar.openSet = PriorityQueue()
			xs, ys = self.startPos
			self.algoComponents.aStar.openSet.put((0, self.algoComponents.aStar.count, self.nodes[xs][ys]))
			self.algoComponents.aStar.gScore = {node: float("inf") for row in self.nodes for node in row}
			self.algoComponents.aStar.gScore[self.nodes[xs][ys]] = 0
			self.algoComponents.aStar.fScore = {node: float("inf") for row in self.nodes for node in row}
			xe, ye = self.endPos
			temp = heuristic(self.nodes[xs][ys].get_coordinates(), self.nodes[xe][ye].get_coordinates())
			self.algoComponents.aStar.fScore[self.nodes[xs][ys]] = temp
			self.algoComponents.aStar.openSetHash = {self.nodes[xs][ys]}

		if not self.algoComponents.aStar.openSet.empty():
			current = self.algoComponents.aStar.openSet.get()[2]
			self.algoComponents.aStar.openSetHash.remove(current)
			self.currentlyConsideredPos = current.get_coordinates()

			if current.get_coordinates() == self.endPos:
				self.endFound = True
				return

			for neighbor in current.get_neighbors():
				xx, yy = neighbor.get_coordinates()
				temp_g_score = self.algoComponents.aStar.gScore[current] + self.nodes[xx][yy].get_weight()

				if temp_g_score < self.algoComponents.aStar.gScore[neighbor]:
					self.algoComponents.fathersPos[xx][yy] = current.get_coordinates()
					self.algoComponents.aStar.gScore[neighbor] = temp_g_score
					self.algoComponents.aStar.fScore[neighbor] = temp_g_score + heuristic(neighbor.get_coordinates(), self.endPos)

					if neighbor not in self.algoComponents.aStar.openSetHash:
						self.algoComponents.aStar.count += 1
						self.algoComponents.aStar.openSet.put(
							(
								self.algoComponents.aStar.fScore[neighbor],
								self.algoComponents.aStar.count,
								neighbor
							)
						)
						self.algoComponents.aStar.openSetHash.add(neighbor)
						self.safely_change_node_state(xx, yy, 'IN_QUEUE')

			x, y = current.get_coordinates()
			self.safely_change_node_state(x, y, 'CLOSED')

	# ACCESSORS:
	def get_node_coordinates(self, mouse_pos):
		"""
		RETURNS OVER WHICH COLUMN AND ROW OF THE GRAPH THE MOUSE CURSOR IS LOCATED.
		NOTICE THAT IF THE MOUSE CURSOR ISN'T OVER THE GRAPH THE FUNCTION WILL RETURN NEGATIVE OR TOO BIG NUMBERS.
		IN OTHER WORDS, THE FUNCTION DOESN'T CHECK IF THE MOUSE CURSOR IS OVER THE GRAPH.
		"""
		x, y = mouse_pos
		col = (x - self.xPos) // self.nodes[0][0].size
		row = (y - self.yPos) // self.nodes[0][0].size
		return col, row

	def get_node(self, col, row):
		return self.nodes[col][row]

	def is_done(self):
		"""
		RETURNS TRUE IF ANOTHER CALL OF make_step FUNCTION WOULDN'T CHANGE ANYTHING.
		IN OTHER WORDS,
		RETURNS TRUE IF PATH HAS BEEN FOUND OR IF PATH-FINDING PROCESS HAS FAILED, BECAUSE THERE IS NO PATH BETWEEN
		START AND END NODE.

		IF FUNCTION RETURNS FALSE, IT MEANS THAT THE PATH-FINDING PROCESS WOULD STILL GOING ON (NEXT CALLING make_step
		FUNCTION WILL CHANGE SOMETHING)
		"""

		if self.endFound:
			return self.pathIsDone

		if not self.sthHappened:
			return False

		if self.algorithm == 'BFS':
			return self.algoComponents.bfs.queue.empty()
		if self.algorithm == 'DFS':
			return not self.algoComponents.dfs.stack
		if self.algorithm == 'DIJKSTRA':
			return self.algoComponents.dijkstra.priorityQueue.empty()
		if self.algorithm == 'A*':
			return self.algoComponents.aStar.openSet.empty()

	# MUTATORS:
	def safely_change_node_state(self, column, row, state):
		"""
		SIMPLY CHANGES A NODE STATE, BUT PREVENTS CHANGING STATE OF A NODE, WHICH IS START OR END
		"""

		if self.nodes[column][row].get_state() != 'START' and self.nodes[column][row].get_state() != 'END':
			self.nodes[column][row].change_state(state)
			if state == 'START':
				x, y = self.startPos
				self.nodes[x][y].change_state(None)
				self.startPos = column, row
				self.nodes[column][row].change_state('START')
			elif state == 'END':
				x, y = self.endPos
				self.nodes[x][y].change_state(None)
				self.endPos = column, row
				self.nodes[column][row].change_state('END')

	def set_algorithm(self, algorithm):
		"""
		TAKES AS THE ARGUMENT A STRING
		"""
		self.algorithm = algorithm

	def increase_weight(self, column, row, weight_gain):
		"""
		weights_gain ARGUMENT HAVE TO BE NON-NEGATIVE.

		IF NEW WEIGHT WILL BE GREATER THAN maxNodeWeight (WHICH IS THE GRAPH VARIABLE),
		THEN NEW WEIGHT WILL BE AUTOMATICALLY DECREASED TO THE VALUE OF maxNodeWeight VARIABLE.
		"""

		assert weight_gain >= 0, "ERROR: increase_weight function:\nArgument weight_gain must be non-negative\n"
		self.nodes[column][row].set_weight(
			min(self.nodes[column][row].maxWeight, self.nodes[column][row].get_weight() + weight_gain)
		)

	def decrease_weight(self, column, row, weight_loss):
		"""
		weights_loss ARGUMENT HAVE TO BE NON-NEGATIVE.

		IF NEW WEIGHT WILL BE SMALLER THAN minNodeWeight (WHICH IS THE GRAPH VARIABLE),
		THEN NEW WEIGHT WILL BE AUTOMATICALLY INCREASED TO THE VALUE OF minNodeWeight VARIABLE.
		"""

		assert weight_loss >= 0, "ERROR: decrease_weight function:\nArgument weight_gain must be non-negative\n"
		self.nodes[column][row].set_weight(
			max(self.nodes[column][row].minWeight, self.nodes[column][row].get_weight() - weight_loss)
		)

	def reset(self):
		"""
		REMOVE ALL PROGRESS IN THE PATH-FINDING PROCESS, RESTORE THE GRAPH TO ITS INITIAL STATE
		"""

		for x in self.nodes:
			for y in x:
				y.set_visited(False)
				if not y.get_state() == 'START' and not y.get_state() == 'END':
					y.change_state(None)

		self.currentlyConsideredPos = None
		self.sthHappened = False
		self.pathIsDone = False
		self.currentlyConsideredPathPos = None
		self.endFound = False

		self.algoComponents = AlgoComponents(self.columnsCount, self.rowsCount)

	def clean_all(self):
		"""
		FIRST CALLS reset FUNCTION AND THEN
		SETS ALL WEIGHTS IN THE GRAPH TO VALUE OF THE minNodeWeight VARIABLE (WHICH IS VARIABLE OF THE GRAPH)
		"""
		self.reset()
		for x in self.nodes:
			for y in x:
				y.set_weight(self.minNodeWeight)

	def make_random(self):
		"""
		CALLS clean_all FUNCTION, SETS START AND END IN A RANDOM POSITIONS AND
		SETS ALL WEIGHTS TO RANDOM VALUES FROM RANGE <minNodeWeight; maxNodeWeight>
		(minNodeWeight and maxNodeWeight are the Graph variables)
		"""

		self.clean_all()

		x, y = self.startPos
		self.nodes[x][y].change_state(None)
		x1 = random.randint(0, self.columnsCount - 1)
		y1 = random.randint(0, self.rowsCount - 1)
		self.startPos = x1, y1
		self.nodes[x1][y1].change_state('START')

		x2 = random.randint(0, self.columnsCount - 1)
		y2 = random.randint(0, self.rowsCount - 1)
		x, y = self.endPos
		self.nodes[x][y].change_state(None)
		while x1 == x2 and y1 == y2:
			x2 = random.randint(0, self.columnsCount - 1)
			y2 = random.randint(0, self.rowsCount - 1)
		self.endPos = x2, y2
		self.nodes[x2][y2].change_state('END')

		for x in self.nodes:
			for y in x:
				y.set_weight(random.randint(self.minNodeWeight, self.maxNodeWeight))
				y.set_visited(False)

	# OTHER METHODS:
	def make_step(self):
		"""
		MAKE ANOTHER STEP IN PATH-FINDING PROCESS. AFTER CALLING render FUNCTION CHANGES WILL BE VISIBLE.
		"""

		if self.endFound:
			self.make_path_step()
		elif self.algorithm == 'BFS':
			self.make_bfs_step()
		elif self.algorithm == 'DFS':
			self.make_dfs_step()
		elif self.algorithm == 'DIJKSTRA':
			self.make_dijkstra_step()
		elif self.algorithm == 'A*':
			self.make_a_star_step()

	def render(self):
		"""
		CALL THE FUNCTION AT THE END OF EVERY FRAME
		"""

		if not self.is_done():
			for x in self.nodes:
				for y in x:
					y.render_with_state()
		else:
			for x in self.nodes:
				for y in x:
					if y.state != 'START' and y.state != 'END' and y.state != 'IN_PATH':
						y.render_without_state()
					else:
						y.render_with_state()

	def save_to_file(self, file_path):
		template = open(file_path, "w")
		for y in range(int(self.rowsCount)):
			string = ""
			for x in range(int(self.columnsCount)):
				if self.nodes[x][y].get_state() == 'START':
					string += 'START '
				elif self.nodes[x][y].get_state() == "END":
					string += 'END '
				else:
					string += str(self.nodes[x][y].get_weight()) + ' '
			template.write(str(string))
			template.write('\n')
		template.close()

	def load_from_file(self, file_path):
		self.clean_all()

		x, y = self.startPos
		self.nodes[x][y].change_state(None)

		x, y = self.endPos
		self.nodes[x][y].change_state(None)

		template = open(file_path, "r")
		y = 0
		for line in template:
			x = 0
			for word in line.split():
				if word == 'START':
					self.nodes[x][y].change_state('START')
					self.startPos = x, y
				elif word == 'END':
					self.nodes[x][y].change_state('END')
					self.endPos = x, y
				else:
					self.nodes[x][y].set_weight(int(word))
				x += 1
			y += 1
		template.close()


def init_choice_boxes(graph):
	x = 2 * LEFT_MARGIN + graph.columnsCount * graph.nodes[0][0].size
	algorithm_choice_box = ChoiceBox(
		x, TOP_MARGIN, 160, 18, 12, GREY224, BLACK, ['BFS', 'DFS', 'DIJKSTRA', 'A*'], 'BFS', 'ALGORITHM:', BLACK
	)
	node_action_choice_box = ChoiceBox(
		x, 2 * TOP_MARGIN + 162, 160, 18, 12, GREY224, BLACK, ['START', 'END', 'INCREASE', 'DECREASE'], 'START',
		'NODE ACTIONS:', BLACK
	)
	on_choice_box = ChoiceBox(
		x, 3 * TOP_MARGIN + 324, 160, 18, 12, GREY224, BLACK, ['ON', 'OFF'], 'OFF', 'ON/OFF:', BLACK
	)
	return algorithm_choice_box, node_action_choice_box, on_choice_box


def init_buttons(graph):
	buttons = []
	x = 2 * LEFT_MARGIN + graph.columnsCount * graph.nodes[0][0].size + 30
	y = 4 * TOP_MARGIN + 324 + 4 * 12 + 3 * 18 + 10
	buttons.append(Button(x, y + 0 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "RESET"))
	buttons.append(Button(x, y + 1 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "CLEAN"))
	buttons.append(Button(x, y + 2 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "RANDOM"))
	buttons.append(Button(x, y + 3 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "LOAD"))
	buttons.append(Button(x, y + 4 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "SAVE"))
	buttons.append(Button(x, y + 5 * 42, 100, 32, GREY224, GREY240, GREY192, 1, BLACK, 18, "MAZE"))
	return buttons


def render_buttons_background(graph):
	pg.draw.rect(
		window, BLACK,
		(
			2 * LEFT_MARGIN + graph.columnsCount * graph.nodes[0][0].size,
			4 * TOP_MARGIN + 324 + 4 * 12 + 3 * 18,
			160,
			HEIGHT - (4 * TOP_MARGIN + 324 + 4 * 12 + 3 * 18) - TOP_MARGIN
		)
	)
	pg.draw.rect(
		window, GREY224,
		(
			2 * LEFT_MARGIN + graph.columnsCount * graph.nodes[0][0].size + 1,
			4 * TOP_MARGIN + 324 + 4 * 12 + 3 * 18 + 1,
			158,
			HEIGHT - (4 * TOP_MARGIN + 324 + 4 * 12 + 3 * 18) - TOP_MARGIN - 2
		)
	)


def main():
	clock = pg.time.Clock()
	graph = Graph(LEFT_MARGIN, TOP_MARGIN, 23, 23, 32, BLACK, 1, 1, 255, 1)

	algorithm_choice_box, node_action_choice_box, on_choice_box = init_choice_boxes(graph)
	buttons = init_buttons(graph)

	run = True
	mouse_pos = None

	# MAIN LOOP, THE ENTIRE PROGRAM RUNS HERE:
	while run:
		clock.tick(FPS)  # TO NOT EXCEED THE FRAMES PER SECOND LIMIT

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
						graph.save_to_file('Graph templates/saved.txt')
					elif text == 'LOAD':
						graph.load_from_file('Graph templates/saved.txt')
					elif text == 'MAZE':
						graph.load_from_file('Graph templates/maze.txt')
					break

		# UPDATING CHOICE BOXES:
		algorithm_choice_box.update(mouse_pos)
		node_action_choice_box.update(mouse_pos)
		on_choice_box.update(mouse_pos)

		node_action = node_action_choice_box.get_current_option()

		if algorithm_choice_box.get_state_has_changed():
			graph.set_algorithm(algorithm_choice_box.get_current_option())
			graph.reset()

		# CHANGING A NODE STATE:
		if pg.mouse.get_pressed()[0]:
			col, row = graph.get_node_coordinates(mouse_pos)
			if 0 <= col < graph.columnsCount and 0 <= row < graph.rowsCount:
				graph.reset()
				if node_action == 'START' or node_action == 'END':
					graph.safely_change_node_state(col, row, node_action)
				elif node_action == 'INCREASE':
					graph.increase_weight(col, row, 10)
				elif node_action == 'DECREASE':
					graph.decrease_weight(col, row, 10)

		# REMOVING BARRIERS USING RIGHT MOUSE BUTTON:
		if pg.mouse.get_pressed()[2]:
			col, row = graph.get_node_coordinates(mouse_pos)
			if 0 <= col < graph.columnsCount and 0 <= row < graph.rowsCount:
				graph.reset()
				if node_action == 'START':
					graph.safely_change_node_state(col, row, 'END')
				elif node_action == 'END':
					graph.safely_change_node_state(col, row, 'START')
				elif node_action == 'INCREASE':
					graph.decrease_weight(col, row, 10)
				elif node_action == 'DECREASE':
					graph.increase_weight(col, row, 10)

		# UPDATING NEIGHBORS:
		for x in range(int(graph.columnsCount)):
			for y in range(int(graph.rowsCount)):
				graph.get_node(x, y).update_neighbors(graph)

		if graph.is_done():
			on_choice_box.set_option('OFF')

		if on_choice_box.get_current_option() == 'ON':
			graph.make_step()

		# RENDERING:
		window.fill(BACKGROUND_COLOR)
		graph.render()
		render_buttons_background(graph)
		for btn in buttons:
			btn.render()
		algorithm_choice_box.render()
		node_action_choice_box.render()
		on_choice_box.render()
		pg.display.update()

	pg.quit()


if __name__ == '__main__':
	main()

print('\nCode is done, so everything works fine!')
