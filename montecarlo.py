from graph import *
from common import *
from randomwalk import RandomWalk
from turing_machine import *
from itertools import product
import random

def comp_length_to_output_length_converter(random_bits: int):
    converter: Callable[[int],int] = lambda comp_length: comp_length + random_bits + 1
    return converter

class MonteCarloSampler(Graph):
    def __init__(self, random_bits: int, computation: TuringMachine):
        super().__init__(directed = False)
        
        top_randomizer = Randomizer(random_bits)
        for node in top_randomizer.adj_list:
            node.name = "rand_" + node.name
            
        bottom_randomizer = Randomizer(random_bits)
        for node in bottom_randomizer.adj_list:
            node.name = "rand_" + node.name
        
        comp_length_to_output_length = comp_length_to_output_length_converter(random_bits)

        top_half = HalfHourglass(top_randomizer, computation, None, comp_length_to_output_length)
        for node in top_half.adj_list:
            node.name = "top_" + node.name
        bottom_half = HalfHourglass(bottom_randomizer, computation, None, comp_length_to_output_length)
        for node in bottom_half.adj_list:
            node.name = "bottom_" + node.name

        top_layers = top_half.layers
        bottom_layers = list(reversed(bottom_half.layers))

        self.layers: list[list[Node]] = [[] for _ in top_layers] # the pattern [[]] * len(top_layers) doesn't work here. try it in REPL to see why
        
        for i, layer in enumerate(self.layers):
            for top_node, bottom_node in product(top_layers[i], bottom_layers[i]):
                node = self.add_node(top_node.type + "_" + bottom_node.type, {"top": top_node, "bottom": bottom_node})
                node.top_component = top_node
                node.bottom_component = bottom_node
                node.name = top_node.name + "_" + bottom_node.name
                layer.append(node)
                if i == 0: continue
                top_neighbors = set(top_half.adj_list[top_node])
                bottom_neighbors = set(bottom_half.adj_list[bottom_node])
                
                for potential_neighbor in self.layers[i - 1]:
                    if potential_neighbor.top_component in top_neighbors and potential_neighbor.bottom_component in bottom_neighbors:
                        self.add_edge(potential_neighbor, node)

class MonteCarloRandomWalk(RandomWalk):
    def __init__(self, monte_carlo:MonteCarloSampler, random_seed = None):
        super().__init__(monte_carlo, random.choice(list(monte_carlo.adj_list)), random_seed)
        self.top_reset = self.bottom_reset = True

    def step(self):
        super().step()
        top_node = self.current_node.data["top"]
        bottom_node = self.current_node.data["bottom"]
        if top_node.type == "randomizer" and top_node.data["layer"] == 0:
            self.top_reset = True
        elif bottom_node.type == "randomizer" and bottom_node.data["layer"] == 0:
            self.bottom_reset = True
        
    def observe(self) -> tuple[bool, Node]:
        outputting_half, _ = outputting_half_of_monte_carlo_node(self.current_node)
        outputting_half_was_reset = None
        if outputting_half == "top":
            outputting_half_was_reset = self.top_reset
            self.top_reset = False
        elif outputting_half == "bottom":
            outputting_half_was_reset = self.bottom_reset
            self.bottom_reset = False
        return outputting_half_was_reset, self.current_node

def outputting_half_of_monte_carlo_node(node: Node) -> tuple[str, Node]:
    top_type = node.data["top"].type
    bottom_type = node.data["bottom"].type
    match (top_type, bottom_type):
        case ("randomizer" | "computation", "output"):
            return "bottom", node.data["bottom"]
        case ("output", "randomizer" | "computation"):
            return "top", node.data["top"]
        case _:
            raise Exception("Monte Carlo node in invalid top/bottom state")
        
