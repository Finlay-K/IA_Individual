# Digital Forensics Agent Part 2 - Individual Project

This repository contains benchmarking tools and prototype agents for the Digital Forensics Agent project in the Intelligent Agents module. It is intended for experimentation with file-type detection, metadata extraction, and learning-based classification.

benchmark_forensic_AI.py is a Python-based intelligent agent designed to automatically identify, copy, and audit files (specifically images) from one or more source directories.
The agent analyses each file’s MIME type, extension, and optional metadata before copying matching files to a structured destination directory. It also generates a CSV audit log recording all processed files, their SHA-256 hashes, sizes, and metadata.

### Prerequisites

- Python 3.11+ installed
- VS Code installed (optional, but recommended)

### Directory Structure

By default, the agent uses:
| Path            | Description                                          |
| --------------- | ---------------------------------------------------- |
| `DEFAULT_ROOTS` | Source folder(s) to scan for matching files          |
| `DEFAULT_DEST`  | Destination folder for copied files and audit logs   |
| `DEFAULT_RULES` | Defines file types to match — e.g. all image formats |

These locations should be amended to suit the user and their requirements

Example (default configuration in code):
```bash
C:\Users\Finn\OneDrive\Documents\Masters\Module 4 - IA\Drive
│
└── [Agent scans this directory recursively]
```

Copies and logs will be created under:
```bash
C:\Users\Finn\OneDrive\Documents\Masters\Module 4 - IA\IA_Copy
│
├── All images
│   └── [Original folder structure preserved]
│
└── audit_XXXXXXXX.csv
```

### Step 1: Clone the project

```bash
git clone https://github.com/Finlay-K/IA_Individual.git
```

### Step 2: Create a Virtual Environment

Open a terminal in the root project folder (where this README.md file is located) and run:

```bash
cd IA_Individual
python -m venv venv
```

This will create a folder named `venv/` containing the Python environment.



### Step 3: Activate the Virtual Environment

**On Windows (Command Prompt):**

```bash
venv\Scripts\activate
```

**On Windows (PowerShell):**

```bash
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**

```bash
source venv/bin/activate
```

You should now see `(venv)` at the start of your terminal prompt. This means the virtual environment is active.


### Step 4: Install Dependencies

The following Python packages are required:

```bash
pip install pillow exifread python-magic
```

Note:
On Windows, use python-magic-bin instead of python-magic:

```bash
pip install pillow exifread python-magic-bin
```


### Step 5: Install shared libraries on Linux
The `libmagic` library is required by `python-magic` and may need to be installed on Linux or macOS. Installation steps vary depending on your OS or Linux distribution, for example, on Debian, Ubuntu, or Linux Mint:
```bash
sudo apt update && sudo apt install libmagic1
```

Its located in `file-libs` on Fedora and CentOS and is part of the `file` package on Nix and Arch.


### Step 6: (Optional) Using the Virtual Environment in VS Code

If you're using **VS Code**:

1. Open the root folder in VS Code.
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS).
3. Search for and select: `Python: Select Interpreter`.
4. Choose the interpreter that starts with `.venv` or `./venv` (usually labelled as recommended).

Now, VS Code will use the virtual environment set up

### Example: Dry Run 
### (user must copy in their own directory path)
```bash
python benchmark_forensic_AI.py "ROOT\FILE\PATH\HERE" `
  --dest "DEST\FILE\PATH\HERE" `
  --dry-run
```
No files are copied — only a log of intended actions is created.

### For a full run
### (user must copy in their own directory path)
This will copy all discovered images and keep folder structure intact
```bash
cd "ROOT\FILE\PATH\HERE"
python benchmark_forensic_AI.py "ROOT\FILE\PATH\HERE" `
  --dest "DEST\FILE\PATH\HERE" `
```

### Audit Log Format

Each execution produces an audit CSV file in the destination directory:
| Column      | Description                                   |
| ----------- | --------------------------------------------- |
| `time`      | UTC timestamp of processing                   |
| `rule`      | Name of rule triggered (e.g. “All images”)    |
| `src`       | Original source file path                     |
| `mime`      | Detected MIME type                            |
| `ext`       | File extension                                |
| `sha256`    | File hash for integrity verification          |
| `size`      | File size in bytes                            |
| `copied_to` | Destination path or `(dry-run)` if not copied |
| `metadata`  | JSON-formatted extracted metadata             |


### Summary

This intelligent agent provides a proof of concept for automated digital asset retrieval using rule-based logic and basic metadata reasoning.
It can be easily extended to other file types, complex metadata searches, or integrated into multi-agent systems for more advanced autonomous workflows.

