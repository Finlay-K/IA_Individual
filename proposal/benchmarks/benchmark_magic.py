import time
import magic
from pathlib import Path
from collections import defaultdict

# Always resolve relative to this script's location to allow the directory to be found
# whether running the in vscode or for the terminal
SCRIPT_DIR = Path(__file__).resolve().parent
SCAN_DIR = SCRIPT_DIR / "mock_data"

def run():
    ms = magic.Magic()    

    start = time.time()
    extensions = (".pdf", ".docx", ".txt")
    directory = Path(SCAN_DIR)
    matching_files = find_files_by_extension(directory, extensions)

    ext_counts = defaultdict(int)
    for file in matching_files:
        ext = file.suffix.lower()
        ext_counts[ext] += 1
        print(f"{file.name}: {ms.from_file(str(file))}")

    end = time.time()

    print("\nSummary:")
    for ext in extensions:
        print(f"  {ext}: {ext_counts[ext]} file(s)")

    print(f"\nFound {len(matching_files)} files using pathlib in {end - start:.4f} seconds")


def find_files_by_extension(directory: Path, extensions: tuple):
    return [p for p in directory.rglob("*") if p.suffix in extensions]


if __name__ == "__main__":
    run()