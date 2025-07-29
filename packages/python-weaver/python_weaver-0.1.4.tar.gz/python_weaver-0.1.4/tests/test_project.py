import pytest
import json
from pathlib import Path
from weaver.project import Project
from weaver.exceptions import WeaverError
from unittest.mock import patch

@pytest.fixture
def tmp_project(tmp_path):
    proj_dir = tmp_path / "proj"
    yield str(proj_dir)

def test_init_and_meta(tmp_project):
    p = Project(tmp_project, project_goal="Goal")
    meta = json.loads(Path(tmp_project, "project.json").read_text())
    assert meta["project_goal"] == "Goal"
    # Re-loading should not error
    p2 = Project(tmp_project)
    assert p2.project_goal == "Goal"

def test_ingest_and_plan(tmp_project, monkeypatch):
    # Prepare a fake text file
    src = tmp_path = Path(tmp_project)
    Path(tmp_project).mkdir()
    txt = Path(tmp_project) / "sample.txt"
    txt.write_text("DATA")
    p = Project(tmp_project, project_goal="G")
    p.ingest([str(txt)])
    # Monkey-patch LLM completion to return a simple plan
    fake_plan = {
        "tasks": [
            {"name": "A", "prompt_template": "Do A", "dependencies": []}
        ]
    }
    def fake_completion(*args, **kwargs):
        return {"choices":[{"message":{"content":json.dumps(fake_plan)}}]}
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with patch("litellm.completion", side_effect=fake_completion):
        p.plan()
    # Blueprint CSV should exist
    assert (Path(tmp_project) / "blueprint.csv").exists()
    # And one pending task in DB
    tasks = p.blueprint._execute_query("SELECT COUNT(*) FROM tasks", [], fetch="one")[0]
    assert tasks == 1

def test_run_with_steps(tmp_project, monkeypatch):
    # Create project + blueprint manually
    p = Project(tmp_project, project_goal="G")
    p.blueprint.add_task("A", "gpt-4o-mini", "Hello")
    # Stub Agent.execute_task to just mark task complete
    class DummyAgent:
        def __init__(self, b, g):
            self.b = b
        def execute_task(self, tid):
            self.b.update_task_status(tid, "awaiting_human_approval")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr("weaver.project.Agent", DummyAgent)
    p.run(human_feedback=False, steps=1)
    rec = p.blueprint.get_task(1)
    assert rec["status"] == "completed"
