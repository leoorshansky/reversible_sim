from graph import *
import random

class RandomWalk:
    def __init__(self, graph: Graph, start: Node, random_seed = None):
        self.graph = graph
        self.current_node = start
        self.random = random.Random(random_seed)
        self.time = 0

    def step(self) -> Node:
        neighbors = self.graph.adj_list[self.current_node]
        self.current_node = self.random.choice(neighbors + [self.current_node])
        self.time += 1
        return self.current_node