from automorphisms.automorphisms_fast_ref import analyze_automorphisms
from colorref.colorref_v2_0_0 import fast_solve_colorref_transform, is_balanced, is_bijection, MIN_COLOR
from graphs.graph import Graph, Vertex
from graphs.graph_io import load_graph
from orchestration.dataclasses import IsomorphismAnalResult
from testing.test_function_multicore import create_report

# for comparative testing
from branching.branching_v1_0_3 import basic_branching
from branching.branching_v1_0_4 import fast_branching
from branching.branching_v1_0_5 import aut_branching
from branching.branching_v1_0_6 import aut_mixed_branching
from branching.branching_v1_0_7 import aut_fast_branching_v3
from branching.branching_v1_0_8 import aut_basic_multicore_branching

# early terminating branching based on branching_v1_0_3.py, but colorref replaced with the faster colorref_v2_0_0
def are_isomorphic(g: Graph, h: Graph, d_seq: list[Vertex], i_seq: list[Vertex]) -> bool:
    initial_coloring = {vertex: MIN_COLOR for vertex in g.vertices + h.vertices}
    for i, vertices in enumerate(zip(d_seq, i_seq)):
        x_vertex, y_vertex = vertices
        initial_coloring[x_vertex] = MIN_COLOR + i + 1
        initial_coloring[y_vertex] = MIN_COLOR + i + 1
    coloring = fast_solve_colorref_transform(initial_coloring)
    # draw_graphs_by_colors(graph_list, coloring)

    if not is_balanced(g, h, coloring):
        return False

    if is_bijection(g, h, coloring):
        return True

    min_color_class: None | int = None
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


def aut_dupa_branching(path: str, do_aut_count: bool = True, do_membership_testing: bool = True) -> IsomorphismAnalResult:
    with open(path, 'r') as file:
        graph_list = load_graph(file, read_list=True)

    isomorphic_graphs = []
    iso_counts = []

    for i, graph in enumerate(graph_list):
        class_found = False
        for iso_idx, iso_class in enumerate(isomorphic_graphs):
            base_graph = graph_list[iso_class[0]]
            if are_isomorphic(base_graph, graph, [], []):
                iso_class.append(i)
                class_found = True
                break

        if not class_found:
            isomorphic_graphs.append([i])
            if do_aut_count:
                anal_result = analyze_automorphisms(graph, do_membership_testing)
                iso_counts.append(anal_result.automorphism_count)
            else:
                iso_counts.append(0)

    return IsomorphismAnalResult(isomorphic_graphs=isomorphic_graphs, automorphism_counts=iso_counts, was_counting_automorphism=do_aut_count)

def aut_dupa_branching_no_mt(path: str, do_aut_count: bool = True) -> IsomorphismAnalResult:
    return aut_dupa_branching(path, do_aut_count=do_aut_count, do_membership_testing=False)

if __name__ == "__main__":
    one_round_paths = [
        '../input/colorref/colorref_largeexample_4_1026.grl',
        '../input/branching/bigtrees1.grl',
        '../input/branching/bigtrees2.grl',
        '../input/branching/bigtrees3.grl',
        '../input/branching/bigtrees1.grl',
        '../input/branching/bigtrees2.grl',
        '../input/branching/bigtrees3.grl',
        '../input/branching/bigtrees1.grl',
        '../input/branching/bigtrees2.grl',
        '../input/branching/bigtrees3.grl',
        '../input/branching/bigtrees1.grl',
        '../input/branching/bigtrees2.grl',
        '../input/branching/bigtrees3.grl',
        #'../input/branching/cographs1.grl',
        #'../input/branching/cubes3.grl',
        #'../input/branching/cubes4.grl',
        #'../input/branching/cubes5.grl',
        #'../input/branching/cubes6.grl',
        #'../input/branching/cubes7.grl',
        #'../input/branching/cubes8.grl',
        #'../input/branching/cubes9.grl',
        #'../input/branching/lecture.grl',
        #'../input/branching/modulesC.grl',
        #'../input/branching/modulesD.grl',
        #'../input/branching/products216.grl',
        #'../input/branching/products72.grl',
        #'../input/branching/regulartwins.grl',
        #'../input/branching/small forest.gr',
        #'../input/branching/torus144.grl',
        #'../input/branching/torus24.grl',
        #'../input/branching/torus72.grl',
        #'../input/branching/trees11.grl',
        #'../input/branching/trees36.grl',
        #'../input/branching/trees90.grl',
        #'../input/branching/wheeljoin14.grl',
        #'../input/branching/wheeljoin19.grl',
        #'../input/branching/wheeljoin25.grl',
        #'../input/branching/wheeljoin33.grl',
        #'../input/branching/wheelstar12.grl',
        #'../input/branching/wheelstar15.grl',
        #'../input/branching/wheelstar16.grl',
        #'../input/fast_colorref/threepaths10.gr',
        #'../input/fast_colorref/threepaths10240.gr',
        #'../input/fast_colorref/threepaths1280.gr',
        #'../input/fast_colorref/threepaths160.gr',
        #'../input/fast_colorref/threepaths20.gr',
        #'../input/fast_colorref/threepaths2560.gr',
        #'../input/fast_colorref/threepaths320.gr',
        #'../input/fast_colorref/threepaths40.gr',
        #'../input/fast_colorref/threepaths5.gr',
        #'../input/fast_colorref/threepaths5120.gr',
        #'../input/fast_colorref/threepaths640.gr',
        #'../input/fast_colorref/threepaths80.gr',

        '../input/colorref/colorref_largeexample_6_960.grl',
    ]
    paths = one_round_paths * 4

    create_report(paths, {
        'aut_dupa_branching': aut_dupa_branching,
        'aut_basic_multicore_branching': aut_basic_multicore_branching,
        'aut_fast_branching_v3': aut_fast_branching_v3,
         'aut_mixed_branching': aut_mixed_branching,
        'aut_basic_branching': aut_branching,
        'basic_branching': basic_branching,
        'fast_branching': fast_branching,
    }, out_path='../docs/branching-v1_1_0.tex')