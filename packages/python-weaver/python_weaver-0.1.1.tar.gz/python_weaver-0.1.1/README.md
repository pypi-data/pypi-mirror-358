[![PyPI version](https://img.shields.io/pypi/v/python-weaver.svg)](https://pypi.org/project/python-weaver)
<lr>

# python-weaver

_python-weaver_ is an open-source Python framework designed to enable Large Language Models (LLMs) to execute complex, long-duration tasks by orchestrating workflows through a persistent, human-editable task tracker called the **Blueprint**.
<lr>
## Architecture Diagram
![Architecture Diagram](architecture.png)



## Features

- **Stateful & Resumable**: All project state is stored in a local SQLite database (built into Python), ensuring no work is lost.
- **Human-in-the-Loop**: Users can review, edit, and approve task plans and results via a CSV export/import.
- **Local-First Security**: All data remains on your machine.
- **Modular & Unopinionated**: Model-agnostic orchestration via `litellm`, customizable connectors.
- **Extreme Robustness**: Comprehensive error handling and retry logic at every step.

## Installation

```bash
pip install python-weaver
```

## Quick Start

```python
from weaver.project import Project

project = Project(
    project_name="my_long_task",
    project_goal="Generate a detailed report on climate change impacts across different regions."
)

# Ingest sources (PDFs, URLs, local docs)
project.ingest(["sources/report.pdf", "sources/article.txt"])

# Plan and review tasks
project.plan()
# Edit the generated blueprint.csv if needed

# Run tasks with human feedback between steps
project.run(human_feedback=True)
```

## Development & Testing

```bash
pip install -e .[dev]
pytest
```

````

## Package Structure

```text
python-weaver/
├── weaver/
│   ├── __init__.py
│   ├── cli.py               # CLI entrypoint stub
│   ├── project.py           # Main user-facing class
│   ├── blueprint.py         # SQLite-backed task tracker
│   ├── agent.py             # The LLM-powered executor
│   ├── config.py            # LLM configurations
│   ├── exceptions.py        # Custom exceptions
│   └── connectors/
│       ├── __init__.py
│       ├── base_connector.py
│       ├── pdf_reader.py
│       └── url_scraper.py
├── tests/
│   ├── test_project.py
│   └── test_blueprint.py
├── examples/
│   └── simple_report_generation.py
├── setup.py                 # Packaging
├── requirements.txt
└── README.md
````
