from collections import defaultdict

from graphs.graph import Vertex, Graph
from graphs.graph_io import load_graph
from testing.test_function import create_report

type Coloring = dict[Vertex, int]
type TColoring = dict[int, set[Vertex]]
MIN_COLOR = 0


def transform_coloring(vertex_color: Coloring) -> Coloring:
    new_vertex_color = {}
    color_group_vertices = defaultdict(set)
    for vertex, color in vertex_color.items():
        neighbourhood = tuple(sorted(vertex_color[vertex] for vertex in vertex.neighbours))
        color_group_vertices[(color, neighbourhood)].add(vertex)

    for index, items in enumerate(color_group_vertices.items()):
        color_group, vertices = items
        for vertex in vertices:
            new_vertex_color[vertex] = index

    return new_vertex_color


def solve_colorref(graph_list: list[Graph], initial_coloring: Coloring = None) -> Coloring:
    prev_coloring: Coloring = initial_coloring if initial_coloring is not None else {vertex: MIN_COLOR for graph in
                                                                                     graph_list for vertex in
                                                                                     graph.vertices}
    current_coloring = transform_coloring(prev_coloring)

    while prev_coloring != current_coloring:
        prev_coloring = current_coloring
        current_coloring = transform_coloring(prev_coloring)

    return current_coloring

def solve_colorref_transform(graph_list: list[Graph], initial_coloring: Coloring = None) -> TColoring:
    coloring = solve_colorref(graph_list, initial_coloring)
    transformation: TColoring = defaultdict(set)

    for vertex, color in coloring.items():
        transformation[color].add(vertex)

    return transformation

# @profile
def basic_colorref(path: str) -> Coloring:
    with open(path, 'r') as file:
        graph_list = load_graph(file, read_list=True)

    return solve_colorref(graph_list)


if __name__ == '__main__':
    basic_colorref('input/colorref/colorref_largeexample_6_960.grl')

    # paths = [
    #     'input/colorref',
    #     'input/fast_colorref/threepaths5.gr',
    #     'input/fast_colorref/threepaths10.gr',
    #     'input/fast_colorref/threepaths20.gr',
    #     'input/fast_colorref/threepaths40.gr',
    #     'input/fast_colorref/threepaths80.gr',
    #     'input/fast_colorref/threepaths160.gr',
    #     'input/fast_colorref/threepaths320.gr',
    #     'input/fast_colorref/threepaths640.gr',
    #     'input/fast_colorref/threepaths1280.gr',
    #     'input/fast_colorref/threepaths2560.gr',
    # ]
    #
    # create_report(paths, {
    #     'colorref 1.2.0' : fast_colorref,
    #     'colorref 1.2.1' : basic_colorref
    # }, out_path='docs/colorref-1.2.0-vs-1.2.1.tex', multiplier=1000)
