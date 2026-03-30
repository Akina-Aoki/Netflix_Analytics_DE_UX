# Netflix Analytics (DE + UX)

This repository is a starter project for collaboration between the **UX Design** and **Data Engineering** teams to build analytics and visualization workflows for Netflix-related data.

---

## First-time setup (after cloning)

Use these steps if this is your first time cloning and running the project.

## Clone the repository

```bash
git clone <REPO_URL>
cd Netflix_Analytics_DE_UX
```

## Create a virtual environment

From the project root:

```bash
python3 -m venv .venv
```

This creates a local environment folder named `.venv` so dependencies are isolated from your global Python installation.

## Activate the virtual environment

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows (Command Prompt)

```cmd
.venv\Scripts\activate.bat
```

When activated, your terminal usually shows `(.venv)` at the start of the prompt.

## Upgrade pip (recommended)

```bash
python -m pip install --upgrade pip
```

## Install project dependencies

Install the package and all required dependencies from `pyproject.toml`:

```bash
pip install -e .
```

## Run the project

For the current starter script:

```bash
python main.py
```

Expected output:

```text
Hello from netflix-analytics-de-ux!
```

---

## Jupyter workflow (optional)

This project includes Jupyter/JupyterLab dependencies.

Start JupyterLab:

```bash
jupyter lab
```

Or start classic notebook:

```bash
jupyter notebook
```

To make this virtual environment selectable as a notebook kernel:

```bash
python -m ipykernel install --user --name netflix-analytics-de-ux --display-name "Python (.venv) Netflix Analytics"
```

---

# Daily workflow after first setup

Each time you open a new terminal:

```bash
cd Netflix_Analytics_DE_UX
source .venv/bin/activate   # use the Windows command if applicable
```

Then run your commands (examples):

```bash
python main.py
jupyter lab
```


---

## Troubleshooting

### `python3: command not found`

Try:

```bash
python --version
python -m venv .venv
```

