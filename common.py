from graph import Graph, Node
from turing_machine import TuringMachine
from typing import Callable

def binary_string(n: int, bits: int) -> str:
    return ''.join([str((n >> k) & 1) for k in range(bits-1, -1, -1)])

class Randomizer(Graph):
    def __init__(self, random_bits: int):
        super().__init__(False)
        num_layers = random_bits + 1
        nodes_per_layer = 2 ** num_layers
        
        self.layers: list[dict[str, Node]] = [None] * num_layers

        rand_strings = [binary_string(n, num_layers) for n in range(nodes_per_layer)]

        for layer in range(0, num_layers):
            current_layer = {bstr: self.add_node('randomizer', {'layer': layer, 'bits': bstr}) for bstr in rand_strings}
            self.layers[layer] = current_layer
            if layer == 0:
                continue
            prev_layer = self.layers[layer - 1]
            bit_to_change = layer - 1
            for bstr, node in current_layer.items():
                self.add_edge(node, prev_layer[bstr])
                # flip the bit
                bstr = bstr[:bit_to_change] + str(1 - int(bstr[bit_to_change])) + bstr[bit_to_change + 1:]
                self.add_edge(node, prev_layer[bstr])

def tape_string(tape: dict) -> str:
    return ''.join([value for key, value in sorted(tape.items(), key = lambda x: x[0])])

def tm_to_graph(tm: TuringMachine) -> tuple[Graph, Node, Node]:
    graph = Graph()
    initial = graph.add_node('computation', {'tape': tape_string(tm.tape), 'head': tm.head_loc, 'state': tm.state})
    previous = initial
    while True:
        if tm.forward(): # when halted
            break
        current = graph.add_node('computation', {'tape': tape_string(tm.tape), 'head': tm.head_loc, 'state': tm.state})
        graph.add_edge(previous, current)
        previous = current
    previous.type = "output"
    return graph, initial, previous

def computation_and_hold_output(tm: TuringMachine, comp_length_to_output_length: Callable[[int],int]):
    comp_graph, start, output = tm_to_graph(tm)
    output_section_length = comp_length_to_output_length(len(comp_graph.adj_list) - 1)
    output.data["counter"] = 0
    prev = output
    for counter in range(1, output_section_length):
        node = comp_graph.add_node('output', {**output.data, "counter": counter})
        comp_graph.add_edge(node, prev)
        prev = node
    return comp_graph, start, prev

def resize_list(x: list, size: int, default = lambda: None):
    while len(x) < size:
        x.append(default())

class HalfHourglass(Graph):
    def __init__(self, randomizer: Randomizer, computation: TuringMachine, half: str, comp_length_to_output_length: Callable[[int],int]):
        super().__init__(False)
        self.union(randomizer)

        self.layers: list[list[Node]] = [list(randomizer_layer.values()) for randomizer_layer in randomizer.layers]
        randomizer_layer_index = -1
        if half == 'bottom':
            randomizer_layer_index = 0
            self.layers = list(reversed(self.layers))
        random_layer = list(randomizer.layers[randomizer_layer_index].items())

        random_layer_consecutive_pairs = [(bstr[:-1], node1, node2) for (bstr, node1), (_, node2) \
                                           in zip(random_layer[::2], random_layer[1::2])]
        
        for bstr, random_node_one, random_node_two in random_layer_consecutive_pairs:
            random_tape = {i: c for i, c in enumerate(bstr)}

            tm_one = TuringMachine(computation.rules, random_tape, computation.state)
            comp_output_graph_one, comp_one_start, _ = computation_and_hold_output(tm_one, comp_length_to_output_length)
            resize_list(self.layers, len(randomizer.layers) + len(comp_output_graph_one.adj_list), lambda: [])
            for i, node in enumerate(comp_output_graph_one.adj_list):
                node.name = f"comp{bstr}_track0_{node.name}"
                if half is not None:
                    node.data["half"] = half
                node.data["randomness"] = bstr
                self.layers[len(randomizer.layers) + i].append(node)
            self.union(comp_output_graph_one)
            self.add_edge(random_node_one, comp_one_start)
            self.add_edge(random_node_two, comp_one_start)

            tm_two = TuringMachine(computation.rules, random_tape, computation.state)
            comp_output_graph_two, comp_two_start, _ = computation_and_hold_output(tm_two, comp_length_to_output_length)
            for i, node in enumerate(comp_output_graph_two.adj_list):
                node.name = f"comp{bstr}_track1_{node.name}"
                if half is not None:
                    node.data["half"] = half
                node.data["randomness"] = bstr
                self.layers[len(randomizer.layers) + i].append(node)
            self.union(comp_output_graph_two)
            self.add_edge(random_node_one, comp_two_start)
            self.add_edge(random_node_two, comp_two_start)

            ### STITCH THE TWO COMPUTATIONS TOGETHER
            node_list_one = list(comp_output_graph_one.adj_list)
            for i, node in enumerate(comp_output_graph_two.adj_list):
                if i > 0:
                    self.add_edge(node, node_list_one[i - 1])
                if i < len(node_list_one) - 1:
                    self.add_edge(node, node_list_one[i + 1])