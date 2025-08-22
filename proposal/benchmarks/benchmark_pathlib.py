from pathlib import Path
import time

# Always resolve relative to this script's location to allow the directory to be found
# whether running the in vscode or for the terminal
SCRIPT_DIR = Path(__file__).resolve().parent
SCAN_DIR = SCRIPT_DIR / "mock_data"

def run():
    start = time.time()
    extensions = (".pdf", ".docx", ".txt")
    matching_files = find_files_by_extension(Path(SCAN_DIR), extensions)
    end = time.time()
    print(f"Found {len(matching_files)} files using pathlib in {end - start:.4f} seconds")

def find_files_by_extension(directory: Path, extensions: tuple):
    return [p for p in directory.rglob("*") if p.suffix in extensions]

if __name__ == "__main__":
    run()