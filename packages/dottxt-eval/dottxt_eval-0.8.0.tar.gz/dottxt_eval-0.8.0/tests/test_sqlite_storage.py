import os
import sqlite3

import pytest
from PIL import Image

from doteval.metrics import accuracy
from doteval.models import EvaluationResult, Sample, Score
from doteval.sessions import Session, SessionStatus
from doteval.storage.sqlite import SQLiteStorage


@pytest.fixture
def storage_path(tmp_path):
    """Create a temporary SQLite database path."""
    return str(tmp_path / "test.db")


@pytest.fixture
def storage(storage_path):
    """Create a SQLiteStorage instance."""
    return SQLiteStorage(storage_path)


def test_sqlite_storage_initialization(storage_path):
    """Test SQLiteStorage initialization creates database and tables."""
    _ = SQLiteStorage(storage_path)
    assert os.path.exists(storage_path)

    # Verify tables exist
    with sqlite3.connect(storage_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        expected_tables = {"sessions", "tests", "results", "scores", "locks"}
        assert expected_tables.issubset(tables)


def test_sqlite_storage_save_and_load_session(storage):
    """Test saving and loading a session."""
    session = Session(name="test_session")
    session.metadata = {"key": "value", "number": 42}
    session.status = SessionStatus.completed

    score1 = Score("evaluator1", True, [accuracy], {"arg1": "value1"})
    score2 = Score("evaluator2", 0.95, [], {"arg2": "value2"})
    sample1 = Sample(prompt="test prompt 1", scores=[score1, score2])
    sample2 = Sample(prompt="test prompt 2", scores=[score1])
    result1 = EvaluationResult(
        sample=sample1,
        item_id=0,
        dataset_row={"input": "test", "expected": "output"},
        error=None,
        timestamp=1234567890.0,
    )
    result2 = EvaluationResult(
        sample=sample2,
        item_id=1,
        dataset_row={"input": "test2"},
        error="Test error",
        timestamp=1234567891.0,
    )

    session.add_results("test_func", [result1, result2])
    storage.save(session)

    # Load the session
    loaded = storage.load("test_session")

    assert loaded is not None
    assert loaded.name == session.name
    assert loaded.metadata == session.metadata
    assert loaded.created_at == session.created_at
    assert loaded.status == session.status

    assert "test_func" in loaded.results
    loaded_results = loaded.results["test_func"]
    assert len(loaded_results) == 2

    # Check first result
    assert loaded_results[0].item_id == 0
    assert len(loaded_results[0].sample.scores) == 2
    assert loaded_results[0].sample.scores[0].name == "evaluator1"
    assert loaded_results[0].sample.scores[0].value is True
    assert len(loaded_results[0].sample.scores[0].metrics) == 1
    assert loaded_results[0].sample.scores[0].metrics[0].__name__ == "accuracy"
    assert loaded_results[0].sample.scores[0].metadata == {"arg1": "value1"}
    assert loaded_results[0].sample.scores[1].name == "evaluator2"
    assert loaded_results[0].sample.scores[1].value == 0.95
    assert loaded_results[0].sample.scores[1].metadata == {"arg2": "value2"}
    assert loaded_results[0].dataset_row == {"input": "test", "expected": "output"}
    assert loaded_results[0].error is None
    assert loaded_results[0].timestamp == 1234567890.0

    # Check second result
    assert loaded_results[1].item_id == 1
    assert loaded_results[1].error == "Test error"


def test_sqlite_storage_load_nonexistent_session(storage):
    """Test loading a non-existent session returns None."""
    loaded = storage.load("nonexistent")
    assert loaded is None


def test_sqlite_storage_list_names(storage):
    """Test listing session names."""
    assert storage.list_names() == []

    session1 = Session("session1")
    session2 = Session("session2")
    session3 = Session("session3")

    storage.save(session1)
    storage.save(session2)
    storage.save(session3)

    names = storage.list_names()
    assert len(names) == 3
    assert set(names) == {"session1", "session2", "session3"}


def test_sqlite_storage_overwrite_session(storage):
    """Test that saving a session with the same name overwrites it."""
    # Save initial session
    session1 = Session("test_session")
    session1.metadata = {"version": 1}
    storage.save(session1)

    # Save session with same name but different data
    session2 = Session("test_session")
    session2.metadata = {"version": 2}
    storage.save(session2)

    # Load and verify it's the second version
    loaded = storage.load("test_session")
    assert loaded.metadata == {"version": 2}


def test_sqlite_storage_rename_session(storage):
    """Test renaming a session."""
    session = Session("old_name")
    session.metadata = {"test": "data"}
    storage.save(session)

    storage.rename("old_name", "new_name")

    # Old name should not exist
    assert storage.load("old_name") is None

    # New name should exist with same data
    loaded = storage.load("new_name")
    assert loaded is not None
    assert loaded.name == "new_name"
    assert loaded.metadata == {"test": "data"}

    # List should show new name
    assert "new_name" in storage.list_names()
    assert "old_name" not in storage.list_names()


def test_sqlite_storage_delete_session(storage):
    """Test deleting a session."""
    session = Session("to_delete")
    storage.save(session)

    assert "to_delete" in storage.list_names()

    storage.delete("to_delete")

    assert "to_delete" not in storage.list_names()
    assert storage.load("to_delete") is None


def test_sqlite_storage_delete_nonexistent_session(storage):
    """Test deleting a non-existent session raises error."""
    with pytest.raises(ValueError, match="session not found"):
        storage.delete("nonexistent")


def test_lock_is_created_and_removed(storage):
    """Test lock creation and removal for interrupted session tracking."""
    session_name = "testsession"

    # Should not be locked initially
    assert not storage.is_locked(session_name)

    # Acquire lock
    storage.acquire_lock(session_name)
    assert storage.is_locked(session_name)

    # Release lock
    storage.release_lock(session_name)
    assert not storage.is_locked(session_name)


def test_acquire_lock_raises_if_locked(storage):
    """Test acquiring lock on already locked session raises error."""
    session_name = "locked_session"
    storage.acquire_lock(session_name)

    with pytest.raises(RuntimeError, match="already locked"):
        storage.acquire_lock(session_name)

    # Clean up
    storage.release_lock(session_name)


def test_release_lock_noop_if_not_locked(storage):
    """Test releasing non-existent lock doesn't raise error."""
    session_name = "not_locked"
    # Should not raise even if lock doesn't exist
    storage.release_lock(session_name)
    assert not storage.is_locked(session_name)


def test_is_locked_reports_correctly(storage):
    """Test lock status is reported correctly."""
    session_name = "lockcheck"
    assert not storage.is_locked(session_name)
    storage.acquire_lock(session_name)
    assert storage.is_locked(session_name)
    storage.release_lock(session_name)
    assert not storage.is_locked(session_name)


def test_multiple_tests_per_session(storage):
    """Test saving and loading a session with multiple test functions."""
    session = Session("multi_test")

    # Add results for first test
    score1 = Score("exact_match", True, [])
    sample1 = Sample(prompt="test prompt", scores=[score1])
    result1 = EvaluationResult(sample=sample1, item_id=0)
    session.add_results("test_func1", [result1])

    # Add results for second test
    score2 = Score("similarity", 0.85, [])
    sample2 = Sample(prompt="test prompt 2", scores=[score2])
    result2 = EvaluationResult(sample=sample2, item_id=0)
    session.add_results("test_func2", [result2])

    storage.save(session)

    loaded = storage.load("multi_test")
    assert len(loaded.results) == 2
    assert "test_func1" in loaded.results
    assert "test_func2" in loaded.results
    assert loaded.results["test_func1"][0].sample.scores[0].name == "exact_match"
    assert loaded.results["test_func2"][0].sample.scores[0].name == "similarity"


def test_incremental_save(storage):
    """Test that incremental saves work correctly."""
    session = Session("incremental")

    # Save with initial results
    score1 = Score("evaluator", True, [])
    sample1 = Sample(prompt="test prompt", scores=[score1])
    result1 = EvaluationResult(sample=sample1, item_id=0)
    session.add_results("test", [result1])
    storage.save(session)

    # Add more results and save again
    sample2 = Sample(prompt="test prompt 2", scores=[score1])
    result2 = EvaluationResult(sample=sample2, item_id=1)
    session.add_results("test", [result2])
    storage.save(session)

    # Load and verify all results are there
    loaded = storage.load("incremental")
    assert len(loaded.results["test"]) == 2
    assert loaded.results["test"][0].item_id == 0
    assert loaded.results["test"][1].item_id == 1


# Test query helper methods


def test_get_failed_results(storage):
    """Test getting failed results."""
    session = Session("test_failures")

    # Add mix of passing and failing results
    pass_score = Score("exact_match", True, [])
    fail_score = Score("exact_match", False, [])
    numeric_fail = Score("accuracy", 0.0, [])

    sample_pass = Sample(prompt="1+1", scores=[pass_score])
    sample_fail = Sample(prompt="2+2", scores=[fail_score])
    sample_numeric_fail = Sample(prompt="3+3", scores=[numeric_fail])
    results = [
        EvaluationResult(
            sample=sample_pass, item_id=0, dataset_row={"q": "1+1", "a": "2"}
        ),
        EvaluationResult(
            sample=sample_fail, item_id=1, dataset_row={"q": "2+2", "a": "5"}
        ),
        EvaluationResult(
            sample=sample_numeric_fail, item_id=2, dataset_row={"q": "3+3", "a": "7"}
        ),
    ]

    session.add_results("math_test", results)
    storage.save(session)

    # Get all failed results
    failed = storage.get_failed_results("test_failures")
    assert len(failed) == 2
    assert failed[0]["item_id"] == 1
    assert failed[0]["value"] is False
    assert failed[1]["item_id"] == 2
    assert failed[1]["value"] == 0.0

    # Filter by evaluator
    failed_exact = storage.get_failed_results(
        "test_failures", evaluator_name="exact_match"
    )
    assert len(failed_exact) == 1
    assert failed_exact[0]["evaluator_name"] == "exact_match"


def test_get_error_results(storage):
    """Test getting results with errors."""
    session = Session("test_errors")

    score = Score("evaluator", None, [])
    sample1 = Sample(prompt="test prompt 1", scores=[score])
    sample2 = Sample(prompt="test prompt 2", scores=[score])
    sample3 = Sample(prompt="test prompt 3", scores=[score])
    results = [
        EvaluationResult(sample=sample1, item_id=0, error=None),
        EvaluationResult(sample=sample2, item_id=1, error="Timeout error"),
        EvaluationResult(sample=sample3, item_id=2, error="API error"),
    ]

    session.add_results("error_test", results)
    storage.save(session)

    errors = storage.get_error_results("test_errors")
    assert len(errors) == 2
    assert errors[0]["item_id"] == 1
    assert errors[0]["error"] == "Timeout error"
    assert errors[1]["item_id"] == 2
    assert errors[1]["error"] == "API error"


def test_pil_image_serialization_sqlite(storage):
    """Test that PIL Images are properly serialized and deserialized in SQLite."""
    # Create a test PIL Image
    test_image = Image.new("RGB", (100, 100), color="red")

    # Create a session with PIL Image in item_data
    session = Session(name="test_pil")
    sample = Sample(prompt="test image prompt", scores=[Score("test", 1.0, [], {})])
    result = EvaluationResult(
        sample=sample,
        item_id="test_item",
        dataset_row=(test_image, "expected_info"),
        error=None,
        timestamp=0.0,
    )
    session.results["test"] = [result]

    # Save and load the session
    storage.save(session)

    # Load the session back
    loaded_session = storage.load("test_pil")
    assert loaded_session is not None

    # Verify the PIL Image was properly deserialized
    loaded_result = loaded_session.results["test"][0]
    loaded_image, loaded_info = loaded_result.dataset_row

    assert isinstance(loaded_image, Image.Image)
    assert loaded_image.mode == "RGB"
    assert loaded_image.size == (100, 100)
    assert loaded_info == "expected_info"


def test_nested_pil_images_sqlite(storage):
    """Test serialization of nested structures containing PIL Images in SQLite."""
    # Create test images
    img1 = Image.new("RGB", (50, 50), color="blue")
    img2 = Image.new("RGBA", (75, 75), color="green")

    # Create complex nested structure
    session = Session(name="test_nested")
    sample = Sample(prompt="nested test prompt", scores=[Score("test", 1.0, [], {})])
    result = EvaluationResult(
        sample=sample,
        item_id="nested_test",
        dataset_row={
            "images": [img1, img2],
            "metadata": {
                "primary_image": img1,
                "tuple_with_image": (img2, "description"),
            },
        },
        error=None,
        timestamp=0.0,
    )
    session.results["test"] = [result]

    # Save and load
    storage.save(session)

    loaded_session = storage.load("test_nested")
    assert loaded_session is not None

    loaded_data = loaded_session.results["test"][0].dataset_row

    # Verify images list
    assert len(loaded_data["images"]) == 2
    assert isinstance(loaded_data["images"][0], Image.Image)
    assert loaded_data["images"][0].size == (50, 50)
    assert loaded_data["images"][0].mode == "RGB"

    assert isinstance(loaded_data["images"][1], Image.Image)
    assert loaded_data["images"][1].size == (75, 75)
    assert loaded_data["images"][1].mode == "RGBA"

    # Verify nested metadata
    assert isinstance(loaded_data["metadata"]["primary_image"], Image.Image)
    assert loaded_data["metadata"]["primary_image"].size == (50, 50)

    # Verify tuple
    assert isinstance(loaded_data["metadata"]["tuple_with_image"], tuple)
    assert len(loaded_data["metadata"]["tuple_with_image"]) == 2
    assert isinstance(loaded_data["metadata"]["tuple_with_image"][0], Image.Image)
    assert loaded_data["metadata"]["tuple_with_image"][1] == "description"


def test_get_failed_results_with_images(storage):
    """Test query methods work correctly with PIL images."""
    session = Session("test_image_failures")

    # Create test image
    test_img = Image.new("RGB", (20, 20), color="yellow")

    fail_score = Score("image_match", False, [])
    sample = Sample(prompt="image test prompt", scores=[fail_score])
    result = EvaluationResult(
        sample=sample, item_id=0, dataset_row={"image": test_img, "expected": "cat"}
    )

    session.add_results("image_test", [result])
    storage.save(session)

    # Get failed results
    failed = storage.get_failed_results("test_image_failures")
    assert len(failed) == 1
    assert isinstance(failed[0]["dataset_row"]["image"], Image.Image)
    assert failed[0]["dataset_row"]["image"].size == (20, 20)
