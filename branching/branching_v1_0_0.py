from line_profiler_pycharm import profile

from colorref.colorref_v1_0_0 import is_balanced, is_bijection, solve_colorref
from graphs.graph import Vertex, Graph
from graphs.graph_io import load_graph


MIN_COLOR = 0

@profile
def count_isomorphisms(g: Graph, h: Graph, d_seq: list[Vertex], i_seq: list[Vertex]) -> int:
    graph_list = [g, h]
    initial_coloring = {MIN_COLOR: g.vertices + h.vertices}
    for i, x_vertex in enumerate(d_seq):
        y_vertex = i_seq[i]
        initial_coloring[MIN_COLOR].remove(x_vertex)
        initial_coloring[MIN_COLOR].remove(y_vertex)
        initial_coloring[MIN_COLOR + i + 1] = [x_vertex, y_vertex]
    coloring, _ = solve_colorref(graph_list, initial_coloring)

    if not is_balanced(graph_list, coloring):
        return 0

    if is_bijection(g, h, coloring):
        return 1

    min_color_class : None | int = None
    for color, color_class in coloring.items():
        if len(color_class) == 4:
            min_color_class = color
            break
        elif len(color_class) > 4 and (min_color_class is None or len(color_class) < len(coloring[min_color_class])):
            min_color_class = color

    if min_color_class is None:
        return 0

    class_to_fix = set(coloring[min_color_class])

    num = 0
    y_set = class_to_fix.intersection(set(h.vertices))
    x = list(class_to_fix.difference(y_set))[0]
    for y in y_set:
        num += count_isomorphisms(g, h, d_seq + [x], i_seq + [y])
    return num


# @profile
def basic_branching(path: str):
    with open(path, 'r') as file:
        graph_list = load_graph(file, read_list=True)

    isomorphic_graphs = [[0]]
    iso_counts = [0]

    for i, graph in enumerate(graph_list[1:]):
        print(f"Processing graph {i+2}")
        class_found = False
        for iso_idx, iso_class in enumerate(isomorphic_graphs[::]):
            print(f"Comparing with iso class {iso_idx+1}")
            base_graph = graph_list[iso_class[0]]
            count = count_isomorphisms(base_graph, graph, [], [])
            if count != 0:
                iso_class.append(i+1)
                iso_counts[iso_idx] = count
                class_found = True
                break

        if not class_found:
            isomorphic_graphs.append([i+1])
            iso_counts.append(0)


    for i, iso_class in enumerate(isomorphic_graphs):
        print(iso_class, iso_counts[i])


if __name__ == "__main__":
    print(basic_branching("input/branching/cubes4.grl"))

    # paths = [
    #     'input/branching/cubes3.grl',
    #     'input/branching/cubes4.grl',
    #     'input/branching/cubes5.grl',
    #     'input/branching/trees36.grl',
    #     'input/branching/wheeljoin14.grl'
    # ]
    #
    # create_report(paths, {
    #     'normal_branching': basic_branching,
    #     'fast_branching': fast_branching
    # }, out_path='docs/branching-normal-vs-fast-1.0.0.tex')
