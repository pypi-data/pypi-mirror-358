"""Tests for CLI commands and user interface."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from doteval.cli import cli


@pytest.fixture
def cli_runner():
    """Provide a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_storage():
    """Provide temporary storage for CLI tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_cli_list_empty_storage(cli_runner):
    """Test 'doteval list' with empty storage."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        mock_manager = mock_session_manager.return_value
        mock_manager.list_sessions.return_value = []

        result = cli_runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "No sessions found" in result.output


def test_cli_list_with_sessions(cli_runner):
    """Test 'doteval list' with existing sessions."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        # Create mock sessions
        mock_session1 = MagicMock()
        mock_session1.status.value = "Completed"
        mock_session1.created_at = 1640995200.0  # 2022-01-01

        mock_session2 = MagicMock()
        mock_session2.status.value = "Running"
        mock_session2.created_at = 1640995200.0

        mock_manager = mock_session_manager.return_value
        mock_manager.list_sessions.return_value = ["test_session_1", "test_session_2"]
        mock_manager.get_session.side_effect = [
            mock_session1,
            mock_session1,
            mock_session2,
            mock_session2,
        ]
        mock_manager.storage.is_locked.return_value = False

        result = cli_runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "test_session_1" in result.output
        assert "test_session_2" in result.output


def test_cli_show_existing_session(cli_runner):
    """Test 'doteval show' with existing session."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        # Mock session with some results
        mock_session = MagicMock()
        mock_session.results = {
            "eval_test": [MagicMock(scores=[MagicMock()], item_id=0, dataset_row={})]
        }

        mock_manager = mock_session_manager.return_value
        mock_manager.get_session.return_value = mock_session

        result = cli_runner.invoke(cli, ["show", "test_session"])

        assert result.exit_code == 0
        assert "test_session" in result.output


def test_cli_show_nonexistent_session(cli_runner):
    """Test 'doteval show' with nonexistent session."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        mock_manager = mock_session_manager.return_value
        mock_manager.get_session.return_value = None

        result = cli_runner.invoke(cli, ["show", "nonexistent"])

        assert result.exit_code == 0  # CLI doesn't exit with error code
        assert "not found" in result.output


def test_cli_rename_session_success(cli_runner):
    """Test 'doteval rename' command success."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        mock_session = MagicMock()
        mock_session.name = "old_name"

        mock_manager = mock_session_manager.return_value
        mock_manager.get_session.return_value = mock_session
        mock_manager.storage = MagicMock()

        result = cli_runner.invoke(cli, ["rename", "old_name", "new_name"])

        assert result.exit_code == 0
        assert "renamed" in result.output
        # Verify the session name was changed
        assert mock_session.name == "new_name"
        mock_manager.storage.save.assert_called_once_with(mock_session)
        mock_manager.storage.rename.assert_called_once_with("old_name", "new_name")


def test_cli_rename_nonexistent_session(cli_runner):
    """Test 'doteval rename' with nonexistent session."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        mock_manager = mock_session_manager.return_value
        mock_manager.get_session.return_value = None

        result = cli_runner.invoke(cli, ["rename", "nonexistent", "new_name"])

        assert result.exit_code == 0
        assert "not found" in result.output


def test_cli_delete_session_success(cli_runner):
    """Test 'doteval delete' command success."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        mock_manager = mock_session_manager.return_value
        # Mock successful deletion
        mock_manager.delete_session.return_value = None

        result = cli_runner.invoke(cli, ["delete", "session_to_delete"])

        assert result.exit_code == 0
        assert "Deleted session" in result.output
        mock_manager.delete_session.assert_called_once_with("session_to_delete")


def test_cli_delete_nonexistent_session(cli_runner):
    """Test 'doteval delete' with nonexistent session."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        mock_manager = mock_session_manager.return_value
        # Mock deletion failure
        mock_manager.delete_session.side_effect = ValueError("Session not found")

        result = cli_runner.invoke(cli, ["delete", "nonexistent"])

        assert result.exit_code == 0
        assert "not found" in result.output


def test_cli_list_with_name_filter(cli_runner):
    """Test 'doteval list --name' filtering."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        mock_session = MagicMock()
        mock_session.status.value = "Completed"
        mock_session.created_at = 1640995200.0

        mock_manager = mock_session_manager.return_value
        mock_manager.list_sessions.return_value = [
            "math_eval",
            "text_eval",
            "other_test",
        ]
        mock_manager.get_session.return_value = mock_session
        mock_manager.storage.is_locked.return_value = False

        result = cli_runner.invoke(cli, ["list", "--name", "eval"])

        assert result.exit_code == 0
        # Should only show sessions containing "eval"
        assert "math_eval" in result.output
        assert "text_eval" in result.output
        assert "other_test" not in result.output


