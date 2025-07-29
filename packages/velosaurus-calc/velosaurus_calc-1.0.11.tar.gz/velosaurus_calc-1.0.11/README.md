# Python DevOps Sample Project

This repository was created for a Grad­u­ate Sem­i­nar at the [Department of Atmospheric and Cryospheric Sciences (ACINN)](https://www.uibk.ac.at/en/acinn/) in Innsbruck on May 8th 2024. It serves as a dummy [PyPI package](https://pypi.org/project/velosaurus-calc/) to demonstrate some modern DevOps practices.

- Collaboration (Scrum)
- AI supported development
- Git / PR / Code Review
- CI/CD (Pipelines / IaC)
- UnitTests / Static Linter

## Prerequisites

### Setup Python Environment

```bash
# Create/activate/deactivate venv
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux
.\venv\Scripts\deactivate

# Install packages with activated env and check
python -m pip install --upgrade pip
pip install --upgrade -r ./requirements.txt 
```

## Unit Testst

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Generate and test python package locally

```bash
python setup.py sdist bdist_wheel
pip install dist/velosaurus_sum-1.0.4-py3-none-any.whl
```

## Tools

- ruff (linter, formatter)
- mypy (type annotation linter)
  - if **Extension** installed, add rule: Search for mypy in Settings and ad "Mypy-type-checker args": ``"python.linting.mypyArgs": [     "--ignore-missing-imports" ]``
- autoDocstring - Python Docstring Generator

todo:

- pytest and coverage
- pre-commit instead pipeline test/linter runs

### ruff and mypy

Tools can be applied manualle in console or automatically in pipeline on commit/PR. Configuration for manual/local usage is done in **settings.json**. Configuration for pipeline/build-tool usage is done via **pyproject.toml**.

Use Ruff instead of flake8 (linter), black (formatter) and isort (import sorter) separately.

- **ruff** (linter / formatter)
  - `ruff check .`   ...basic check (linter)
  - `ruff check --fix .` ...fix basic issues (linter)
  - `ruff format --diff .` (show diffs)
  - `ruff format --check .` (show files)
  - `ruff format .` (apply formatter)

- **mypy** (static type annotations)
  - `mypy --exclude venv .`

## Pipelines (Workflows)

- The overall automation process, defined in a YAML file, that runs on certain triggers (like push, pull request, etc.).
- e.g. `python-linting.yml` file defines a pipeline (workflow).

### Hierarchy in Github

**In GitHub Actions, there are no native "stages"** like in Azure DevOps or GitLab CI.  
The highest hierarchy in a workflow is:

- **Workflow** (the whole YAML file, sometimes called a pipeline)
  - **Jobs** (can run in parallel or in sequence using `needs`)
    - **Steps** (run sequentially within a job)

If you want to mimic "stages," you use multiple jobs and control their order with the `needs:` keyword. But officially, **jobs** are the top-level execution units inside a workflow.

### **Runner**

- **Definition:** A server (virtual machine or container) that executes your workflow jobs.
- **Example:** `runs-on: ubuntu-latest` tells GitHub to use an Ubuntu runner.

---

### **Job**

- **Definition:**
  - A set of steps that run sequentially on the same runner.
  - Multiple jobs in one pipeline (workflow) can run in parallel (unless you specify dependencies between them).
  - Each job can specify its own runner using the runs-on key.
  - By default, jobs run on separate runners (virtual machines or containers), which allows them to run in parallel and in isolated environments.
- **Example:** Your `lint` job runs all the steps (checkout, setup Python, install, test, lint).

---

### **Action**

- **Definition:** A reusable unit of code that performs a specific task in a workflow step.
- **Example:** `actions/checkout@v2` is an action that checks out your code.

---

| Term     | GitHub Actions Example         | Description                                   |
|----------|-------------------------------|-----------------------------------------------|
| Runner   | `runs-on: ubuntu-latest`      | Where jobs run                                |
| Action   | `actions/checkout@v2`         | Reusable step/task                            |
| Pipeline | `.github/workflows/*.yml`     | The whole workflow process                    |
| Stage    | (Not native, use jobs)        | Logical phase (build/test/deploy)             |
| Job      | `jobs: lint:`                 | Group of steps on one runner                  |
