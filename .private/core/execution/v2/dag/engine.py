class DAG:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, name, value=None):
        if name in self.nodes:
            raise ValueError(f"Node already exists: {name}")
        self.nodes[name] = value
        self.edges.setdefault(name, set())
        return name

    def add_edge(self, source, target):
        if source not in self.nodes or target not in self.nodes:
            raise KeyError("Both DAG nodes must exist before adding an edge")
        self.edges.setdefault(source, set()).add(target)

    def topological_order(self):
        indegree = {node: 0 for node in self.nodes}

        for source, targets in self.edges.items():
            for target in targets:
                indegree[target] += 1

        queue = [node for node, degree in indegree.items() if degree == 0]
        order = []

        while queue:
            node = queue.pop(0)
            order.append(node)

            for target in self.edges.get(node, set()):
                indegree[target] -= 1
                if indegree[target] == 0:
                    queue.append(target)

        if len(order) != len(self.nodes):
            raise ValueError("DAG contains a cycle")

        return order


class DAGEngine:
    def __init__(self, dag=None):
        self.dag = dag or DAG()

    def execute(self):
        return self.dag.topological_order()
