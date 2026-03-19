import os
import time
from threading import Thread


def test_function(function, path: str):
    input_files = os.listdir(path)
    for file in input_files:
        full_path = os.path.join(path, file)
        print(f"Testing file {full_path}")
        result = function(full_path)
        print(result)


def measure_time(function, path: str):
    start_time = time.time()
    result = function(path)
    # print(result)
    end_time = time.time()
    print(f"Total time of running {function}: {end_time - start_time}s")
    return end_time - start_time


def compare_functions(f1, f2, path: str):
    t1 = Thread(target=measure_time, args=(f1, path))
    t2 = Thread(target=measure_time, args=(f2, path))
    t1.start()
    t2.start()
    t1.join()
    t2.join()


DOCUMENT_TEMPLATE = """
%! Author = stanislaw
%! Date = 12.03.2026

% Preamble
\\documentclass[11pt]{article}

% Packages
\\usepackage{amsmath}
\\usepackage{tabularx}
\\usepackage{booktabs}
\\usepackage{seqsplit}

% Document
\\begin{document}

\\begin{table}[h!]
    \\centering
    \\small
    \\begin{tabularx}{\\textwidth}{|l#LAYOUT#}
        \\hline
        File name & #FILE_NAMES# \\\\
        \\hline
#DATA#        \\hline
    \\end{tabularx}
    \\caption{Example of a basic table}
    \\label{tab:1}
\\end{table}

\\end{document}
"""


def create_report(in_paths: list[str], functions: dict,
                  out_path: str = "docs/benchmarks.tex"):
    file_names = " & ".join(["\\seqsplit{"+name+"}" for name in functions.keys()]).replace("_", "\\_")
    document = DOCUMENT_TEMPLATE.replace("#FILE_NAMES#", file_names)
    document = document.replace("#LAYOUT#", "|"+"X|"*len(functions.keys()))

    results = ""
    for in_path in in_paths:
        if os.path.isdir(in_path):
            for file in os.listdir(in_path):
                file_name = os.path.join(in_path, file)
                base_name = os.path.basename(file_name)
                results += f"\t\t{base_name}"
                for f_name, func in functions.items():
                    print(f"Running {f_name} on {base_name}")
                    result_time = measure_time(func, file_name)
                    results += f" & {round(result_time, 2)}"
                results += " \\\\\n"
        else:
            results += f"\t\t{os.path.basename(in_path)}"
            for f_name, func in functions.items():
                print(f"Running {f_name} on {in_path}")
                result_time = measure_time(func, in_path)
                results += f" & {round(result_time, 2)}"
            results += " \\\\\n"

    document = document.replace("#DATA#", results.replace('_', '\\_'))

    with open(out_path, "w") as f:
        f.write(document)
