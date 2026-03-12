from graphs.graph import Vertex
from graphs.graph_io import write_dot


def draw_graphs_by_vertices(graph_list, vertex_color: dict[Vertex, int]):
    for vertex, color in vertex_color.items():
        vertex.color = color

    for i, graph in enumerate(graph_list):
        with open(f'graphs_out/graph_{i + 1}.dot', 'w') as file:
            write_dot(graph, file)


def draw_graphs_by_colors(graph_list, color_vertices: dict[int, list[Vertex]]):
    for color, vertices in color_vertices.items():
        for vertex in vertices:
            vertex.color = color

    for i, graph in enumerate(graph_list):
        with open(f'graphs_out/graph_{i + 1}.dot', 'w') as file:
            write_dot(graph, file)