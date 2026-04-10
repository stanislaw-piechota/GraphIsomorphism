from line_profiler_pycharm import profile

import concurrent.futures

from automorphisms.automorphisms import analyze_automorphisms
from colorref.colorref_v1_0_0 import is_balanced, is_bijection
from colorref.colorref_v1_2_1 import MIN_COLOR, solve_colorref_transform
from graphs.graph import Graph, Vertex
from graphs.graph_io import load_graph
from testing.test_function_multicore import create_report
from branching.branching_v1_0_5 import are_isomorphic

# for comparative testing
from branching.branching_v1_0_3 import basic_branching
from branching.branching_v1_0_4 import fast_branching
from branching.branching_v1_0_5 import aut_branching
from branching.branching_v1_0_6 import aut_mixed_branching
from branching.branching_v1_0_7 import aut_fast_branching_v3

MAX_DEPTH_FOR_PARALLELIZATION = 0

# early terminating branching based on branching_v1_0_3.py, augmented with process parallelization
def are_isomorphic_multicore(g: Graph, h: Graph, d_seq: list[Vertex], i_seq: list[Vertex], depth: int = 0) -> bool:
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
    if depth <= MAX_DEPTH_FOR_PARALLELIZATION and len(y_set) > 1:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for y in y_set:
                futures.append(executor.submit(are_isomorphic_multicore, g, h, d_seq + [x], i_seq + [y], depth + 1))
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    executor.shutdown(wait=False, cancel_futures=True)
                    return True
        return False
    else:
        for y in y_set:
            if are_isomorphic_multicore(g, h, d_seq + [x], i_seq + [y], depth + 1):
                return True
        return False


def aut_basic_bad_multicore_branching(path: str):
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
            if are_isomorphic_multicore(base_graph, graph, [], []):
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


def aut_basic_multicore_branching(path: str):
    with open(path, "r") as file:
        graph_list = load_graph(file, read_list=True)

    isomorphic_graphs = []
    iso_counts = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for i, graph in enumerate(graph_list):
            print(f"Processing graph {i}")
            class_found = False
            future_to_class_idx = {}
            for class_idx, iso_class in enumerate(isomorphic_graphs):
                base_graph = graph_list[iso_class[0]]
                future = executor.submit(are_isomorphic, base_graph, graph, [], [])
                future_to_class_idx[future] = class_idx

            for future in concurrent.futures.as_completed(future_to_class_idx):
                if future.result():
                    matched_class_idx = future_to_class_idx[future]
                    isomorphic_graphs[matched_class_idx].append(i)
                    class_found = True

                    for other_future in future_to_class_idx:
                        if other_future is not future:
                            other_future.cancel()
                    break

            if not class_found:
                print(f"Creating new iso class for graph {i}")
                anal_result = analyze_automorphisms(graph)
                isomorphic_graphs.append([i])
                iso_counts.append(anal_result.automorphism_count)

    for i, iso_class in enumerate(isomorphic_graphs):
        print(iso_class, iso_counts[i])

if __name__ == "__main__":
    one_round_paths = [
        '../input/branching/bigtrees1.grl',
        '../input/branching/bigtrees2.grl',
        '../input/branching/bigtrees3.grl',
        '../input/branching/cographs1.grl',
        '../input/branching/cubes3.grl',
        '../input/branching/cubes4.grl',
        '../input/branching/cubes5.grl',
        '../input/branching/cubes6.grl',
        '../input/branching/cubes7.grl',
        '../input/branching/cubes8.grl',
        '../input/branching/cubes9.grl',
        '../input/branching/lecture.grl',
        '../input/branching/modulesC.grl',
        '../input/branching/modulesD.grl',
        '../input/branching/products216.grl',
        '../input/branching/products72.grl',
        '../input/branching/regulartwins.grl',
        '../input/branching/small forest.gr',
        '../input/branching/torus144.grl',
        '../input/branching/torus24.grl',
        '../input/branching/torus72.grl',
        '../input/branching/trees11.grl',
        '../input/branching/trees36.grl',
        '../input/branching/trees90.grl',
        '../input/branching/wheeljoin14.grl',
        '../input/branching/wheeljoin19.grl',
        '../input/branching/wheeljoin25.grl',
        '../input/branching/wheeljoin33.grl',
        '../input/branching/wheelstar12.grl',
        '../input/branching/wheelstar15.grl',
        '../input/branching/wheelstar16.grl',
        '../input/fast_colorref/threepaths10.gr',
        '../input/fast_colorref/threepaths10240.gr',
        '../input/fast_colorref/threepaths1280.gr',
        '../input/fast_colorref/threepaths160.gr',
        '../input/fast_colorref/threepaths20.gr',
        '../input/fast_colorref/threepaths2560.gr',
        '../input/fast_colorref/threepaths320.gr',
        '../input/fast_colorref/threepaths40.gr',
        '../input/fast_colorref/threepaths5.gr',
        '../input/fast_colorref/threepaths5120.gr',
        '../input/fast_colorref/threepaths640.gr',
        '../input/fast_colorref/threepaths80.gr',
        '../input/colorref/colorref_largeexample_4_1026.grl',
        '../input/colorref/colorref_largeexample_6_960.grl',
    ]
    paths = one_round_paths * 2

    create_report(paths, {
         #'aut_basic_bad_multicore_branching': aut_basic_bad_multicore_branching,
        'aut_basic_multicore_branching': aut_basic_multicore_branching,
        'aut_fast_branching_v3': aut_fast_branching_v3,
         'aut_mixed_branching': aut_mixed_branching,
        'aut_basic_branching': aut_branching,
        'basic_branching': basic_branching,
        'fast_branching': fast_branching,
    }, out_path='../docs/branching-v1_0_3-vs-v1_0_4-vs-v1_0_5-vs-v1_0_6-vs-v1_0_7-vs-v1_0_8.tex')