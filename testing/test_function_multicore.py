import os
import time
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from .test_function import DOCUMENT_TEMPLATE


BENCHMARK_TIMEOUT_SECONDS = 10 * 60


def _terminate_executor(executor: ProcessPoolExecutor):
    """Force-stop running workers when a benchmark exceeds its deadline."""
    if hasattr(executor, "terminate_workers"):
        executor.terminate_workers()
    else:
        executor.shutdown(wait=False, cancel_futures=True)


def measure_time(function, path: str, label: str | None = None):
    start_time = time.perf_counter()
    result = function(path)
    # print(result)
    end_time = time.perf_counter()
    function_label = label or getattr(function, "__name__", str(function))
    print(f"Total time of running {function_label}: {end_time - start_time}s")
    return end_time - start_time


def run_functions_parallel(functions: dict, path: str,
                           timeout_seconds: int = BENCHMARK_TIMEOUT_SECONDS):
    if not functions:
        return {}

    results = {}
    base_name = os.path.basename(path)

    with ProcessPoolExecutor(max_workers=len(functions)) as executor:
        futures = {}
        for f_name, func in functions.items():
            print(f"Running {f_name} on {base_name}")
            futures[executor.submit(measure_time, func, path, f_name)] = f_name

        start = time.perf_counter()
        for future, f_name in futures.items():
            remaining = max(0.0, timeout_seconds - (time.perf_counter() - start))
            try:
                results[f_name] = (future.result(timeout=remaining), None)
            except TimeoutError as exc:
                print(f"Timeout while running {f_name} on {path}: exceeded {timeout_seconds}s")
                results[f_name] = (None, exc)
                _terminate_executor(executor)
                for pending_future, pending_name in futures.items():
                    if pending_name not in results:
                        results[pending_name] = (None, TimeoutError(f"Timeout after {timeout_seconds}s"))
                break
            except Exception as exc:
                print(f"Error while running {f_name} on {path}: {exc}")
                results[f_name] = (None, exc)

    return results


def create_report(in_paths: list[str], functions: dict,
                  out_path: str = "docs/benchmarks.tex", multiplier=1,
                  timeout_seconds: int = BENCHMARK_TIMEOUT_SECONDS):
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
                parallel_results = run_functions_parallel(functions, file_name, timeout_seconds=timeout_seconds)
                for f_name in functions.keys():
                    result_time, error = parallel_results[f_name]
                    results += f" & {round(result_time * multiplier, 2)}" if error is None else " & ERR"
                results += " \\\\\n"
        else:
            results += f"\t\t{os.path.basename(in_path)}"
            parallel_results = run_functions_parallel(functions, in_path, timeout_seconds=timeout_seconds)
            for f_name in functions.keys():
                result_time, error = parallel_results[f_name]
                results += f" & {round(result_time * multiplier, 2)}" if error is None else " & ERR"
            results += " \\\\\n"

    document = document.replace("#DATA#", results.replace('_', '\\_'))

    with open(out_path, "w") as f:
        f.write(document)
