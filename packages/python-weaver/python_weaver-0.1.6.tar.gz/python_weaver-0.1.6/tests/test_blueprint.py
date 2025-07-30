import sqlite3
import pandas as pd
import tempfile
import os
import pytest

from weaver.blueprint import Blueprint
from weaver.exceptions import DatabaseError

@pytest.fixture
def bp(tmp_path):
    db = tmp_path / "test.db"
    return Blueprint(str(db))

def test_add_and_get_task(bp):
    tid = bp.add_task(
        task_name="T1",
        llm_config_key="gpt-4o-mini",
        prompt_template="Do X",
    )
    rec = bp.get_task(tid)
    assert rec["task_name"] == "T1"
    assert rec["status"] == "pending"
    assert rec["prompt_template"] == "Do X"

def test_update_and_status(bp):
    tid = bp.add_task("T2", "gpt-4o-mini", "Do Y")
    bp.update_task_status(tid, "in_progress")
    assert bp.get_task(tid)["status"] == "in_progress"

def test_dependency_resolution(bp):
    # Task 1 (no deps), Task 2 depends on 1
    t1 = bp.add_task("T1", "gpt-4o-mini", "A")
    t2 = bp.add_task("T2", "gpt-4o-mini", "B", dependencies=str(t1))
    # Only t1 is ready
    next1 = bp.get_next_pending_task()
    assert next1["task_id"] == t1
    # Mark t1 complete
    bp.update_task_status(t1, "completed")
    next2 = bp.get_next_pending_task()
    assert next2["task_id"] == t2

def test_to_from_csv(tmp_path, bp):
    # Add two tasks
    tid1 = bp.add_task("T1", "gpt-4o-mini", "A")
    tid2 = bp.add_task("T2", "gpt-4o-mini", "B", dependencies=str(tid1))
    csvf = tmp_path / "bp.csv"
    bp.to_csv(str(csvf))
    # Edit CSV: change T2 name
    df = pd.read_csv(csvf)
    df.loc[df.task_id == tid2, "task_name"] = "T2-mod"
    df.to_csv(csvf, index=False)
    # Import and check
    bp.import_from_csv(str(csvf))
    assert bp.get_task(tid2)["task_name"] == "T2-mod"

def test_update_from_df_rollback(bp):
    # Simulate malformed DataFrame (missing task_id)
    df = pd.DataFrame([{"foo": "bar"}])
    with pytest.raises(Exception):
        bp.update_from_df(df)