def test_cli_list_with_status_filter(cli_runner):
    """Test 'doteval list --status' filtering."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        mock_session_completed = MagicMock()
        mock_session_completed.status.value = "Completed"
        mock_session_completed.created_at = 1640995200.0

        mock_session_running = MagicMock()
        mock_session_running.status.value = "Running"
        mock_session_running.created_at = 1640995200.0

        mock_manager = mock_session_manager.return_value
        mock_manager.list_sessions.return_value = ["session1", "session2"]
        mock_manager.get_session.side_effect = [
            mock_session_completed,
            mock_session_completed,
            mock_session_running,
            mock_session_running,
        ]
        mock_manager.storage.is_locked.return_value = False

        result = cli_runner.invoke(cli, ["list", "--status", "Completed"])

        assert result.exit_code == 0
        # Should only show completed sessions


def test_cli_show_with_full_flag(cli_runner):
    """Test 'doteval show --full' with detailed output."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        with patch("doteval.cli.serialize") as mock_serialize:
            mock_session = MagicMock()
            mock_serialize.return_value = {"session": "data"}

            mock_manager = mock_session_manager.return_value
            mock_manager.get_session.return_value = mock_session

            result = cli_runner.invoke(cli, ["show", "test_session", "--full"])

            assert result.exit_code == 0
            mock_serialize.assert_called_once_with(mock_session)


def test_cli_with_custom_storage_option(cli_runner):
    """Test CLI commands with custom storage option."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        mock_manager = mock_session_manager.return_value
        mock_manager.list_sessions.return_value = []

        result = cli_runner.invoke(cli, ["list", "--storage", "json://custom/path"])

        # Should pass custom storage path to SessionManager
        mock_session_manager.assert_called_with("json://custom/path")
        assert result.exit_code == 0


def test_cli_interrupted_session_status(cli_runner):
    """Test that interrupted sessions are properly marked."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        from doteval.sessions import SessionStatus

        mock_session = MagicMock()
        mock_session.status = SessionStatus.running  # Use actual enum value
        mock_session.created_at = 1640995200.0

        mock_manager = mock_session_manager.return_value
        mock_manager.list_sessions.return_value = ["interrupted_session"]
        mock_manager.get_session.return_value = mock_session
        # Mock that this session is NOT locked (interrupted - process died)
        mock_manager.storage.is_locked.return_value = False

        result = cli_runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "Interrupted" in result.output


