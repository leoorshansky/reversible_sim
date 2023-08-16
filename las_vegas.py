from graph import Graph, Node
from turing_machine import TuringMachine
from common import Randomizer, HalfHourglass
from typing import Callable
from randomwalk import RandomWalk
import random

def comp_length_to_output_length_converter(random_bits: int):
    converter: Callable[[int],int] = lambda comp_length: comp_length * 2 + random_bits + 1
    return converter
class LasVegasSampler(Graph):
    def __init__(self, random_bits: int, computation: TuringMachine):
        super().__init__(directed = False)

        randomizer = Randomizer(random_bits)
        for node in randomizer.adj_list:
            node.name = "rand_" + node.name
            
        comp_length_to_output_length = comp_length_to_output_length_converter(random_bits)

        top_half = HalfHourglass(randomizer, computation, 'top', comp_length_to_output_length)
        for node in top_half.adj_list:
            if node.type != 'randomizer':
                node.name = "top_" + node.name
        bottom_half = HalfHourglass(randomizer, computation, 'bottom', comp_length_to_output_length)
        for node in bottom_half.adj_list:
            if node.type != 'randomizer':
                node.name = "bottom_" + node.name

        self.union(top_half)
        self.union(bottom_half)

class LasVegasRandomWalk(RandomWalk):
    def __init__(self, model:LasVegasSampler, random_seed = None):
        super().__init__(model, random.choice([node for node in model.adj_list if "half" in node.data]), random_seed)
        self.half = self.current_node.data["half"]

    def observe(self) -> tuple[bool, Node]:
        ready = False
        if self.current_node.type == "output" and self.current_node.data["half"] != self.half:
            ready = True
            self.half = self.current_node.data["half"]
        return ready, self.current_node