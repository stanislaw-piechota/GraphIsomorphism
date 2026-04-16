import re
import statistics
from collections import defaultdict


def parse_latex_table(file_path):
    data = defaultdict(lambda: {'colorref_1_2_1': [], 'fast_part_1_0_4': [], 'colorref_2_0_0': []})
    row_pattern = re.compile(r"^\s*(.+?)\s*&\s*([0-9\.]+|ERR)\s*&\s*([0-9\.]+|ERR)\s*&\s*([0-9\.]+|ERR)\s*\\\\")

    with open(file_path, 'r') as f:
        for line in f:
            match = row_pattern.search(line)
            if match:
                filename = match.group(1).replace(r'\_', '_').strip()
                val_colorref_1_2_1 = match.group(2).strip()
                val_fast_part_1_0_4 = match.group(3).strip()
                val_colorref_2_0_0 = match.group(4).strip()

                data[filename]['colorref_1_2_1'].append(val_colorref_1_2_1)
                data[filename]['fast_part_1_0_4'].append(val_fast_part_1_0_4)
                data[filename]['colorref_2_0_0'].append(val_colorref_2_0_0)

    return data


def calculate_stats(values):
    if 'ERR' in values:
        return "-"

    float_vals = [float(v) for v in values]
    if not float_vals:
        return "N/A"

    avg = statistics.mean(float_vals)
    if len(float_vals) > 1:
        dev = statistics.stdev(float_vals)
    else:
        dev = 0.0

    return f"{avg:.3f} +/- {dev:.3f}"


def main():
    file_path = 'colorref-v1_2_1-vs-fast-part-refinement-vs-colorref_v2_0_0.tex'

    try:
        data = parse_latex_table(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return

    # Print header
    print(f"{'File Name':<35} | {'colorref 1.2.1':<22} | {'fast part ref 1.0.4':<22} | {'fast_part_backwards_comp (cref 2.0.0)':<22}")
    print("-" * 105)

    for filename, results in data.items():
        stat_colorref_1_2_1 = calculate_stats(results['colorref_1_2_1'])
        stat_fast_part_1_0_4 = calculate_stats(results['fast_part_1_0_4'])
        stat_colorref_2_0_0 = calculate_stats(results['colorref_2_0_0'])

        print(f"{filename:<35} | {stat_colorref_1_2_1:<22} | {stat_fast_part_1_0_4:<22} | {stat_colorref_2_0_0:<22}")


if __name__ == "__main__":
    main()