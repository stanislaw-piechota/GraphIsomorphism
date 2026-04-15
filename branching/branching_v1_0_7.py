from automorphisms.automorphisms_fast_branching import analyze_automorphisms

from graphs.alex.graph_io import load_graph
from orchestration.dataclasses import IsomorphismAnalResult
from testing.test_function import create_report

# for comparative testing
from branching.branching_v1_0_3 import basic_branching
from branching.branching_v1_0_4 import fast_branching
from branching.branching_v1_0_5 import aut_branching
from branching.branching_v1_0_6 import aut_mixed_branching

# are_isomorphic from branching_v1_0_6 ->
# this is an early terminating branching based on branching_v1_0_4.py (alex/fast_branching_v3.py),
from branching.branching_v1_0_6 import are_isomorphic
# now using the automorphism counter also based on the branching_v1_0_4.py

def aut_fast_branching_v3(path: str, do_aut_count: bool = True) -> IsomorphismAnalResult:
    with open(path, 'r') as file:
        graph_list = load_graph(file, read_list=True)

    isomorphic_graphs = []
    iso_counts = []

    for i, graph in enumerate(graph_list):
        # print(f"Processing graph {i}")
        class_found = False
        for iso_idx, iso_class in enumerate(isomorphic_graphs):
            # print(f"Comparing with iso class {iso_idx}")
            base_graph = graph_list[iso_class[0]]
            if are_isomorphic(base_graph, graph):
                iso_class.append(i)
                class_found = True
                break

        if not class_found:
            isomorphic_graphs.append([i])
            if do_aut_count:
                anal_result = analyze_automorphisms(graph)
                iso_counts.append(anal_result.automorphism_count)
            else:
                iso_counts.append(0)

    # for i, iso_class in enumerate(isomorphic_graphs):
    #     print(iso_class, iso_counts[i])

    return IsomorphismAnalResult(isomorphic_graphs=isomorphic_graphs, automorphism_counts=iso_counts, was_counting_automorphism=do_aut_count)


if __name__ == "__main__":

    paths = [
         '../input/branching/cubes3.grl',
         '../input/branching/cubes4.grl',
         '../input/branching/cubes5.grl',
         '../input/branching/cubes6.grl',
         '../input/branching/trees36.grl',
         '../input/branching/wheeljoin14.grl',
         '../input/branching/modulesD.grl'
         '../input/branching/cubes3.grl',
        '../input/branching/cubes4.grl',
        '../input/branching/cubes5.grl',
        '../input/branching/cubes6.grl',
        '../input/branching/trees36.grl',
        '../input/branching/wheeljoin14.grl',
        '../input/branching/modulesD.grl'
        '../input/branching/cubes3.grl',
        '../input/branching/cubes4.grl',
        '../input/branching/cubes5.grl',
        '../input/branching/cubes6.grl',
        '../input/branching/trees36.grl',
        '../input/branching/wheeljoin14.grl',
        '../input/branching/modulesD.grl'
    ]
    create_report(paths, {
        'aut_fast_branching_v3': aut_fast_branching_v3,
        'aut_mixed_branching': aut_mixed_branching,
        'aut_basic_branching': aut_branching,
        'basic_branching': basic_branching,
        'fast_branching': fast_branching,
    }, out_path='../docs/branching-v1_0_3-vs-v1_0_4-vs-v1_0_5-v1_0_6-v1_0_7.tex')