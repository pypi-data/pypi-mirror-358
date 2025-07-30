import json
import shutil
import re
from pathlib import Path
import litellm

from weaver.blueprint import Blueprint
from weaver.agent import Agent
from weaver.config import LLM_CONFIG, get_model_config
from weaver.exceptions import WeaverError
from weaver.connectors.pdf_reader import PDFReader
from weaver.connectors.url_scraper import URLScraper  
from weaver.connectors.base_connector import BaseConnector


def extract_json_from_response(content: str) -> str:
    """
    Extract JSON from LLM response, handling markdown code blocks and other formatting.
    
    Args:
        content: Raw LLM response content
        
    Returns:
        Cleaned JSON string ready for parsing
        
    Raises:
        ValueError: If no valid JSON is found
    """
    # First, try to find JSON within markdown code blocks
    json_block_patterns = [
        r'```json\s*\n(.*?)\n```',  # ```json ... ```
        r'```\s*\n(.*?)\n```',      # ``` ... ``` (generic code block)
        r'`(.*?)`',                  # Single backticks
    ]
    
    for pattern in json_block_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            try:
                # Test if this match is valid JSON
                json.loads(match.strip())
                return match.strip()
            except json.JSONDecodeError:
                continue
    
    # If no code blocks found, try to extract JSON from the raw content
    # Look for content between { and } (handling nested braces)
    brace_count = 0
    start_idx = None
    
    for i, char in enumerate(content):
        if char == '{':
            if start_idx is None:
                start_idx = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_idx is not None:
                potential_json = content[start_idx:i+1]
                try:
                    json.loads(potential_json)
                    return potential_json
                except json.JSONDecodeError:
                    # Reset and continue looking
                    start_idx = None
                    brace_count = 0
    
    # If still no valid JSON found, try the entire content as-is
    try:
        json.loads(content.strip())
        return content.strip()
    except json.JSONDecodeError:
        pass
    
    raise ValueError(f"No valid JSON found in response. Content preview: {content[:200]}...")


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

        # 2) Get orchestrator model configuration
        orchestrator_key = LLM_CONFIG["main_orchestrator"]
        orchestrator_config = get_model_config(orchestrator_key)
        orchestrator_model = orchestrator_config["model"]

        # 3) Build planning prompt with more explicit JSON instructions
        planning_prompt = f"""
You are an expert project planner. You must respond with valid JSON only.

Project Goal:
{self.project_goal}

Sources:
{combined_sources}

Create a step-by-step plan to achieve the project goal. Return ONLY valid JSON in this exact format:

{{
  "tasks": [
    {{
      "name": "Task title",
      "prompt_template": "Instructions for this task",
      "dependencies": [0, 1]
    }},
    {{
      "name": "Another task",
      "prompt_template": "Instructions for another task",
      "dependencies": []
    }}
  ]
}}

Important:
- The "dependencies" array contains zero-based indices of prior tasks that must complete first
- Use empty array [] if no dependencies
- Return ONLY the JSON, no explanations or markdown formatting
"""

        # 4) Call LLM using litellm
        try:
            resp = litellm.completion(
                model=orchestrator_model,
                messages=[{"role": "user", "content": planning_prompt}],
                max_tokens=orchestrator_config.get("max_tokens", 2000)
            )
            raw_content = resp["choices"][0]["message"]["content"]
        except Exception as e:
            raise WeaverError(f"Failed to call orchestrator LLM: {e}")

        # 5) Extract and parse JSON from response
        try:
            json_content = extract_json_from_response(raw_content)
            plan = json.loads(json_content)
            tasks = plan["tasks"]
        except ValueError as e:
            raise WeaverError(f"Failed to extract JSON from LLM response: {e}")
        except json.JSONDecodeError as e:
            raise WeaverError(f"Failed to parse plan JSON: {e}")
        except KeyError as e:
            raise WeaverError(f"Invalid plan structure - missing 'tasks' key: {e}")

        # 6) Validate plan structure
        if not isinstance(tasks, list):
            raise WeaverError("Plan 'tasks' must be a list")
        
        for idx, task in enumerate(tasks):
            required_keys = ["name", "prompt_template"]
            for key in required_keys:
                if key not in task:
                    raise WeaverError(f"Task {idx} missing required key: {key}")
            
            # Ensure dependencies is a list
            if "dependencies" not in task:
                task["dependencies"] = []
            elif not isinstance(task["dependencies"], list):
                raise WeaverError(f"Task {idx} 'dependencies' must be a list")

        # 7) Populate blueprint (1-based task_ids)
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

        # 8) Export for human editing
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
                input(f"[WEAVER] Task {task_id} complete. Edit blueprint.csv and press Enter to continue…")
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