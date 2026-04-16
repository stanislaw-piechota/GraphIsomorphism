import concurrent.futures

from automorphisms.automorphisms_fast_ref import analyze_automorphisms
from branching.branching_v1_1_0 import are_isomorphic, aut_dupa_branching
from colorref.colorref_v2_0_0 import fast_solve_colorref_transform, is_balanced, is_bijection, MIN_COLOR
from graphs.graph import Graph, Vertex
from graphs.graph_io import load_graph
from orchestration.dataclasses import IsomorphismAnalResult
from testing.test_function import create_report

# for comparative testing
from branching.branching_v1_0_3 import basic_branching
from branching.branching_v1_0_4 import fast_branching
from branching.branching_v1_0_5 import aut_branching
from branching.branching_v1_0_6 import aut_mixed_branching
from branching.branching_v1_0_7 import aut_fast_branching_v3
from branching.branching_v1_0_8 import aut_basic_multicore_branching


def aut_dupa_multicore_branching(path: str, do_aut_count: bool = True, do_membership_testing: bool = True) -> IsomorphismAnalResult:
    with open(path, "r") as file:
        graph_list = load_graph(file, read_list=True)

    isomorphic_graphs = []
    iso_counts = []

    with concurrent.futures.ProcessPoolExecutor(max_tasks_per_child=1) as executor:
        for i, graph in enumerate(graph_list):
            # print(f"Processing graph {i}")
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
                isomorphic_graphs.append([i])
                if do_aut_count:
                    anal_result = analyze_automorphisms(graph, do_membership_testing)
                    iso_counts.append(anal_result.automorphism_count)
                else:
                    iso_counts.append(0)

    #for i, iso_class in enumerate(isomorphic_graphs):
    #    print(iso_class, iso_counts[i])

    return IsomorphismAnalResult(isomorphic_graphs=isomorphic_graphs, automorphism_counts=iso_counts, was_counting_automorphism=do_aut_count)

def aut_dupa_multicore_branching_no_mt(path: str, do_aut_count: bool = True) -> IsomorphismAnalResult:
    return aut_dupa_multicore_branching(path, do_aut_count=do_aut_count, do_membership_testing=False)

if __name__ == "__main__":
    one_round_paths = [
        #'../input/branching/bigtrees1.grl',
        #'../input/branching/bigtrees2.grl',
        #'../input/branching/bigtrees3.grl',
        #'../input/branching/cographs1.grl',
        '../input/branching/cubes3.grl',
        '../input/branching/cubes4.grl',
        '../input/branching/cubes5.grl',
        '../input/branching/cubes6.grl',
        #'../input/branching/cubes7.grl',
        #'../input/branching/cubes8.grl',
        #'../input/branching/cubes9.grl',
        '../input/branching/lecture.grl',
        #'../input/branching/modulesC.grl',
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
        '../input/colorref/colorref_largeexample_4_1026.grl',
        '../input/colorref/colorref_largeexample_6_960.grl',
    ]
    paths = one_round_paths * 8

    create_report(paths, {
        'aut_dupa_multicore_branching': aut_dupa_multicore_branching,
        'aut_dupa_branching': aut_dupa_branching,
        'aut_basic_multicore_branching': aut_basic_multicore_branching,
        'aut_fast_branching_v3': aut_fast_branching_v3,
         'aut_mixed_branching': aut_mixed_branching,
        'aut_basic_branching': aut_branching,
        'basic_branching': basic_branching,
        'fast_branching': fast_branching,
    }, out_path='../docs/branching-v1_1_0.tex')