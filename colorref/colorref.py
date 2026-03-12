from collections import defaultdict

from graphs.graph import Vertex, Graph
from graphs.graph_io import load_graph

MIN_COLOR = 0


def transform_coloring(color_vertices: dict[int, list[Vertex]], vertex_color: dict[Vertex, int]) -> tuple[
    dict[int, list[Vertex]], dict[Vertex, int]]:
    current_color = max(color_vertices.keys())
    output_color_vertices, output_vertex_colors = defaultdict(list), {}

    for color, vertices in color_vertices.items():
        color_group_vertices = defaultdict(list)
        for vertex in vertices:
            color_group = tuple(sorted(vertex_color[vertex] for vertex in vertex.neighbours))
            color_group_vertices[color_group].append(vertex)

        vertices_group_color = {}
        preserveColor = True
        for group in color_group_vertices.keys():
            new_color = current_color = current_color + 1
            if preserveColor:
                new_color = color
                current_color -= 1
                preserveColor = False
            vertices_group_color[group] = new_color

        for group, group_vertices in color_group_vertices.items():
            new_color = vertices_group_color[group]
            for group_vertex in group_vertices:
                output_vertex_colors[group_vertex] = new_color
                output_color_vertices[new_color].append(group_vertex)

    return dict(output_color_vertices), output_vertex_colors


def solve_colorref(graph_list, initial_coloring: dict[int, list[Vertex]] = None) -> tuple[dict[int, list[Vertex]], int]:
    all_vertices = [vertex for graph in graph_list for vertex in graph.vertices]
    prev_color_vertices = {MIN_COLOR: all_vertices} if initial_coloring is None else initial_coloring
    prev_vertex_color = {} # coloring a_1
    for color, color_class in prev_color_vertices.items():
        for vertex in color_class:
            prev_vertex_color[vertex] = color
    cur_color_vertices, cur_vertex_color = transform_coloring(prev_color_vertices, prev_vertex_color)  # coloring a_2
    iteration_count = 1

    while prev_vertex_color != cur_vertex_color:
        iteration_count += 1
        prev_color_vertices, prev_vertex_color = cur_color_vertices, cur_vertex_color
        cur_color_vertices, cur_vertex_color = transform_coloring(prev_color_vertices,
                                                                  prev_vertex_color)  # coloring a_i

    return cur_color_vertices, iteration_count - 1


def verify_graph_equivalence(g: Graph, h: Graph, color_vertices: dict[int, list[Vertex]]) -> bool:
    g_vertices_set, h_vertices_set = set(g.vertices), set(h.vertices)
    for color, color_equivalence_class in color_vertices.items():
        color_equivalence_class = set(color_equivalence_class)
        if len(g_vertices_set.intersection(color_equivalence_class)) != len(
                h_vertices_set.intersection(color_equivalence_class)):
            return False
    return True


def get_equivalence_classes(graph_list: list[Graph], color_vertices: dict[int, list[Vertex]]) -> list[list[int]]:
    graph_equivalence_classes = []
    used_graph_indices = []
    for i, graph_i in enumerate(graph_list):
        if i in used_graph_indices:
            continue

        equivalence_class = [i]
        used_graph_indices.append(i)
        for rel_j, graph_j in enumerate(graph_list[i + 1:]):
            real_j = i + rel_j + 1
            if real_j not in used_graph_indices and verify_graph_equivalence(graph_i, graph_j, color_vertices):
                equivalence_class.append(real_j)
                used_graph_indices.append(real_j)
        graph_equivalence_classes.append(equivalence_class)

    return graph_equivalence_classes


def is_discrete(color_counts: list[int]) -> bool:
    return color_counts.count(1) == len(color_counts)


def is_balanced(graph_list: list[Graph], coloring: dict[int, list[Vertex]]) -> bool:
    for color, color_class in coloring.items():
        for i in range(len(graph_list) - 1):
            for j in range(i + 1, len(graph_list)):
                # TODO: Optimize memory/time usage
                color_class_set = set(color_class)
                if len(color_class_set.intersection(set(graph_list[i].vertices))) != len(
                        color_class_set.intersection(set(graph_list[j].vertices))):
                    return False
    return True


def is_bijection(g: Graph, h: Graph, coloring: dict[int, list[Vertex]]) -> bool:
    g_set, h_set = set(g.vertices), set(h.vertices)
    for color, color_class in coloring.items():
        color_class_set = set(color_class)
        g_inter, h_inter = color_class_set.intersection(g_set), color_class_set.intersection(h_set)
        if len(g_inter) != len(h_inter) or len(g_inter) != 1:
            return False

    return True


def basic_colorref(path: str) -> list[tuple[list[int], dict[int, int], int, bool]]:
    with open(path, 'r') as file:
        graph_list = load_graph(file, read_list=True)

    all_graphs_coloring, _ = solve_colorref(graph_list)
    graph_equivalence_classes = get_equivalence_classes(graph_list, all_graphs_coloring)

    output_data = []
    for equivalence_class in graph_equivalence_classes:
        class_graph_list = [graph_list[i] for i in equivalence_class]
        class_coloring, iteration_count = solve_colorref(class_graph_list)
        color_counts = [len(vertices) // len(equivalence_class) for vertices in class_coloring.values()]
        output_data.append((equivalence_class, sorted(color_counts), iteration_count, is_discrete(color_counts)))

    return output_data


if __name__ == "__main__":
    result = basic_colorref("input/colorref/colorref_largeexample_6_960.grl")
    print(result)
