from automorphisms.automorphisms import analyze_automorphisms
from colorref.colorref_v1_0_0 import is_balanced, is_bijection
from graphs.alex.graph import Graph
from graphs.alex.graph_io import load_graph
from graphs.graph_io import load_graph as old_load_graph
from orchestration.dataclasses import IsomorphismAnalResult
from testing.test_function import create_report

from branching.branching_v1_0_4 import refine, is_balanced, is_bijection

# for comparative testing
from branching.branching_v1_0_3 import basic_branching
from branching.branching_v1_0_4 import fast_branching
from branching.branching_v1_0_5 import aut_branching

# early terminating branching core based on branching_v1_0_4.py (alex/fast_branching_v3.py),
# but using the automorphism counter based on branching_v1_0_3.py
def are_isomorphic(g: Graph, h: Graph) -> int:
    graphs = [g, h]

    color_classes, max_color = refine([v for graph_vertices in [g.vertices for g in graphs] for v in graph_vertices])

    if not is_balanced(g, h, color_classes):
        return False

    if is_bijection(g, h, color_classes):
        return True

    min_color_class: None | int = None
    for color, color_class in color_classes.items():
        if len(color_class) == 4:
            min_color_class = color
            break
        elif len(color_class) > 4 and (
                min_color_class is None or len(color_class) < len(color_classes[min_color_class])):
            min_color_class = color

    if min_color_class is None:
        return False

    class_to_fix = set(color_classes[min_color_class])

    y_set = class_to_fix.intersection(set(h.vertices))
    x = list(class_to_fix.difference(y_set))[0]
    for y in y_set:
        g_copy = g.copy()
        h_copy = h.copy()

        g_copy[x.label].color = h_copy[y.label].color = max_color + 1

        if are_isomorphic(g_copy, h_copy):
         return True
    return False


def aut_mixed_branching(path: str, do_aut_count: bool = True) -> IsomorphismAnalResult:
    with open(path, 'r') as file:
        graph_list = load_graph(file, read_list=True)
    with open(path, 'r') as file:
        old_graph_list = old_load_graph(file, read_list=True)

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
                anal_result = analyze_automorphisms(old_graph_list[i]) # dirty hack to avoid writing converters
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
    ]
    create_report(paths, {
         'aut_mixed_branching': aut_mixed_branching,
         'aut_basic_branching': aut_branching,
         'basic_branching': basic_branching,
         'fast_branching': fast_branching,
    }, out_path='../docs/branching-v1_0_3-vs-v1_0_4-vs-v1_0_5-v1_0_6.tex')