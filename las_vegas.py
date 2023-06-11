from graph import Graph, tm_to_graph
from turing_machine import TuringMachine

def binary_string(n: int, bits: int) -> str:
    return ''.join([str((n >> k) & 1) for k in range(bits-1, -1, -1)])

class Randomizer(Graph):
    def __init__(self, random_bits: int):
        super().__init__(False)
        self.outer_layers = {}
        self.num_layers = random_bits + 1
        self.nodes_per_layer = 2 ** random_bits

        rand_strings = [binary_string(n, random_bits) for n in range(self.nodes_per_layer)]
        self.outer_layers["bottom"] = {bstr: self.add_node('randomizer', {'layer': 0, 'bits': bstr}) for bstr in rand_strings}

        prev_layer = self.outer_layers["bottom"]
        for layer in range(1, self.num_layers):
            current_layer = {bstr: self.add_node('randomizer', {'layer': layer, 'bits': bstr}) for bstr in rand_strings}
            bit_to_change = layer - 1
            for bstr, node in current_layer.items():
                self.add_edge(node, prev_layer[bstr])
                # flip the bit
                bstr = bstr[:bit_to_change] + str(1 - int(bstr[bit_to_change])) + bstr[bit_to_change + 1:]
                self.add_edge(node, prev_layer[bstr])
            prev_layer = current_layer
        
        self.outer_layers["top"] = current_layer

class HalfHourglass(Graph):
    def __init__(self, randomizer: Randomizer, computation: TuringMachine, half = 'top'):
        super().__init__(False)
        self.union(randomizer)

        random_layer = randomizer.outer_layers[half]
        
        # COMPUTATION + HOLD OUTPUT
        for bstr, random_node in random_layer.items():
            random_tape = {i: c for i, c in enumerate(bstr)}

            tm_one = TuringMachine(computation.rules, random_tape, computation.state, computation.head_loc)
            comp_graph_one, start, end = tm_to_graph(tm_one)
            node_list_one = list(comp_graph_one.adj_list.keys())
            for node in comp_graph_one.adj_list:
                node.name = "comp_" + bstr + "_one_" + node.name
                node.data["half"] = half
                node.data["randomness"] = bstr
            self.union(comp_graph_one)
            self.add_edge(random_node, start)
            output_length = len(comp_graph_one.adj_list) * 2 + randomizer.num_layers
            prev = end
            for counter in range(output_length):
                node = self.add_node('hold_output', {"counter": counter, "output": end.data['tape'], "half": half, "randomness": bstr})
                self.add_edge(node, prev)
                prev = node

            tm_two = TuringMachine(computation.rules, random_tape, computation.state, computation.head_loc)
            comp_graph_two, start, end = tm_to_graph(tm_two)
            for node in comp_graph_two.adj_list:
                node.name = "comp_" + bstr + "_two_" + node.name
                node.data["half"] = half
                node.data["randomness"] = bstr
            node_list_two = list(comp_graph_two.adj_list.keys())
            self.union(comp_graph_two)
            ### STITCH THE TWO COMPUTATIONS TOGETHER
            for i, node in enumerate(node_list_two):
                if i > 0:
                    self.add_edge(node, node_list_one[i - 1])
                if i < len(node_list_one) - 1:
                    self.add_edge(node, node_list_one[i + 1])
            self.add_edge(random_node, start)
            output_length = len(comp_graph_two.adj_list) * 2 + randomizer.num_layers
            prev = end
            for counter in range(output_length):
                node = self.add_node('hold_output', {"counter": counter, "output": end.data['tape'], "half": half, "randomness": bstr})
                self.add_edge(node, prev)
                prev = node

class Hourglass(Graph):
    def __init__(self, random_bits: int, computation: TuringMachine):
        super().__init__(False)

        randomizer = Randomizer(random_bits)
        for node in randomizer.adj_list:
            node.name = "rand_" + node.name

        top_half = HalfHourglass(randomizer, computation, 'top')
        bottom_half = HalfHourglass(randomizer, computation, 'bottom')
        for node in top_half.adj_list:
            if node.type != 'randomizer':
                node.name = "top_" + node.name
        for node in bottom_half.adj_list:
            if node.type != 'randomizer':
                node.name = "bottom_" + node.name

        self.union(top_half)
        self.union(bottom_half)