import pytest
from unittest.mock import patch
from weaver.agent import Agent
from weaver.blueprint import Blueprint
from weaver.exceptions import AgentError

class DummyResponse:
    def __init__(self, content, usage):
        self.choices = [{"message": {"content": content}}]
        self.usage = usage

    def get(self, k, default=None):
        if k == "usage":
            return self.usage
        return default

@pytest.fixture
def bp(tmp_path, monkeypatch):
    db = tmp_path / "a.db"
    return Blueprint(str(db))

def test_execute_success(tmp_path, bp, monkeypatch):
    # Add a simple task
    tid = bp.add_task("T", "gpt-4o-mini", "Hello")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    # Mock LLM
    dummy = DummyResponse("OK", {"prompt_tokens": 10, "completion_tokens": 5})
    with patch("litellm.completion", return_value={"choices": [{"message": {"content": "OK"}}], "usage": {"prompt_tokens": 10, "completion_tokens": 5}}):
        agent = Agent(bp, project_goal="G")
        agent.execute_task(tid)
    rec = bp.get_task(tid)
    assert rec["status"] == "awaiting_human_approval"
    assert rec["raw_result"] == "OK"
    assert rec["parsed_result"] == "OK"
    assert rec["cost"] > 0

def test_execute_failure(tmp_path, bp, monkeypatch):
    tid = bp.add_task("T", "gpt-4o-mini", "Hello")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    # Mock LLM to always raise
    def bad(*args, **kw): raise RuntimeError("API down")
    with patch("litellm.completion", side_effect=bad):
        agent = Agent(bp, project_goal="G")
        with pytest.raises(AgentError):
            agent.execute_task(tid)
    rec = bp.get_task(tid)
    assert rec["status"] == "failed"
    assert rec["retry_count"] == 1
    assert "API down" in rec["error_log"]
