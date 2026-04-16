import re
import statistics
from collections import defaultdict

# https://gemini.google.com/share/a1fff68ccc17
def parse_log(filepath, timeout_penalty=600.0):
    # Data structure: data[algorithm][dataset] = {'times': [], 'successes': 0, 'failures': 0}
    data = defaultdict(lambda: defaultdict(lambda: {'times': [], 'successes': 0, 'failures': 0}))

    current_dataset = None
    pending_algs = set()

    # Regex patterns to capture the necessary lines
    re_start = re.compile(r"Running\s+(.+?)\s+on\s+(?:.*/)?(.+?)\.grl?")
    re_success = re.compile(r"Total time of running\s+(.+?):\s+([0-9.]+)s")
    re_timeout = re.compile(r"Timeout while running\s+(.+?)\s+on\s+(?:.*/)?(.+?)\.grl?:\s+exceeded\s+([0-9.]+)s")

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            # 1. Check for the start of an algorithm run
            m_start = re_start.search(line)
            if m_start:
                alg, dataset = m_start.groups()

                # If we encounter a new dataset, flush any pending algorithms from the previous one as timeouts
                if current_dataset and dataset != current_dataset:
                    for p_alg in pending_algs:
                        data[p_alg][current_dataset]['times'].append(timeout_penalty)
                        data[p_alg][current_dataset]['failures'] += 1
                    pending_algs.clear()

                current_dataset = dataset
                pending_algs.add(alg)
                continue

            # 2. Check for a successful completion
            m_succ = re_success.search(line)
            if m_succ:
                alg, time_str = m_succ.groups()
                if alg in pending_algs:
                    data[alg][current_dataset]['times'].append(float(time_str))
                    data[alg][current_dataset]['successes'] += 1
                    pending_algs.remove(alg)
                continue

            # 3. Check for an explicit timeout
            m_tout = re_timeout.search(line)
            if m_tout:
                alg, dataset, limit_str = m_tout.groups()
                if alg in pending_algs:
                    data[alg][dataset]['times'].append(float(limit_str))
                    data[alg][dataset]['failures'] += 1
                    pending_algs.remove(alg)
                continue

    # Flush any remaining pending algorithms at the very end of the file as timeouts
    if current_dataset:
        for p_alg in pending_algs:
            data[p_alg][current_dataset]['times'].append(timeout_penalty)
            data[p_alg][current_dataset]['failures'] += 1
        pending_algs.clear()

    return data


def generate_report(data):
    algorithms = sorted(list(data.keys()))

    print("=" * 80)
    print(" PER-DATASET BREAKDOWN")
    print("=" * 80)

    # Gather all unique datasets
    all_datasets = set()
    for alg in data:
        for ds in data[alg]:
            all_datasets.add(ds)
    all_datasets = sorted(list(all_datasets))

    for ds in all_datasets:
        print(f"\n--- Dataset: {ds} ---")
        for alg in algorithms:
            if ds in data[alg]:
                stats = data[alg][ds]
                times = stats['times']
                succ = stats['successes']
                fail = stats['failures']
                total_runs = succ + fail

                if total_runs == 0:
                    continue

                avg_time = statistics.mean(times)
                std_dev = statistics.stdev(times) if len(times) > 1 else 0.0

                print(f"  {alg:<30} | Avg: {avg_time:>7.2f}s +/- {std_dev:>6.2f}s | "
                      f"Success: {succ}/{total_runs} (Failures: {fail})")

    print("\n\n" + "=" * 80)
    print(" GRAND SUMMARY PER ALGORITHM")
    print("=" * 80)

    print(f"{'Algorithm':<32} | {'Avg Time':>12} | {'Std Dev':>10} | {'Success Rate'}")
    print("-" * 80)

    for alg in algorithms:
        all_times = []
        total_succ = 0
        total_fail = 0

        for ds in data[alg]:
            all_times.extend(data[alg][ds]['times'])
            total_succ += data[alg][ds]['successes']
            total_fail += data[alg][ds]['failures']

        total_runs = total_succ + total_fail
        if total_runs == 0:
            continue

        grand_avg = statistics.mean(all_times)
        grand_std = statistics.stdev(all_times) if len(all_times) > 1 else 0.0
        success_rate = (total_succ / total_runs) * 100

        print(f"{alg:<32} | {grand_avg:>11.2f}s | +/- {grand_std:>6.2f}s | "
              f"{total_succ}/{total_runs} ({success_rate:>5.1f}%)")


if __name__ == "__main__":
    # Ensure this path matches the location of your output file
    log_file_path = "terminal_output.txt"
    try:
        parsed_data = parse_log(log_file_path)
        generate_report(parsed_data)
    except FileNotFoundError:
        print(f"Error: Could not find '{log_file_path}'. Please check the path.")