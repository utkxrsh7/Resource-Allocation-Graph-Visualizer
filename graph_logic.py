"""Resource allocation graph data structures (processes, resources, directed edges)."""

import networkx as nx


class ResourceAllocationGraph:
    """
    A directed resource-allocation graph: processes may request resources;
    resources may be allocated to processes. Uses one node per name; a name
    cannot be both a process and a resource.
    """

    def __init__(self):
        # Directed edges model requests (process → resource) and allocations (resource → process).
        self.graph = nx.DiGraph()
        # Names of process nodes (subset of graph nodes).
        self.processes = set()
        # Names of resource nodes (subset of graph nodes).
        self.resources = set()

    def add_process(self, name):
        """Register a process and add it as a node in the graph."""
        if name in self.resources:
            raise ValueError(f"{name!r} is already a resource; use distinct names.")
        if name in self.processes:
            return
        self.processes.add(name)
        self.graph.add_node(name, kind="process")

    def add_resource(self, name):
        """Register a resource and add it as a node in the graph."""
        if name in self.processes:
            raise ValueError(f"{name!r} is already a process; use distinct names.")
        if name in self.resources:
            return
        self.resources.add(name)
        self.graph.add_node(name, kind="resource")
