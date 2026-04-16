from testing.test_function_multicore import create_report

from automorphisms.automorphisms import count_automorphisms as count_automorphisms
from automorphisms.automorphisms import count_automorphisms_no_mt as count_automorphisms_no_mt
from automorphisms.automorphisms_fast_branching import count_automorphisms as count_automorphisms_fast_branching
from automorphisms.automorphisms_fast_branching import count_automorphisms_no_mt as count_automorphisms_fast_branching_no_mt
from automorphisms.automorphisms_fast_ref import count_automorphisms as count_automorphisms_fast_ref
from automorphisms.automorphisms_fast_ref import count_automorphisms_no_mt as count_automorphisms_fast_ref_no_mt
from automorphisms.automorphisms_fast_ref import count_automorphisms_multicore as count_automorphisms_fast_ref_multicore
from automorphisms.automorphisms_fast_ref import count_automorphisms_multicore_no_mt as count_automorphisms_fast_ref_no_mt


def run_automorphisms_benchmarks():
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

    paths = paths * 8

    create_report(
        [str(path) for path in paths],
        {
            "basic no mt": count_automorphisms_no_mt,
            "basic": count_automorphisms,
            "fast branching no mt": count_automorphisms_fast_branching_no_mt,
            "fast branching": count_automorphisms_fast_branching,
            "fast ref no mt": count_automorphisms_fast_ref_no_mt,
            "fast ref ": count_automorphisms_fast_ref,
            "fast ref multicore no mt": count_automorphisms_fast_ref_no_mt,
            "fast ref multicore": count_automorphisms_fast_ref_multicore,
        },
        out_path=str("../docs/automorphisms-benchmarks.tex"),
        multiplier=1,
    )


if __name__ == "__main__":
    run_automorphisms_benchmarks()

