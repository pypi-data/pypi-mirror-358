# weaver/project.py

import json
import shutil
from pathlib import Path
from litellm import completion as llm_completion

from weaver.blueprint import Blueprint
from weaver.agent import Agent
from weaver.config import LLM_CONFIG
from weaver.exceptions import WeaverError
from weaver.connectors.pdf_reader import PDFReader
from weaver.connectors.url_scraper import URLScraper  
from weaver.connectors.base_connector import BaseConnector


class Project:
    def __init__(self, project_name: str, project_goal: str = None):
        """
        If project_goal is provided, create a new project directory
        and write project.json. Otherwise, load existing metadata.
        """
        self.project_name = project_name
        self.project_dir = Path(project_name)
        self.db_path = self.project_dir / f"{project_name}.db"
        self.sources_dir = self.project_dir / "sources"
        self.results_dir = self.project_dir / "results"
        self.meta_path = self.project_dir / "project.json"

        if project_goal is not None:

            # Only error if metadata already exists
            if self.meta_path.exists():
                raise WeaverError(f"Project metadata file '{self.meta_path}' already exists.")
            
            self.project_dir.mkdir(exist_ok=True)
            self.sources_dir.mkdir()
            self.results_dir.mkdir()
            # Save metadata
            with self.meta_path.open("w", encoding="utf-8") as f:
                json.dump({"project_goal": project_goal}, f, indent=2)
            self.project_goal = project_goal
        else:
            # Load existing project
            if not self.project_dir.exists():
                raise WeaverError(f"Project '{project_name}' not found.")
            if not self.meta_path.exists():
                raise WeaverError(f"Missing project metadata at '{self.meta_path}'.")
            data = json.loads(self.meta_path.read_text(encoding="utf-8"))
            self.project_goal = data.get("project_goal")
            # ensure subdirs exist
            self.sources_dir.mkdir(exist_ok=True)
            self.results_dir.mkdir(exist_ok=True)

        # Initialize blueprint
        self.blueprint = Blueprint(str(self.db_path))

    def ingest(self, sources: list[str]):
        """
        Ingest each source (URL or local file path) into sources_dir.
        Saves plain-text .txt files named 1.txt, 2.txt, ...
        """
        for src in sources:
            # choose connector
            if src.startswith("http://") or src.startswith("https://"):
                connector: BaseConnector = URLScraper()
                name = Path(src).name or "url"
            else:
                ext = Path(src).suffix.lower()
                if ext == ".pdf":
                    connector = PDFReader()
                else:
                    # treat as plain text file copy
                    shutil.copy(src, self.sources_dir / Path(src).name)
                    continue
                name = Path(src).stem

            try:
                text = connector.ingest(src)
            except Exception as e:
                raise WeaverError(f"Failed to ingest '{src}': {e}")

            # write to sources_dir
            out_path = self.sources_dir / f"{name}.txt"
            out_path.write_text(text, encoding="utf-8")

    def plan(self):
        """
        Uses the orchestrator LLM to generate a JSON list of tasks,
        then populates the blueprint and writes blueprint.csv.
        """
        # 1) Combine all sources
        texts = []
        for txt in sorted(self.sources_dir.glob("*.txt")):
            texts.append(txt.read_text(encoding="utf-8"))
        combined_sources = "\n\n".join(texts)

        # 2) Build planning prompt
        orchestrator_key = LLM_CONFIG["main_orchestrator"]
        orchestrator_model = LLM_CONFIG["available_llms"][orchestrator_key]["model"]

        planning_prompt = f"""
You are an expert project planner.

Project Goal:
{self.project_goal}

Sources:
{combined_sources}

Please output JSON in the format:

{{
  "tasks": [
    {{
      "name": "Task title",
      "prompt_template": "Instructions for this task",
      "dependencies": [0, 1]     # zero-based indices of prior tasks
    }},
    ...
  ]
}}
"""

        # 3) Call LLM
        resp = llm_completion(
            model=orchestrator_model,
            prompt=planning_prompt,
            max_tokens=2000
        )
        content = resp["choices"][0]["message"]["content"]
        try:
            plan = json.loads(content)
            tasks = plan["tasks"]
        except Exception as e:
            raise WeaverError(f"Failed to parse plan JSON: {e}")

        # 4) Populate blueprint (1-based task_ids)
        llm_keys = list(LLM_CONFIG["available_llms"].keys())
        for idx, task in enumerate(tasks, start=1):
            deps = ",".join(str(d + 1) for d in task.get("dependencies", []))
            # round-robin assignment
            key = llm_keys[(idx - 1) % len(llm_keys)]
            self.blueprint.add_task(
                task_name=task["name"],
                llm_config_key=key,
                prompt_template=task["prompt_template"],
                dependencies=deps
            )

        # 5) Export for human editing
        self.blueprint.to_csv(str(self.project_dir / "blueprint.csv"))

    def run(self, human_feedback: bool = True, steps: int = 0):
        """
        Execute tasks in sequence. If human_feedback, pause after each
        for CSV edits. Writes per-task results to results/<task_id>.txt and
        at the end compiles final_result.md from all parsed_results.
        """
        count = 0
        while True:
            if steps and count >= steps:
                break

            next_task = self.blueprint.get_next_pending_task()
            if next_task is None:
                break

            task_id = next_task["task_id"]
            agent = Agent(self.blueprint, self.project_goal)
            agent.execute_task(task_id)

            # write per-task result file
            record = self.blueprint.get_task(task_id)
            raw = record.get("raw_result") or ""
            (self.results_dir / f"{task_id}.txt").write_text(raw, encoding="utf-8")

            # human feedback loop
            if human_feedback:
                csv_path = self.project_dir / "blueprint.csv"
                self.blueprint.to_csv(str(csv_path))
                input(f"[WEAVER] Task {task_id} complete. Edited blueprint.csv and press Enter to continue…")
                try:
                    self.blueprint.import_from_csv(str(csv_path))
                except Exception as e:
                    print(f"[WEAVER] WARNING: Invalid CSV: {e}. Continuing with last valid state.")

            # mark completed
            self.blueprint.update_task_status(task_id, "completed")
            count += 1

        # compile final_result.md
        final_lines = []
        for row in sorted(self.blueprint._execute_query(
                "SELECT task_id, parsed_result FROM tasks WHERE status='completed' ORDER BY task_id",
                params=[], fetch="all"
            )):
            tid, parsed = row
            final_lines.append(f"## Task {tid}\n\n{parsed}\n")
        (self.results_dir / "final_result.md").write_text("\n".join(final_lines), encoding="utf-8")
