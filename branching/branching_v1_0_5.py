from line_profiler_pycharm import profile

from automorphisms.automorphisms import analyze_automorphisms
from colorref.colorref_v1_0_0 import is_balanced, is_bijection
from colorref.colorref_v1_2_1 import MIN_COLOR, solve_colorref_transform
from graphs.graph import Graph, Vertex
from graphs.graph_io import load_graph
from testing.test_function import create_report
from branching.branching_v1_0_3 import basic_branching

# early terminating branching based on branching_v1_0_3.py
def are_isomorphic(g: Graph, h: Graph, d_seq: list[Vertex], i_seq: list[Vertex]) -> bool:
    graph_list = [g, h]
    initial_coloring = {vertex: MIN_COLOR for vertex in g.vertices + h.vertices}
    for i, vertices in enumerate(zip(d_seq, i_seq)):
        x_vertex, y_vertex = vertices
        initial_coloring[x_vertex] = MIN_COLOR + i + 1
        initial_coloring[y_vertex] = MIN_COLOR + i + 1
    coloring = solve_colorref_transform(graph_list, initial_coloring)
    # draw_graphs_by_colors(graph_list, coloring)

    if not is_balanced(graph_list, coloring):
        return False

    if is_bijection(g, h, coloring):
        return True

    min_color_class : None | int = None
    for color, color_class in coloring.items():
        if len(color_class) == 4:
            min_color_class = color
            break
        elif len(color_class) > 4 and (min_color_class is None or len(color_class) < len(coloring[min_color_class])):
            min_color_class = color

    if min_color_class is None:
        return False

    class_to_fix = set(coloring[min_color_class])

    y_set = class_to_fix.intersection(set(h.vertices))
    x = list(class_to_fix.difference(y_set))[0]
    for y in y_set:
        if are_isomorphic(g, h, d_seq + [x], i_seq + [y]):
            return True
    return False


def aut_branching(path: str):
    with open(path, 'r') as file:
        graph_list = load_graph(file, read_list=True)

    isomorphic_graphs = []
    iso_counts = []

    for i, graph in enumerate(graph_list):
        print(f"Processing graph {i}")
        class_found = False
        for iso_idx, iso_class in enumerate(isomorphic_graphs):
            print(f"Comparing with iso class {iso_idx}")
            base_graph = graph_list[iso_class[0]]
            if are_isomorphic(base_graph, graph, [], []):
                iso_class.append(i)
                class_found = True
                break

        if not class_found:
            print(f"Creating new iso class for graph {i}")
            anal_result = analyze_automorphisms(graph)
            isomorphic_graphs.append([i])
            iso_counts.append(anal_result.automorphism_count)

    for i, iso_class in enumerate(isomorphic_graphs):
        print(iso_class, iso_counts[i])


if __name__ == "__main__":

    paths = [
         '../input/branching/cubes3.grl',
         '../input/branching/cubes4.grl',
         '../input/branching/cubes5.grl',
         '../input/branching/trees36.grl',
         '../input/branching/wheeljoin14.grl',
         '../input/branching/modulesD.grl'
    ]
    create_report(paths, {
         'aut_branching': aut_branching,
         'basic_branching': basic_branching,
    }, out_path='../docs/branching-v1_0_3-vs-v1_0_4-n_aut.tex')