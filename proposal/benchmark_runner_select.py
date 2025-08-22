"""
Interactive Benchmark Runner

This script provides an interactive terminal interface for discovering and executing
benchmark scripts located in the `proposal/benchmarks` directory.

Features:
- Automatically lists all benchmark files matching the pattern `benchmark_*.py`.
- Allows the user to select a specific benchmark or run all benchmarks.
- Dynamically imports and executes each benchmark module's `run()` function.

Each benchmark module must define a top-level `run()` function.

Usage:
    python benchmark_runner_select.py
"""

import importlib.util
import pathlib
import sys

# Always resolve relative to this script's location to allow the directory to be found
# whether running the in vscode or for the terminal
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
BENCHMARK_DIR = SCRIPT_DIR / "benchmarks"

def list_benchmarks():
    """
    Scans the benchmark directory for Python files matching the pattern 'benchmark_*.py'.

    Returns:
        List[pathlib.Path]: A sorted list of benchmark file paths.
    """
    return sorted(BENCHMARK_DIR.glob("benchmark_*.py"))

def load_and_run(file):
    """
    Dynamically loads a benchmark module and calls its `run()` function.

    Args:
        file (pathlib.Path): The path to the benchmark script.

    Behavior:
        - Imports the script as a module.
        - Checks for a callable `run()` function.
        - If present, executes it.
        - Logs appropriate messages for errors or missing functions.
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

def prompt_user_choice(benchmark_files):
    """
    Prompts the user to select a benchmark from a numbered list or choose to run all.

    Args:
        benchmark_files (List[pathlib.Path]): List of benchmark script paths.

    Returns:
        Union[str, pathlib.Path]: "ALL" if user selected all, or the selected benchmark file.
    """
    print("\nAvailable Benchmarks:\n")
    print("  1. All")  # Option to run all benchmarks
    for idx, file in enumerate(benchmark_files, start=2):
        print(f"  {idx}. {file.name}")
    
    print("\nSelect a benchmark to run (number), or 'q' to quit:")
    while True:
        choice = input("> ").strip()
        if choice.lower() in {'q', 'quit', 'exit'}:
            print("Exiting.")
            sys.exit(0)

        if choice.isdigit():
            index = int(choice)
            if index == 1:
                return "ALL"
            elif 2 <= index <= len(benchmark_files) + 1:
                return benchmark_files[index - 2]

        print("Invalid input. Please enter a valid number or 'q' to quit.")

def main():
    """
    Main entry point.

    - Lists available benchmark scripts.
    - Prompts the user to choose one or all.
    - Loads and runs the selected benchmark(s).
    """
    benchmark_files = list_benchmarks()
    if not benchmark_files:
        print("No benchmark files found in the directory.")
        return

    selected = prompt_user_choice(benchmark_files)

    if selected == "ALL":
        for file in benchmark_files:
            load_and_run(file)
    else:
        load_and_run(selected)

if __name__ == "__main__":
    main()
