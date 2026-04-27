import json
import os


class Graph:
    def __init__(self):
        self.adj_list: list[int] = []
        self.edge_list: dict[int, list[tuple[int, int]]] = {}
        self.edge_count = 0
        self.node_count = 0

    def has_duplicate_edge_weights(self) -> bool:
        """Return True when any positive edge weight appears more than once."""
        if not all(i > 0  for i in self.adj_list):
            return True
        seen: set[int] = set()
        for u, neighbors in self.edge_list.items():
            for v, weight in neighbors:
                if v < u or weight <= 0:
                    continue
                if weight in seen:
                    return True
                seen.add(weight)
        return False

    def add_node(self, node_value: int = 0):
        """Add a node to the graph."""
        node_idx = len(self.adj_list)
        self.adj_list.append(node_value)
        self.edge_list[node_idx] = []
        self.node_count += 1

    def add_edge(self, u: int, v: int, weight: int = 0):
        """Add an edge to the graph."""
        self.edge_list[u].append((v, weight))
        self.edge_list[v].append((u, weight))
        self.edge_count += 1

    def set_node(self, node_idx: int, node_value: int = 0):
        """Set a node in the graph."""
        self.adj_list[node_idx] = node_value
        for index, (neighbor, weight) in enumerate(self.edge_list[node_idx]):
            if self.adj_list[neighbor] > 0:
                self.edge_list[node_idx][index] = (neighbor, node_value + self.adj_list[neighbor])
                for neighbor_index, (neighbor_neighbor, neighbor_weight) in enumerate(self.edge_list[neighbor]):
                    if neighbor_neighbor == node_idx:
                        self.edge_list[neighbor][neighbor_index] = (node_idx, node_value + self.adj_list[neighbor])
                        break

    def clear_graph(self):
        """clear all nodes and edges in the graph."""
        for idx in range(len(self.adj_list)):
            self.adj_list[idx] = 0
            for edge_idx, (neighbor, weight) in enumerate(self.edge_list[idx]):
                self.edge_list[idx][edge_idx] = (neighbor, 0)

def create_lobster_graph(graph: Graph, n: int, p: int):
    """Create a lobster graph."""
    node_total = (2 * p + 1) * n
    for idx in range(node_total):
        graph.add_node(0)
    for idx in range(node_total):
        if idx % (2 * p + 1) == 0:
            graph.add_edge(idx, idx + 1)
            graph.add_edge(idx, idx + p + 1)
            if idx < (2 * p + 1) * (n - 1):
                graph.add_edge(idx, idx + 2 * p + 1)
        elif idx % (2 * p + 1) == 1 or idx % (2 * p + 1) == p + 1:
            for p_idx in range(1, p):
                graph.add_edge(idx, idx + p_idx)

def middle_node_value(n: int, p: int, idx: int) -> int:
    node_section_size = 2 * p + 1
    curr_section = idx // node_section_size + 1
    if curr_section % 2 == 0:
        return (node_section_size * curr_section) // 2
    else:
        if curr_section < n:
            return (node_section_size * curr_section - (2 * p - 1)) // 2
        else:
            return ((node_section_size * curr_section) + 1) // 2

def upper_node_value(n: int, p: int, idx: int) -> int:
    node_section_size = 2 * p + 1
    curr_section = idx // node_section_size + 1
    if curr_section % 2 == 0:
        return (node_section_size * curr_section) // 2 - p
    else:
        if curr_section < n:
            return (node_section_size * curr_section - 1) // 2
        else:
            return (node_section_size * (curr_section - 1) - 2) // 2

def lower_node_value(n: int, p: int, idx: int) -> int:
    node_section_size = 2 * p + 1
    curr_section = idx // node_section_size + 1
    if curr_section % 2 == 0:
        return (node_section_size * curr_section) // 2
    else:
        if curr_section < n:
            return (node_section_size * (curr_section + 1) - 2) // 2
        else:
            return (node_section_size * curr_section - 1) // 2

def circle_node_value(n: int, p: int, idx: int) -> int:
    node_section_size = 2 * p + 1
    curr_section = idx // node_section_size + 1
    if idx % node_section_size <= p:
        j = idx - node_section_size * (curr_section - 1) - 1
    else:
        j = idx - node_section_size * (curr_section - 1) - (p + 1)
    if curr_section < n:
        if curr_section % 2 == 0:
            return (node_section_size * curr_section) // 2 - p + j
        else:
            return (node_section_size * (curr_section - 1)) // 2 - p + 1 + j
    else:
        if curr_section % 2 == 0:
            return (node_section_size * curr_section) // 2 + j
        else:
            return (node_section_size * (curr_section - 1)) // 2 + 1 + j

def add_k_labeling(graph: Graph, n: int, p: int):
    node_section_size = 2 * p + 1
    node_total = node_section_size * n
    """Add k labeling to the lobster graph."""
    graph.set_node(0, 1)
    for idx in range(1, p + 1):
        graph.set_node(idx, idx)
        graph.set_node(idx + p, idx)
    graph.set_node(p + 1, p + 1)
    for idx in range(node_section_size, node_total):
        if idx % node_section_size == 0:
            node_value = middle_node_value(n, p, idx)
        elif idx % node_section_size == 1:
            node_value = upper_node_value(n, p, idx)
        elif idx % node_section_size == p + 1:
            node_value = lower_node_value(n, p, idx)
        else:
            node_value = circle_node_value(n, p, idx)
        graph.set_node(idx, node_value)


