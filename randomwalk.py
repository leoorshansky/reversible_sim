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
        hop = {neighbor: random.expovariate(1) for neighbor in neighbors}
        self.current_node = min(neighbors, key=lambda n: hop[n])
        self.time += min(hop.values())
        return self.current_node
    
    def run_for_time(self, time: float) -> Node:
        start = self.time
        while self.time <= start + time:
            self.step()
        return self.current_node