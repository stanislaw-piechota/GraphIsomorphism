from collections import defaultdict

from graph import Vertex, Graph
from graph_io import load_graph, write_dot

MIN_COLOR = 1


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


def draw_graphs_by_vertices(graph_list, vertex_color: dict[Vertex, int]):
    for vertex, color in vertex_color.items():
        vertex.color = color

    for i, graph in enumerate(graph_list):
        with open(f'graph_{i + 1}.dot', 'w') as file:
            write_dot(graph, file)


def draw_graphs_by_colors(graph_list, color_vertices: dict[int, list[Vertex]]):
    for color, vertices in color_vertices.items():
        for vertex in vertices:
            vertex.color = color

    for i, graph in enumerate(graph_list):
        with open(f'graph_{i + 1}.dot', 'w') as file:
            write_dot(graph, file)


def solve_colorref(graph_list) -> tuple[dict[int, list[Vertex]], int]:
    all_vertices = [vertex for graph in graph_list for vertex in graph.vertices]
    prev_color_vertices, prev_vertex_color = {MIN_COLOR: all_vertices}, {vertex: MIN_COLOR for vertex in
                                                                         all_vertices}  # coloring a_1
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


def verify_discrete(color_counts: list[int]) -> bool:
    return color_counts.count(1) == len(color_counts)


def basic_colorref(path: str) -> list[tuple[list[int], dict[int, int], int, bool]]:
    with open(path, 'r') as file:
        graph_list = load_graph(file, read_list=True)

    all_graphs_coloring, _ = solve_colorref(graph_list)
    graph_equivalence_classes = get_equivalence_classes(graph_list, all_graphs_coloring)

    output_data = []
    for equivalence_class in graph_equivalence_classes:
        class_graph_list = [graph_list[i] for i in equivalence_class]
        class_coloring, iteration_count = solve_colorref(class_graph_list)
        # draw_graphs_by_colors(class_graph_list, class_coloring)git
        color_counts = [len(vertices) // len(equivalence_class) for vertices in class_coloring.values()]
        output_data.append((equivalence_class, sorted(color_counts), iteration_count, verify_discrete(color_counts)))

    return output_data


if __name__ == "__main__":
    result = basic_colorref("input/colorref/colorref_largeexample_6_960.grl")
    print(result)
