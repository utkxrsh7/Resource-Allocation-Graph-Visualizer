from flask import Flask, render_template, request
from graph_logic import ResourceAllocationGraph
import os

import matplotlib

# Use a non-GUI backend suitable for servers
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402

app = Flask(__name__)

rag = ResourceAllocationGraph()


def cycle_path_string(rag):
    """Human-readable closed path for circular wait, or empty string if none."""
    nodes = rag.get_cycle_nodes()
    if not nodes:
        return ""
    return " → ".join(nodes + [nodes[0]])


def cycle_edge_set(nodes):
    """Set of (u, v) directed edges for the closed walk given ordered cycle nodes."""
    if not nodes:
        return set()
    n = len(nodes)
    return {(nodes[i], nodes[(i + 1) % n]) for i in range(n)}


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        action = request.form.get("action", "request")
        if action == "reset":
            rag.reset()
        elif action == "delete_process":
            rag.remove_process(request.form.get("node", ""))
        elif action == "delete_resource":
            rag.remove_resource(request.form.get("node", ""))
        elif action == "request":
            process = request.form["process"]
            resource = request.form["resource"]
            rag.add_request(process, resource)
        elif action == "allocation":
            process = request.form["process"]
            resource = request.form["resource"]
            rag.add_allocation(resource, process)

    return render_template(
        "index.html",
        processes=list(rag.processes),
        resources=list(rag.resources),
        graph_url=None,
        cycle_path=cycle_path_string(rag),
    )


@app.route("/graph", methods=["GET"])
def show_graph():
    """Generate a PNG of the current resource allocation graph and render the home page."""
    if not os.path.exists("static"):
        os.makedirs("static", exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4))

    # Use spring layout for a simple automatic layout
    pos = nx.spring_layout(rag.graph) if rag.graph.number_of_nodes() > 0 else {}

    # Draw process nodes as circles
    process_nodes = list(rag.processes)
    if process_nodes:
        nx.draw_networkx_nodes(
            rag.graph,
            pos,
            nodelist=process_nodes,
            node_shape="o",
            node_color="#1f77b4",
            ax=ax,
        )

    # Draw resource nodes as squares
    resource_nodes = list(rag.resources)
    if resource_nodes:
        nx.draw_networkx_nodes(
            rag.graph,
            pos,
            nodelist=resource_nodes,
            node_shape="s",
            node_color="#ff7f0e",
            ax=ax,
        )

    request_edges = [
        (u, v)
        for u, v, d in rag.graph.edges(data=True)
        if d.get("kind") == "request"
    ]
    allocation_edges = [
        (u, v)
        for u, v, d in rag.graph.edges(data=True)
        if d.get("kind") == "allocation"
    ]
    on_cycle = cycle_edge_set(rag.get_cycle_nodes())

    req_normal = [e for e in request_edges if e not in on_cycle]
    req_wait = [e for e in request_edges if e in on_cycle]
    alloc_normal = [e for e in allocation_edges if e not in on_cycle]
    alloc_wait = [e for e in allocation_edges if e in on_cycle]

    if req_normal:
        nx.draw_networkx_edges(
            rag.graph,
            pos,
            edgelist=req_normal,
            edge_color="black",
            arrowstyle="->",
            arrowsize=15,
            ax=ax,
        )
    if alloc_normal:
        nx.draw_networkx_edges(
            rag.graph,
            pos,
            edgelist=alloc_normal,
            edge_color="green",
            arrowstyle="->",
            arrowsize=15,
            ax=ax,
        )
    if req_wait:
        nx.draw_networkx_edges(
            rag.graph,
            pos,
            edgelist=req_wait,
            edge_color="red",
            arrowstyle="->",
            arrowsize=15,
            ax=ax,
        )
    if alloc_wait:
        nx.draw_networkx_edges(
            rag.graph,
            pos,
            edgelist=alloc_wait,
            edge_color="red",
            arrowstyle="->",
            arrowsize=15,
            ax=ax,
        )

    # Draw labels for all nodes
    nx.draw_networkx_labels(rag.graph, pos, font_size=9, ax=ax)

    ax.set_axis_off()
    plt.tight_layout()

    output_path = os.path.join("static", "graph.png")
    plt.savefig(output_path, format="png", dpi=150)
    plt.close(fig)

    return render_template(
        "index.html",
        processes=list(rag.processes),
        resources=list(rag.resources),
        graph_url="/static/graph.png",
        cycle_path=cycle_path_string(rag),
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
