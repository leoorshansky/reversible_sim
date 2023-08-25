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
        if self.directed != other.directed:
            raise Exception("cannot take the union of a directed and an undirected graph")
        for node in self.adj_list:
            neighbors = set(self.adj_list.get(node, [])) | set(other.adj_list.get(node, []))
            self.adj_list[node] = list(neighbors)
        for node in other.adj_list:
            if node not in self.adj_list:
                self.adj_list[node] = other.adj_list[node]
        
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
    
    def to_graphviz_layered(self, clusterings:list[tuple[str, list[int]]] = []) -> str:
        output = 'graph G {\nrankdir="LR";\n'
        layers_graphed = set()
        node_num = 0
        cluster_num = 0
        for cluster_name, cluster_layers in clusterings:
            output += f'  subgraph cluster_{cluster_num} {{\nlabel="{cluster_name}";\n'
            cluster_num += 1
            for layer in cluster_layers:
                layers_graphed.add(layer)
                output += f'    subgraph cluster_{cluster_num} {{\n'
                output += '    label="";\n'
                cluster_num += 1
                for node in self.layers[layer]:
                    node.in_graph_num = node_num
                    output += f'      {node.in_graph_num} [tooltip="{node.name}"];\n'
                    node_num += 1
                output += '    }\n'
            output += '  }\n'
        for i, layer in enumerate(self.layers):
            if i not in layers_graphed:
                output += f'  subgraph cluster_{cluster_num} {{\n'
                cluster_num += 1
                for node in layer:
                    node.in_graph_num = node_num
                    output += f'    {node.in_graph_num} [tooltip="{node.name}"];\n'
                    node_num += 1
                output += '  }\n'
        for node, neighbors in self.adj_list.items():
            for neighbor in neighbors:
                if node.name < neighbor.name:
                    output += f'  {node.in_graph_num} -- {neighbor.in_graph_num};\n'
        output += '}\n'
        return output
