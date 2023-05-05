from graph import Graph, tm_to_graph
from turing_machine import TuringMachine

def binary_string(n: int, bits: int) -> str:
    return ''.join([str((n >> k) & 1) for k in range(bits-1, -1, -1)])

class HalfHourglass(Graph):
    def __init__(self, random_bits: int, computation: TuringMachine, half = 'top'):
        super().__init__(False)

        # RAND GEN
        nodes_per_layer = 2 ** random_bits

        self.core_layer = [self.add_node('rand_gen', {"randomness": '0',"battery": i, "half": half}) for i in range(nodes_per_layer)]

        prev_layer = self.core_layer
        for i in range(1, random_bits + 1):
            current_layer = []
            for randomness in range(2 ** i):
                for battery in range(2 ** (random_bits - i)):
                    node = self.add_node('rand_gen', {"randomness": binary_string(randomness, i), \
                                                      "battery": binary_string(battery, random_bits - i), "half": half})

                    last_battery = battery * 2
                    last_randomness = randomness // 2

                    left_parent_idx = last_randomness * (2 ** (random_bits - i + 1)) + last_battery
                    right_parent_idx = left_parent_idx + 1

                    self.add_edge(node, prev_layer[left_parent_idx])
                    self.add_edge(node, prev_layer[right_parent_idx])

                    current_layer.append(node)
            prev_layer = current_layer
        
        # COMPUTATION + HOLD OUTPUT
        for randomness in range(nodes_per_layer):
            prev = prev_layer[randomness]
            randomness = prev.data['randomness']
            random_tape = {i: c for i, c in enumerate(randomness)}
            tm = TuringMachine(computation.rules, random_tape, computation.state, computation.head_loc)
            comp_graph, start, end = tm_to_graph(tm)
            for node in comp_graph.adj_list:
                node.data["half"] = half
                node.data["randomness"] = randomness
            comp_length = len(comp_graph.adj_list)
            self.union(comp_graph)
            self.add_edge(prev, start)
            prev = end
            for counter in range(comp_length):
                node = self.add_node('hold_output', {"counter": counter, "output": end.data['tape'], "half": half, "randomness": randomness})
                self.add_edge(node, prev)
                prev = node

class Hourglass(HalfHourglass):
    def __init__(self, random_bits: int, computation: TuringMachine):
        super().__init__(random_bits, computation)
        bottom_half = HalfHourglass(random_bits, computation, 'bottom')
        for node in bottom_half.adj_list:
            node.name = str(int(node.name) + len(self.adj_list))
        self.union(bottom_half)
        for core_index in range(len(self.core_layer)):
            self.add_edge(self.core_layer[core_index], bottom_half.core_layer[core_index])