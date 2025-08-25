# Digital Forensics Agent Part 1 - Group Project - Project Proposal

This project contains shared benchmarking tools and agent prototypes for the *Intelligent Agents* group project.


## Project Structure

```
IA-GROUP-E/
├── proposal/                       # Shared experiments, benchmarks, and utilities
│   ├── benchmarks/                 # Performance tests for libraries and approaches
│   │   └── mock_data/              # Mock data for shared testing
│   ├── agents/                     # Agent prototypes
│   ├── benchmark_runner.py         # Benchmark runner helper with CLI support
│   └── benchmark_runner_select.py  # Benchmark runner with interactive selection
│
├── project/                        # For individual projects after forking the repo
│
├── requirements.txt                # Python dependencies
└── README.md                       # You're reading it!
```

Feel free to add to this structure but remember to update this file to keep everyting documented.


## Getting Started

Follow these steps to set up the project correctly on your machine.

### Prerequisites

- Python 3.11+ installed
- VS Code installed (optional, but recommended)

### Step 1: Clone the project

```bash
git clone https://github.com/jaco-uoeo/ia-group-e.git
```

### Step 2: Create a Virtual Environment

Open a terminal in the root project folder (where this README.md file is located) and run:

```bash
cd ia-group-e
python -m venv venv
```

This will create a folder named `venv/` containing your isolated Python environment.



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



Once the virtual environment is activated, install the required libraries:

```bash
pip install -r requirements.txt && pip install -r requirements_deps.txt
```
- requirements.txt: Contains the main dependencies for the project.
- requirements_deps.txt: Contains dependencies that must be installed after those in requirements.txt (required since pip does not guarantee installation order).
- Always install requirents.txt first, then requirements_deps.txt.

If new packages are needed later, install them and then update the `requirements.txt` file.

#### Option 1: Using pip (simple and common)

```bash
pip install pandas
pip freeze > requirements.txt
```

> **Note:** This captures *all installed packages*, including indirect ones. It's easy, but may include more than you expect. You may need to move some packages to requirements_deps.txt to maintain dependencies. 

#### Option 2: Using `uv` (recommended for curated dependencies)

If you're using [`uv`](https://github.com/astral-sh/uv), make sure to regenerate `requirements.txt` from your `pyproject.toml` to keep the dependency list clean and reliable:

```bash
uv pip compile pyproject.toml -o requirements.txt
```

> **Team Note:** `requirements.txt` should remain the single source of truth for group development since not everyone may be comfortable using uv.  
> If you use `uv` locally, **always export updates to `requirements.txt` before committing or sharing**.

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

Now, VS Code will use the virtual environment you set up. Ther


## Running Benchmarks

To run benchmarks, navigate to the `proposal` directory and use one of the following commands:

```bash
cd proposal
```

There are three ways to run benchmarks, to simply run all benchmarks in sequence:
```bash
python benchmark_runner.py
```
To run a specific benchmark:
```bash
python benchmark_runner.py --run benchmark_pathlib
```
> **Note:** Replace benchmark_pathlib with the name of the specific benchmark you want to run.

And finally, via interactive selection:
```bash
python benchmark_runner_select.py
```

## Adding Your Own Benchmark

To add a new benchmark:

1. Create a new file in `proposal/benchmarks/`, e.g. `benchmark_new_approach.py`
2. Define a `run()` function inside it.
3. Code your benchmark. 
3. Run `benchmark_runner.py`

Hava a look at the an existing benchmark file for an example.


## Team Contribution Guidelines

- Only edit files inside `proposal/` when working on shared experiments during the group project.
- The `project/` folder is just a **placeholder** to show where your individual project artifacts might go.
- **Do not** work on your final project inside this shared repository.
- Once the group project is complete, **fork this repository** and use your fork for your individual project.
- You are free to:
  - Keep the existing folder structure.
  - Rename or restructure folders to suit your final vision and goals.
  - Remove unused files or modules as needed.

This approach keeps the group collaboration clean and gives each team member full flexibility for their final submission.


## Git Workflow (No Pull Requests)

This project does not use pull requests — changes are merged directly into `main` after benchmarking.

### Step-by-step:

```bash
# Clone the repository
git clone <repo-url>
cd <repo-directory>

# Create a new feature branch
git checkout -b feature/my-new-feature

# Add and commit your changes
git add .
git commit -m "Added benchmark for xyz"

# Push your feature branch to remote
git push origin feature/my-new-feature

# Merge the feature branch into main
git checkout main
git pull origin main        
git merge feature/my-new-feature
git push origin main

# (Optional) Delete the feature branch
git branch -d feature/my-new-feature
git push origin --delete feature/my-new-feature
```
Or just use [GitHub Desktop](https://docs.github.com/en/desktop) for a nice GUI experience.

## .gitignore

This project excludes the following from Git commits:

```
__pycache__/
*.pyc
.env
.venv
venv
.vscode/
.idea/
```

If you create personal data folders that you don't need to share with the group, feel free to add it to the ignore file so that it's not committed to the shared repository.


## Need Help?

Don’t hesitate to ask teammates if you get stuck. This repo is built to help you experiment, learn, and contribute effectively.
