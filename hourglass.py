from graph import *

class HalfHourglass(Graph):
    def __init__(self, random_bits: int, comp_length: int):
        super().__init__(False)

        # RAND GEN
        nodes_per_layer = 2 ** random_bits

        self.core_layer = [self.add_node('rand_gen', {"randomness": 0,"battery": i}) for i in range(nodes_per_layer)]

        prev_layer = self.core_layer
        for i in range(1, random_bits + 1):
            current_layer = []
            for randomness in range(2 ** i):
                for battery in range(2 ** (random_bits - i)):
                    node = self.add_node('rand_gen', {"randomness": randomness, "battery": battery})

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
            for counter in range(comp_length):
                node = self.add_node('computation', {"counter": counter})
                self.add_edge(node, prev)
                prev = node
            for counter in range(comp_length):
                node = self.add_node('hold_output', {"counter": counter})
                self.add_edge(node, prev)
                prev = node

class Hourglass(HalfHourglass):
    def __init__(self, random_bits: int, comp_length: int):
        super().__init__(random_bits, comp_length)
        bottom_half = HalfHourglass(random_bits, comp_length)
        for node in bottom_half.adj_list:
            node.name = str(int(node.name) + len(self.adj_list))
        self = self.union(bottom_half)
        for core_index in range(len(self.core_layer)):
            self.add_edge(self.core_layer[core_index], bottom_half.core_layer[core_index])