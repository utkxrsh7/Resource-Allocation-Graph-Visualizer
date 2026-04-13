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

    def add_request(self, process, resource):
        """Add a request edge process → resource between existing or new nodes."""
        # Ensure both endpoints exist with the correct types
        self.add_process(process)
        self.add_resource(resource)
        # Directed edge from process to resource models a request
        self.graph.add_edge(process, resource, kind="request")

    def add_allocation(self, resource, process):
        """Add an allocation edge resource → process between existing or new nodes."""
        self.add_resource(resource)
        self.add_process(process)
        self.graph.add_edge(resource, process, kind="allocation")

    def detect_deadlock(self):
        """Return True if the directed graph has a cycle (deadlock), else False."""
        if self.graph.number_of_nodes() == 0:
            return False
        return not nx.is_directed_acyclic_graph(self.graph)
