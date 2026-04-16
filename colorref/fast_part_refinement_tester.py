from pathlib import Path

from branching.branching_v1_0_4 import refine
from colorref.colorref_v1_2_1 import basic_colorref
from colorref.colorref_v2_0_0 import fast_colorref
from graphs.alex.graph import Graph
from graphs.alex.graph_io import load_graph
from testing.test_function_multicore import create_report


def fast_part_refinement(path: str):
    with open(path, "r") as file:
        graph_list = load_graph(file, Graph, True)  # pyright: ignore[reportAssignmentType]

    vertices = [vertex for graph in graph_list for vertex in graph.vertices]
    color_classes, _ = refine(vertices)
    return color_classes


def run_fast_part_refinement_benchmark():
    paths = [
        #'../input/fast_colorref/threepaths10240.gr',
        #'../input/branching/bigtrees1.grl',
        #'../input/branching/bigtrees2.grl',
        #'../input/branching/bigtrees3.grl',
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
        '../input/fast_colorref/threepaths10.gr',
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

    paths = paths * 4

    create_report(
        [str(path) for path in paths],
        {
            "colorref 1.2.1": basic_colorref,
            "fast part refinement 1.0.4": fast_part_refinement,
            "colorref 2.0.0": fast_colorref,
        },
        out_path=str("../docs/colorref-v1_2_1-vs-fast-part-refinement.tex"),
        multiplier=1,
    )


if __name__ == "__main__":
    run_fast_part_refinement_benchmark()

