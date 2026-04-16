import sys
from pathlib import Path
import concurrent.futures

from branching.branching_v1_0_9 import aut_fast_multicore_branching

from branching.branching_v1_0_8 import aut_basic_multicore_branching
from branching.branching_v1_0_3 import basic_branching
from branching.branching_v1_0_4 import fast_branching
from branching.branching_v1_0_5 import aut_branching
from branching.branching_v1_0_6 import aut_mixed_branching
from branching.branching_v1_0_7 import aut_fast_branching_v3
from branching.branching_v1_1_0 import aut_dupa_branching
from branching.branching_v1_0_8 import aut_basic_multicore_branching
from automorphisms.automorphisms import count_automorphisms, count_automorphisms_multicore
from automorphisms.automorphisms_fast_branching import count_automorphisms as count_automorphisms_fast
from automorphisms.automorphisms_fast_ref import count_automorphisms as count_automorphisms_faster
from automorphisms.automorphisms_fast_branching import count_automorphisms_multicore as count_automorphisms_fast_multicore
from automorphisms.automorphisms_fast_ref import count_automorphisms_multicore as count_automorphisms_faster_multicore
from branching.branching_v1_1_1 import aut_dupa_multicore_branching


def count_graphs_in_file(filepath: str) -> int:
    count = 0
    target_string = "# Number of vertices:"

    with open(filepath, 'r') as f:
        for line in f:
            if target_string in line:
                count += 1
    return count

BRANCHING_ALGORITHM = aut_dupa_branching
MULTICORE_BRANCHING_ALGORITHM = aut_dupa_multicore_branching
AUT_COUNTER_ALGORITHM = count_automorphisms_faster
MULTICORE_AUT_COUNTER_ALGORITHM = count_automorphisms_faster_multicore
def process_file(filepath: Path) -> tuple[str, str]:
    filename = filepath.name
    stem = filepath.stem  # filename without the extension
    n_graphs = count_graphs_in_file(str(filepath))

    try:
        if stem.endswith('GIAut'):
            if n_graphs >= 5:
                result = MULTICORE_BRANCHING_ALGORITHM(str(filepath))
            else:
                result = BRANCHING_ALGORITHM(str(filepath), do_aut_count=True)
            output_str = str(result)

        elif stem.endswith('GI'):
            if n_graphs >= 5:
                result = MULTICORE_BRANCHING_ALGORITHM(str(filepath), do_aut_count=False)
            else:
                result = BRANCHING_ALGORITHM(str(filepath), do_aut_count=False)
            output_str = str(result)

        elif stem.endswith('Aut'):
            if n_graphs >= 2:
                result = MULTICORE_AUT_COUNTER_ALGORITHM(str(filepath))
            else:
                result = AUT_COUNTER_ALGORITHM(str(filepath))
            output_str = str(result)

        else:
            output_str = "Error: Unknown task type. Filename stem must end in 'GI', 'Aut', or 'GIAut'."

    except Exception as e:
        output_str = f"Execution Error: {str(e)}"

    return filename, output_str


def main():
    folder_path = input("Enter the path to the folder with files to analyze: ").strip()
    folder = Path(folder_path)

    if not folder.is_dir():
        print(f"Error: The directory '{folder_path}' does not exist.")
        sys.exit(1)

    files_to_process = []
    for ext in ('*.gr', '*.grl'):
        files_to_process.extend(folder.glob(ext))

    if not files_to_process:
        print("No .gr or .grl files found in the specified directory.")
        sys.exit(0)

    total_files = len(files_to_process)
    print(f"\nFound {total_files} files to process. Starting analysis...\n")

    output_file = folder / "analysis_results.txt"

    with open(output_file, 'w') as out_f:
        with concurrent.futures.ProcessPoolExecutor(max_tasks_per_child=1) as executor:
            future_to_file = {executor.submit(process_file, f): f for f in files_to_process}

            completed = 0
            for future in concurrent.futures.as_completed(future_to_file):
                completed += 1
                try:
                    filename, result_str = future.result()

                    print(f"[{completed}/{total_files}] Completed: {filename}")

                    out_f.write(f"{filename}:\n")
                    out_f.write(f"{result_str}\n")
                    out_f.write("-" * 40 + "\n")
                    out_f.flush()  # write to file immediately

                except Exception as exc:
                    file_path = future_to_file[future]
                    print(f"[{completed}/{total_files}] Failed: {file_path.name} generated an exception: {exc}")

    print(f"\nAll tasks complete! Results have been saved to: {output_file.resolve()}")


if __name__ == '__main__':
    main()