from turing_machine import TuringMachine, tape_string
import numpy as np

class Node:
    def __init__(self, graph: 'Graph', node_type: str, data: dict = None, name: str = None):
        self.graph = graph
        self.name = name or str(len(self.graph.adj_list))
        self.type = node_type
        self.data = data

    def __str__(self) -> str:
        return self.name + " " + self.type + (" " + str(self.data) if self.data else "")

class Graph:
    def __init__(self, directed = False):
        self.adj_list: dict[Node, list[Node]] = {}
        self.directed = directed
    
    def add_edge(self, node1: Node, node2: Node):
        self.adj_list[node1].append(node2)
        if not self.directed:
            self.adj_list[node2].append(node1)
    
    def add_node(self, node_type: str, node_data: dict = None) -> Node:
        node = Node(self, node_type, node_data)
        self.adj_list[node] = []
        return node

    def union(self, other: 'Graph'):
        self.adj_list |= other.adj_list
        
    def __str__(self) -> str:
        output = []
        for node, neighbors in self.adj_list.items():
            output.append(str(node) + " -> " + ", ".join([neighbor.name for neighbor in neighbors]))
        return "\n".join(output)
    
    def weighted_adj_matrix(self) -> tuple[list[Node], dict[Node, int], np.ndarray]:
        nodes = list(self.adj_list.keys())
        node_idxs = {node: i for i, node in enumerate(nodes)}

        mat = np.eye(len(self.adj_list))
        for node, neighbors in self.adj_list.items():
            denom = len(neighbors) + 1
            i = node_idxs[node]
            mat[i, i] /= denom
            for neighbor in neighbors:
                j = node_idxs[neighbor]
                mat[i, j] = 1/denom
        return nodes, node_idxs, mat
    
    def markov_matrix_n_steps(self, n: int) -> tuple[list[Node], dict[Node, int], np.ndarray]:
        nodes, node_idxs, mat = self.weighted_adj_matrix()
        return nodes, node_idxs, np.linalg.matrix_power(mat, n)
    
    def distribution_n_steps(self, start: Node, n: int) -> tuple[list[Node], dict[Node, int], np.ndarray]:
        nodes, node_idxs, mat = self.markov_matrix_n_steps(n)
        initial_state = np.zeros((1, len(nodes)))
        initial_state[node_idxs[start]] = 1
        return initial_state @ mat
    
    def stationary_distribution(self) -> tuple[list[Node], dict[Node, int], np.ndarray]:
        nodes, node_idxs, mat = self.weighted_adj_matrix()
        S, U = np.linalg.eig(mat.T)
        return nodes, node_idxs, (U[:,np.isclose(S, 1)][:,0] / U[:,np.isclose(S, 1)][:,0].sum()).real
    
    def describe_stationary_distribution(self) -> dict[str, float]:
        nodes, _, mat = self.stationary_distribution()
        types = {}
        for i, node in enumerate(nodes):
            prob = types.setdefault(node.type, 0)
            types[node.type] = prob + mat[i]
        return types
    
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
    return graph, initial, previous