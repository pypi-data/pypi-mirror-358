"""
Agent: Executes individual tasks via an LLM, handling retries and updating the Blueprint.
"""
import time
from datetime import datetime
import litellm
from weaver.config import get_model_config
from weaver.exceptions import AgentError

class Agent:
    def __init__(self, blueprint, project_goal: str):
        """
        blueprint: an instance of weaver.blueprint.Blueprint
        project_goal: the overall goal of the project, used in prompts
        """
        self.blueprint = blueprint
        self.project_goal = project_goal

    def _build_prompt(self, task_record: dict) -> str:
        """
        Construct the final prompt by combining:
          1. The project goal
          2. Parsed results from any dependency tasks
          3. This task's own prompt template
        """
        parts = [f"Project Goal: {self.project_goal}\n"]

        deps = task_record.get("dependencies")
        if deps:
            for dep_id in deps.split(","):
                dep_id = dep_id.strip()
                if dep_id:  # skip empty strings
                    try:
                        # Handle both integer and float strings
                        dep_id_int = int(float(dep_id))
                        dep = self.blueprint.get_task(dep_id_int)
                        parsed = dep.get("parsed_result")
                        if parsed:
                            parts.append(f"Dependency {dep_id_int} result:\n{parsed}\n")
                    except (ValueError, TypeError):
                        print(f"[weaver] Warning: Invalid dependency ID '{dep_id}', skipping.")
                        continue

        parts.append(task_record.get("prompt_template", ""))
        return "\n".join(parts)

    def execute_task(self, task_id: int):
        """
        Execute the specified task:
          - Mark in_progress and record execution_start_timestamp
          - Build and send the prompt to the LLM, with up to 3 retries on failure
          - On success: record raw and parsed results, cost, execution_end_timestamp,
            then mark awaiting_human_approval.
          - On failure after retries: increment retry_count, log error, mark failed.
        """
        # 1) Mark in_progress and record start time
        start_ts = datetime.now().isoformat()
        self.blueprint.update_task_status(task_id, "in_progress")
        self.blueprint._execute_query(
            "UPDATE tasks SET execution_start_timestamp = ? WHERE task_id = ?",
            params=[start_ts, task_id],
            fetch=None
        )

        task = self.blueprint.get_task(task_id)
        prompt = self._build_prompt(task)
        model_cfg = get_model_config(task["llm_config_key"])

        # 2) Attempt LLM call with retries
        last_error = None
        response = None
        
        for attempt in range(1, 4):
            try:
                # Use litellm.completion with the model name directly
                # litellm handles provider routing and authentication
                response = litellm.completion(
                    model=model_cfg["model"],
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=model_cfg.get("max_tokens")
                )
                break
            except Exception as e:
                last_error = e
                print(f"[weaver] Task {task_id} attempt {attempt} failed: {e}")
                if attempt < 3:
                    time.sleep(2 ** attempt)  # exponential backoff
        else:
            # 3a) All retries failed: record failure
            err_msg = str(last_error)
            self.blueprint._execute_query(
                """
                UPDATE tasks
                SET retry_count = retry_count + 1,
                    error_log = COALESCE(error_log, '') || ?,
                    status = 'failed'
                WHERE task_id = ?
                """,
                params=[f"[{datetime.now().isoformat()}] {err_msg}\n", task_id],
                fetch=None
            )
            raise AgentError(f"Task {task_id} failed after 3 retries: {err_msg}")

        # 3b) Success path: compute cost, record end time, save results
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        # Calculate costs using the model's rate information
        rates = model_cfg.get("cost_per_1k_tokens", {})
        cost = (
            prompt_tokens / 1_000 * rates.get("prompt", 0) +
            completion_tokens / 1_000 * rates.get("completion", 0)
        )

        end_ts = datetime.now().isoformat()
        raw = (
            response.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
        )

        self.blueprint.update_task_execution_details(
            task_id=task_id,
            final_prompt=prompt,
            raw_result=raw,
            parsed_result=raw,
            cost=cost,
            execution_end_timestamp=end_ts
        )
        self.blueprint.update_task_status(task_id, "awaiting_human_approval")