def save_graph(graph: Graph, path: str) -> None:
    """Save graph to JSON (.json) or edges CSV (.csv)."""
    try:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("u,v,weight\n")
                seen = set()
                for u in sorted(graph.edge_list):
                    for v, weight in graph.edge_list[u]:
                        edge = (u, v) if u < v else (v, u)
                        if edge in seen:
                            continue
                        seen.add(edge)
                        fh.write(f"{edge[0]},{edge[1]},{weight}\n")
        else:
            payload = {"adj_list": graph.adj_list, "edge_list": {str(k): v for k, v in graph.edge_list.items()}}
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
        print(f"Graph saved to {path}")
    except Exception as e:
        print(f"Failed to save graph to {path}: {e}")

def plot_lobster_graph(
    graph: Graph,
    n: int,
    p: int,
    show_labels: bool = True,
    show_weights: bool = True,
    save_path: str | None = None,
    show: bool = True,
) -> None:
    """Plot a generated lobster graph using a symmetric spine-and-branches layout."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed. Run: pip install matplotlib")
        return

    block_size = 2 * p + 1
    leaf_count = max(0, p - 1)
    leaf_dx = 0.9
    root_y = 1.8
    leaf_y = 1.4
    min_spine_gap = 4.4
    spread_width = max(0.0, (leaf_count - 1) * leaf_dx)
    spine_gap = max(min_spine_gap, spread_width + 2.4)

    positions = {}
    for segment in range(n):
        base = segment * block_size
        spine_x = segment * spine_gap

        # Spine node in each segment.
        positions[base] = (spine_x, 0.0)

        top_root = base + 1
        bottom_root = base + p + 1
        if top_root < graph.node_count:
            positions[top_root] = (spine_x, root_y)
        if bottom_root < graph.node_count:
            positions[bottom_root] = (spine_x, -root_y)

        # Leaves are centered around each segment to keep the lobster symmetric.
        center_shift = (leaf_count - 1) / 2.0
        for leaf_idx in range(1, p):
            top_leaf = top_root + leaf_idx
            bottom_leaf = bottom_root + leaf_idx
            x_offset = (leaf_idx - 1 - center_shift) * leaf_dx
            if top_leaf < graph.node_count:
                positions[top_leaf] = (spine_x + x_offset, root_y + leaf_y)
            if bottom_leaf < graph.node_count:
                positions[bottom_leaf] = (spine_x + x_offset, -root_y - leaf_y)

    fig, ax = plt.subplots(figsize=(max(9, n * 2.2), 7))

    drawn_edges = set()
    for u, neighbors in graph.edge_list.items():
        for v, weight in neighbors:
            edge = (u, v) if u < v else (v, u)
            if edge in drawn_edges:
                continue
            drawn_edges.add(edge)

            x1, y1 = positions[u]
            x2, y2 = positions[v]
            ax.plot([x1, x2], [y1, y2], color="#4c566a", linewidth=1.6, zorder=1)

            if show_weights:
                ax.text((x1 + x2) / 2, (y1 + y2) / 2, str(weight), fontsize=8, color="#5e81ac")

    xs = []
    ys = []
    for node, (x, y) in positions.items():
        xs.append(x)
        ys.append(y)
        ax.scatter(x, y, s=260, color="#ebcb8b", edgecolors="#2e3440", linewidth=1.4, zorder=3)
        if show_labels:
            ax.text(x, y, str(graph.adj_list[node]), ha="center", va="center", fontsize=8, color="#2e3440", zorder=4)

    ax.set_title(f"Lobster Graph (n={n}, p={p})")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(min(xs) - 1.2, max(xs) + 1.2)
    ax.set_ylim(min(ys) - 1.2, max(ys) + 1.2)
    ax.axis("off")

    if save_path:
        try:
            fig.savefig(save_path, dpi=200, bbox_inches="tight")
            print(f"Plot saved to {save_path}")
        except Exception as e:
            print(f"Failed to save plot to {save_path}: {e}")

    if show:
        plt.show()

#Constants
print_graph = True
plot_graph = False
n = int(input("Please enter n: ")) #5
p = int(input("Please enter p: ")) #5
graph_path = f"lobster_graph_n{n}_p{p}.json" #None
plot_path = f"lobster_plot_n{n}_p{p}.png" #None

graph = Graph()
create_lobster_graph(graph, n, p)
add_k_labeling(graph, n, p)

if print_graph:
    print("Node Count: ", graph.node_count)
    print("Edge Count: ", graph.edge_count)
    print("Adjacency List: ", graph.adj_list)
    seen = set()
    print("Edges:")
    for u in sorted(graph.edge_list):
        for v, weight in graph.edge_list[u]:
            e = (u, v) if u < v else (v, u)
            if e in seen:
                continue
            seen.add(e)
            print(f"{e[0]} -- {e[1]} (weight={weight})")
    print("Has Duplicate Edge Weights: ", graph.has_duplicate_edge_weights())

if graph_path:
    save_graph(graph, graph_path)

if plot_graph:
    plot_lobster_graph(graph, n, p, show_labels=True, show_weights=True)

if plot_path:
    # save without showing the interactive window
    plot_lobster_graph(graph, n, p, show_labels=True, show_weights=True, save_path=plot_path, show=False)