def test_cli_show_with_errors(cli_runner):
    """Test 'doteval show' displays error counts."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        from doteval.metrics import accuracy
        from doteval.models import EvaluationResult, Sample, Score

        # Create mock results with some errors
        results = [
            EvaluationResult(
                sample=Sample("test1", Score("llm_judge", 0.9, [accuracy()])),
                item_id=1,
                dataset_row={"prompt": "test1"},
                error=None,
                timestamp=1640995200.0,
            ),
            EvaluationResult(
                sample=Sample("", Score("llm_judge", 0, [accuracy()])),
                item_id=2,
                dataset_row={"prompt": "test2"},
                error="ConnectionError: Unable to connect to API",
                timestamp=1640995201.0,
            ),
            EvaluationResult(
                sample=Sample("test3", Score("llm_judge", 0.8, [accuracy()])),
                item_id=3,
                dataset_row={"prompt": "test3"},
                error=None,
                timestamp=1640995202.0,
            ),
            EvaluationResult(
                sample=Sample("", Score("llm_judge", 0, [accuracy()])),
                item_id=4,
                dataset_row={"prompt": "test4"},
                error="ValueError: Invalid response format",
                timestamp=1640995203.0,
            ),
        ]

        mock_session = MagicMock()
        mock_session.results = {"eval_test": results}

        mock_manager = mock_session_manager.return_value
        mock_manager.get_session.return_value = mock_session

        result = cli_runner.invoke(cli, ["show", "test_session"])

        assert result.exit_code == 0
        # Check that error count is displayed
        assert "2/4 (50.0%)" in result.output
        # Check error summary section
        assert "Error Summary:" in result.output
        assert "Total errors: 2 out of 4 items" in result.output
        assert "ConnectionError: 1 occurrence" in result.output
        assert "ValueError: 1 occurrence" in result.output


def test_cli_show_with_errors_flag(cli_runner):
    """Test 'doteval show --errors' displays detailed error information."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        from doteval.metrics import accuracy
        from doteval.models import EvaluationResult, Sample, Score

        # Create mock results with errors
        results = [
            EvaluationResult(
                sample=Sample("", Score("llm_judge", 0, [accuracy()])),
                item_id=42,
                dataset_row={
                    "prompt": "What is the capital of France?",
                    "expected": "Paris",
                },
                error="ConnectionError: Unable to connect to API endpoint",
                timestamp=1640995200.0,
            ),
            EvaluationResult(
                sample=Sample("", Score("llm_judge", 0, [accuracy()])),
                item_id=87,
                dataset_row={"prompt": "Calculate 2+2", "expected": "4"},
                error="ValueError: Invalid response format",
                timestamp=1640995201.0,
            ),
        ]

        mock_session = MagicMock()
        mock_session.results = {"eval_test": results}

        mock_manager = mock_session_manager.return_value
        mock_manager.get_session.return_value = mock_session

        result = cli_runner.invoke(cli, ["show", "test_session", "--errors"])

        assert result.exit_code == 0
        # Check detailed error display
        assert "Error Details (2 errors):" in result.output
        assert "[1] Item ID: 42" in result.output
        assert "ConnectionError: Unable to connect to API endpoint" in result.output
        assert "What is the capital of France?" in result.output
        assert "[2] Item ID: 87" in result.output
        assert "ValueError: Invalid response format" in result.output
        assert "Calculate 2+2" in result.output
        # Check timestamps are formatted correctly
        assert "2022-01-01" in result.output


def test_cli_show_no_errors(cli_runner):
    """Test 'doteval show' when there are no errors."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        from doteval.metrics import accuracy
        from doteval.models import EvaluationResult, Sample, Score

        # Create mock results without errors
        results = [
            EvaluationResult(
                sample=Sample("test1", Score("llm_judge", 0.9, [accuracy()])),
                item_id=1,
                dataset_row={"prompt": "test1"},
                error=None,
            ),
            EvaluationResult(
                sample=Sample("test2", Score("llm_judge", 0.85, [accuracy()])),
                item_id=2,
                dataset_row={"prompt": "test2"},
                error=None,
            ),
        ]

        mock_session = MagicMock()
        mock_session.results = {"eval_test": results}

        mock_manager = mock_session_manager.return_value
        mock_manager.get_session.return_value = mock_session

        result = cli_runner.invoke(cli, ["show", "test_session"])

        assert result.exit_code == 0
        # Check that error count shows 0
        assert "0/2 (0.0%)" in result.output
        # Error summary should not appear
        assert "Error Summary:" not in result.output


def test_cli_show_truncates_long_dataset(cli_runner):
    """Test that long dataset rows are truncated in error display."""
    with patch("doteval.cli.SessionManager") as mock_session_manager:
        from doteval.metrics import accuracy
        from doteval.models import EvaluationResult, Sample, Score

        # Create a very long dataset row
        long_text = "x" * 200
        results = [
            EvaluationResult(
                sample=Sample("", Score("llm_judge", 0, [accuracy()])),
                item_id=1,
                dataset_row={"prompt": long_text},
                error="Error occurred",
                timestamp=1640995200.0,
            ),
        ]

        mock_session = MagicMock()
        mock_session.results = {"eval_test": results}

        mock_manager = mock_session_manager.return_value
        mock_manager.get_session.return_value = mock_session

        result = cli_runner.invoke(cli, ["show", "test_session", "--errors"])

        assert result.exit_code == 0
        # Check that dataset is truncated
        assert "..." in result.output
        # Should not contain the full 200-character string
        assert long_text not in result.output
