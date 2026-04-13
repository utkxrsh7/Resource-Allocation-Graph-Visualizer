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


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        process = request.form["process"]
        resource = request.form["resource"]
        action = request.form.get("action", "request")
        if action == "request":
            rag.add_request(process, resource)
        elif action == "allocation":
            rag.add_allocation(resource, process)

    return render_template(
        "index.html",
        processes=list(rag.processes),
        resources=list(rag.resources),
        graph_url=None,
        deadlock=rag.detect_deadlock(),
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
    if request_edges:
        nx.draw_networkx_edges(
            rag.graph,
            pos,
            edgelist=request_edges,
            edge_color="black",
            arrowstyle="->",
            arrowsize=15,
            ax=ax,
        )
    if allocation_edges:
        nx.draw_networkx_edges(
            rag.graph,
            pos,
            edgelist=allocation_edges,
            edge_color="green",
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
        deadlock=rag.detect_deadlock(),
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
