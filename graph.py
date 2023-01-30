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

    def union(self, other: 'Graph') -> 'Graph':
        self.adj_list |= other.adj_list
        return self
        
    def __str__(self) -> str:
        output = []
        for node, neighbors in self.adj_list.items():
            output.append(str(node) + " -> " + ", ".join([neighbor.name for neighbor in neighbors]))
        return "\n".join(output)