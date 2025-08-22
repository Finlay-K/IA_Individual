"""
Benchmark Runner Script

This script dynamically discovers and executes benchmark scripts located in the
`proposal/benchmarks` directory. It provides two modes of operation:

1. Run all benchmark scripts that match the pattern `benchmark_*.py`.
2. Run a specific benchmark script using the `--run` argument.

Each benchmark module must define a top-level `run()` function to be executed.

Usage:
    python benchmark_runner.py              # Runs all benchmarks
    python benchmark_runner.py --run NAME   # Runs benchmark_NAME.py

Example:
    python benchmark_runner.py --run benchmark_sorting
"""

import importlib.util
import pathlib
import argparse
import sys

# Always resolve relative to this script's location to allow the directory to be found
# whether running the in vscode or for the terminal
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
BENCHMARK_DIR = SCRIPT_DIR / "benchmarks"

def load_and_run(file: pathlib.Path):
    """
    Dynamically loads and executes the `run()` function from the given benchmark file.

    Args:
        file (pathlib.Path): The full path to the benchmark Python file.
    """
    module_name = file.stem
    module_path = file.resolve()

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        print(f"Could not load spec for {module_name}")
        return

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        if hasattr(module, "run") and callable(module.run):
            print(f"\nRunning {module_name}.run()")
            module.run()
        else:
            print(f"{module_name} has no callable 'run()' function")
    except Exception as e:
        print(f"Error running {module_name}: {e}")

def load_and_run_all():
    """
    Discovers and runs all benchmark scripts in the benchmarks directory.
    """
    for file in BENCHMARK_DIR.glob("benchmark_*.py"):
        load_and_run(file)

def load_and_run_selected(name: str):
    """
    Runs a specific benchmark script by name.

    Args:
        name (str): The name of the benchmark module without the `.py` extension.
                    For example, to run `benchmark_sorting.py`, pass 'benchmark_sorting'.
    """
    target_file = BENCHMARK_DIR / f"{name}.py"
    if not target_file.exists():
        print(f"Benchmark script '{name}.py' not found in {BENCHMARK_DIR}")
        sys.exit(1)
    load_and_run(target_file)

def main():
    parser = argparse.ArgumentParser(description="Run one or all benchmark scripts.")
    parser.add_argument(
        "--run",
        metavar="BENCHMARK_NAME",
        help="Name of the benchmark to run (without .py). Example: benchmark_pathlib"
    )

    args = parser.parse_args()

    if args.run:
        load_and_run_selected(args.run)
    else:
        load_and_run_all()


if __name__ == "__main__":
    main()