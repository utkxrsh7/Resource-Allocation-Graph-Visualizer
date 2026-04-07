print("STARTING TEST")

from graph_logic import ResourceAllocationGraph

rag = ResourceAllocationGraph()

rag.add_process("P1")
rag.add_resource("R1")

print("Processes:", rag.processes)
print("Resources:", rag.resources)