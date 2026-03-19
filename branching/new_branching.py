from line_profiler_pycharm import profile

from colorref.colorref import is_balanced, is_bijection
from colorref.new_colorref import MIN_COLOR, solve_colorref_transform
from graphs.graph import Graph, Vertex
from graphs.graph_io import load_graph
from branching.branching import basic_branching as old_branching
from testing.test_function import create_report
from alex.fast_branching import basic_branching as fast_branching_v1
from alex.fast_branching import basic_branching as fast_branching_v2


def count_isomorphisms(g: Graph, h: Graph, d_seq: list[Vertex], i_seq: list[Vertex]) -> int:
    graph_list = [g, h]
    initial_coloring = {vertex: MIN_COLOR for vertex in g.vertices + h.vertices}
    for i, vertices in enumerate(zip(d_seq, i_seq)):
        x_vertex, y_vertex = vertices
        initial_coloring[x_vertex] = MIN_COLOR + i + 1
        initial_coloring[y_vertex] = MIN_COLOR + i + 1
    coloring = solve_colorref_transform(graph_list, initial_coloring)
    # draw_graphs_by_colors(graph_list, coloring)

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


@profile
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
    # paths = [
    #     'input/branching/cubes3.grl',
    #     'input/branching/cubes4.grl',
    #     'input/branching/cubes5.grl',
    #     'input/branching/trees36.grl',
    #     'input/branching/wheeljoin14.grl'
    # ]
    #
    # create_report(paths, {
    #     'normal_old_branching': old_branching,
    #     'normal_new_branching': basic_branching,
    #     'fast_branching_v1': fast_branching_v1,
    #     'fast_branching_v2': fast_branching_v2,
    # }, out_path='docs/branching-old-vs-new-1.0.0.tex')

    basic_branching('input/branching/modulesD.grl')