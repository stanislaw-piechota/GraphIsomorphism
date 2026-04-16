from testing.test_function_multicore import create_report

# Import all the branching functions
from branching.branching_v1_0_5 import aut_branching
from branching.branching_v1_0_6 import aut_mixed_branching
from branching.branching_v1_0_8 import aut_basic_multicore_branching
from branching.branching_v1_0_9 import aut_fast_multicore_branching
from branching.branching_v1_1_0 import aut_dupa_branching
from branching.branching_v1_1_1 import aut_dupa_multicore_branching


def run_aut_branching(p):
    return aut_branching(p, do_aut_count=False)


def run_aut_mixed_branching(p):
    return aut_mixed_branching(p, do_aut_count=False)


def run_aut_basic_multicore_branching(p):
    return aut_basic_multicore_branching(p, do_aut_count=False)


def run_aut_fast_multicore_branching(p):
    return aut_fast_multicore_branching(p, do_aut_count=False)


def run_aut_dupa_branching(p):
    return aut_dupa_branching(p, do_aut_count=False)


def run_aut_dupa_multicore_branching(p):
    return aut_dupa_multicore_branching(p, do_aut_count=False)


def run_gi_benchmarks():
    paths = [
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
        '../input/fast_colorref/threepaths10240.gr',
        '../input/colorref/colorref_largeexample_4_1026.grl',
        '../input/colorref/colorref_largeexample_6_960.grl',
    ]

    paths = paths * 4

    functions_to_test = {
        "aut_branching": run_aut_branching,
        "aut_mixed_branching": run_aut_mixed_branching,
        "aut_basic_multicore_branching": run_aut_basic_multicore_branching,
        "aut_fast_multicore_branching": run_aut_fast_multicore_branching,
        "aut_dupa_branching": run_aut_dupa_branching,
        "aut_dupa_multicore_branching": run_aut_dupa_multicore_branching,
    }

    create_report(
        [str(path) for path in paths],
        functions_to_test,
        out_path=str("../docs/gi-benchmarks.tex"),
        multiplier=1,
    )


if __name__ == "__main__":
    run_gi_benchmarks()
