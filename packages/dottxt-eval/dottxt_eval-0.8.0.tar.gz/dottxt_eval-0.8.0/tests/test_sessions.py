from unittest.mock import patch

import pytest

from doteval.models import EvaluationResult, Sample, Score
from doteval.sessions import Session, SessionManager, SessionStatus
from doteval.storage import JSONStorage


def test_session_init():
    """Test that a session is initialized correctly."""
    session = Session(name="test_session")

    assert session.name == "test_session"
    assert session.results == {}
    assert session.metadata == {}
    assert isinstance(session.created_at, float)
    assert session.status == SessionStatus.running


def test_session_add_results():
    """Test adding results to a session."""
    session = Session(name="test_session")

    # Create test results
    score = Score("test_evaluator", True, [])
    sample1 = Sample(prompt="test prompt", scores=[score])
    result1 = EvaluationResult(sample=sample1, item_id=0)
    sample2 = Sample(prompt="test prompt", scores=[score])
    result2 = EvaluationResult(sample=sample2, item_id=1)

    # Add results for a new test
    session.add_results("test_func", [result1])
    assert "test_func" in session.results
    assert len(session.results["test_func"]) == 1
    assert session.results["test_func"][0] == result1

    # Add more results to the same test
    session.add_results("test_func", [result2])
    assert len(session.results["test_func"]) == 2

    # Add results for a different test
    session.add_results("another_test", [result1])
    assert "another_test" in session.results
    assert len(session.results["another_test"]) == 1


def test_session_completed_item_ids():
    """Test getting completed item IDs from a session."""
    session = Session(name="test_session")

    # No results yet
    assert session.get_completed_item_ids("test_func") == set()

    # Add some successful results
    score = Score("test_evaluator", True, [])
    sample1 = Sample(prompt="test prompt", scores=[score])
    result1 = EvaluationResult(sample=sample1, item_id=0)
    sample2 = Sample(prompt="test prompt", scores=[score])
    result2 = EvaluationResult(sample=sample2, item_id=1)
    sample3 = Sample(prompt="test prompt", scores=[score])
    result3 = EvaluationResult(sample=sample3, item_id=2, error="Some error")

    session.add_results("test_func", [result1, result2, result3])

    # Should only return IDs without errors
    completed_ids = session.get_completed_item_ids("test_func")
    assert completed_ids == {0, 1}
    assert 2 not in completed_ids  # Has error


def test_session_get_results():
    """Test getting results from a session."""
    session = Session(name="test_session")

    # No results yet
    assert session.get_results("test_func") == []

    # Add results
    score = Score("test_evaluator", True, [])
    sample = Sample(prompt="test prompt", scores=[score])
    result = EvaluationResult(sample=sample, item_id=0)
    session.add_results("test_func", [result])

    # Get results
    retrieved_results = session.get_results("test_func")
    assert len(retrieved_results) == 1
    assert retrieved_results[0] == result


@pytest.fixture
def temp_storage_dir(tmp_path):
    """Create a temporary directory for storage tests."""
    return tmp_path


def test_session_manager_init_default_storage():
    """Test SessionManager initialization with default storage."""
    manager = SessionManager(None)
    assert isinstance(manager.storage, JSONStorage)
    assert manager.current is None


def test_session_manager_init_custom_storage(temp_storage_dir):
    """Test SessionManager initialization with custom storage path."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path)
    assert isinstance(manager.storage, JSONStorage)
    assert manager.storage.dir == temp_storage_dir


@patch("doteval.sessions.SessionManager.get_git_commit")
def test_session_manager_start_new_session(mock_git_commit, temp_storage_dir):
    """Test starting a new session."""
    mock_git_commit.return_value = "abc123"
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path)

    session = manager.start("test_session")

    assert session.name == "test_session"
    assert session.metadata["git_commit"] == "abc123"
    assert manager.current == session
    assert session.status == SessionStatus.running


def test_session_manager_resume_session(temp_storage_dir):
    """Test resuming an existing session."""
    storage_path = f"json://{temp_storage_dir}"

    # First, create a manager and start a session
    manager1 = SessionManager(storage_path)
    manager1.start("test_session")

    # Add some results
    score = Score("test_evaluator", True, [])
    sample = Sample(prompt="test prompt", scores=[score])
    result = EvaluationResult(sample=sample, item_id=0)
    manager1.add_results("test_func", [result])

    # Verify the session was saved
    assert len(manager1.current.results["test_func"]) == 1

    # Don't finish the session - leave it in running state
    # This simulates a crash or interrupted session

    # Create a new manager with the same storage path
    manager2 = SessionManager(storage_path)
    session2 = manager2.start("test_session")

    # Should resume the existing session with its data
    assert len(session2.results["test_func"]) == 1
    assert manager2.current == session2


def test_session_manager_add_results(temp_storage_dir):
    """Test adding results through SessionManager."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path)
    manager.start("test_session")

    score = Score("test_evaluator", True, [])
    sample = Sample(prompt="test prompt", scores=[score])
    result = EvaluationResult(sample=sample, item_id=0)

    manager.add_results("test_func", [result])

    assert "test_func" in manager.current.results
    assert len(manager.current.results["test_func"]) == 1


def test_session_manager_get_completed_item_ids(temp_storage_dir):
    """Test getting completed item IDs through SessionManager."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path)

    # No current session
    assert manager.get_completed_item_ids("test_func") == set()

    # With current session
    manager.start("test_session")
    score = Score("test_evaluator", True, [])
    sample = Sample(prompt="test prompt", scores=[score])
    result = EvaluationResult(sample=sample, item_id=0)
    manager.add_results("test_func", [result])

    assert manager.get_completed_item_ids("test_func") == {0}


def test_session_manager_get_results(temp_storage_dir):
    """Test getting results through SessionManager."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path)

    # No current session
    assert manager.get_results("test_func") == []

    # With current session
    manager.start("test_session")
    score = Score("test_evaluator", True, [])
    sample = Sample(prompt="test prompt", scores=[score])
    result = EvaluationResult(sample=sample, item_id=0)
    manager.add_results("test_func", [result])

    results = manager.get_results("test_func")
    assert len(results) == 1


def test_session_manager_finish_session(temp_storage_dir):
    """Test finishing a session."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path)
    manager.start("test_session")

    # Finish successfully
    manager.finish(success=True)
    assert manager.current is None

    # Load the session to check status
    loaded_session = manager.get_session("test_session")
    assert loaded_session.status == SessionStatus.completed

    # Start another session and finish with failure
    manager.start("test_session2")
    manager.finish(success=False)
    loaded_session2 = manager.get_session("test_session2")
    assert loaded_session2.status == SessionStatus.failed


def test_session_manager_get_session(temp_storage_dir):
    """Test retrieving a specific session."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path)

    # Non-existent session
    assert manager.get_session("nonexistent") is None

    # Create and retrieve session
    manager.start("test_session")
    manager.finish()

    retrieved = manager.get_session("test_session")
    assert retrieved is not None
    assert retrieved.name == "test_session"


def test_session_manager_list_sessions(temp_storage_dir):
    """Test listing all sessions."""
    storage_path = f"json://{temp_storage_dir}"
    manager = SessionManager(storage_path)

    # Initially empty
    assert manager.list_sessions() == []

    # Create multiple sessions
    manager.start("session1")
    manager.finish()
    manager.start("session2")
    manager.finish()

    sessions = manager.list_sessions()
    assert len(sessions) == 2
    assert "session1" in sessions
    assert "session2" in sessions


@patch("subprocess.check_output")
def test_session_manager_get_git_commit_success(mock_check_output, temp_storage_dir):
    """Test getting git commit when git is available."""
    mock_check_output.return_value = b"abc123def456\n"

    manager = SessionManager(None)
    commit = manager.get_git_commit()

    assert commit == "abc123de"  # First 8 characters


@patch("subprocess.check_output")
def test_session_manager_get_git_commit_failure(mock_check_output, temp_storage_dir):
    """Test getting git commit when git fails."""
    import subprocess

    mock_check_output.side_effect = subprocess.CalledProcessError(1, "git")

    manager = SessionManager(None)
    commit = manager.get_git_commit()

    assert commit is None
