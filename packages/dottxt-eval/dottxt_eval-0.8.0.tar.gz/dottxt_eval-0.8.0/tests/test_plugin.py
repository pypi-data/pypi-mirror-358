"""Tests for the doteval pytest plugin functionality.

These are tests that specifically test the pytest plugin integration.
Tests for the core foreach functionality are in test_core.py.
"""

import os
import subprocess
import sys
import tempfile


def test_pytest_plugin_basic_execution():
    """Test that the pytest plugin can execute doteval tests."""
    # Create a temporary test file
    test_content = """
import doteval
from doteval import Sample
from doteval.evaluators import exact_match

dataset = [("Hello", "Hello"), ("World", "World")]

@doteval.foreach("input,expected", dataset)
def eval_basic(input, expected):
    prompt = f"Input: {input}"
    return Sample(prompt=prompt, scores=[exact_match(input, expected)])
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            # Run pytest on the temp file
            result = subprocess.run(
                [sys.executable, "-m", "pytest", f.name, "-v"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Check that the test passed
            if result.returncode != 0:
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            assert result.returncode == 0
            assert "eval_basic" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_parametrize():
    """Test that the pytest plugin can execute doteval tests."""
    # Create a temporary test file
    test_content = """
import doteval
import pytest
from doteval import Sample
from doteval.evaluators import exact_match

dataset = [("Hello", "Hello"), ("World", "World")]

@pytest.mark.parametrize(
    "add", ["a", "b", "c"]
)
@doteval.foreach("input,expected", dataset)
def eval_basic(input, expected, add):
    prompt = f"Input: {input}, Add: {add}"
    return Sample(prompt=prompt, scores=[exact_match(input, expected)])
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            # Run pytest on the temp file
            result = subprocess.run(
                [sys.executable, "-m", "pytest", f.name, "-v"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )
            # Check that the test passed
            assert result.returncode == 0
            assert "eval_basic" in result.stdout
            assert "3 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_fixture():
    """Test that the pytest plugin can execute doteval tests with fixtures."""
    # Create a temporary test file
    test_content = """
import doteval
import pytest
from doteval import Sample
from doteval.evaluators import exact_match

@pytest.fixture
def add():
    return "a"

dataset = [("Hello", "Hello"), ("World", "World")]

@doteval.foreach("input,expected", dataset)
def eval_basic(input, expected, add):
    add()
    prompt = f"Input: {input}"
    return Sample(prompt=prompt, scores=[exact_match(input, expected)])
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            # Run pytest on the temp file
            result = subprocess.run(
                [sys.executable, "-m", "pytest", f.name, "-v"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )
            # Check that the test passed
            if result.returncode != 0:
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            assert result.returncode == 0
            assert "eval_basic" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_samples_option():
    """Test that the --samples option works with pytest."""
    # Create a temporary test file with larger dataset
    test_content = """
import doteval
from doteval.evaluators import exact_match

dataset = [
    ("Q1", "A1"),
    ("Q2", "A2"),
    ("Q3", "A3"),
    ("Q4", "A4"),
    ("Q5", "A5")
]

@doteval.foreach("question,answer", dataset)
def eval_with_samples(question, answer):
    return exact_match(question, answer)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            # Run pytest with --samples option
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    f.name,
                    "--samples",
                    "2",
                    "-v",  # Verbose to show function names
                ],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Check that the test passed
            assert result.returncode == 0
            assert "eval_with_samples" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_custom_column_names():
    """Test that custom column names work in pytest."""
    test_content = """
import doteval
from doteval.evaluators import exact_match

dataset = [("user_input", "model_output", "extra_context")]

@doteval.foreach("user_prompt,model_response,context", dataset)
def eval_custom_columns(user_prompt, model_response, context):
    combined = f"{user_prompt}-{model_response}-{context}"
    expected = "user_input-model_output-extra_context"
    prompt = f"Combining: {user_prompt}, {model_response}, {context}"
    return doteval.Sample(prompt=prompt, scores=[exact_match(combined, expected)])
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(test_content)
        f.flush()

        try:
            # Run pytest
            result = subprocess.run(
                [sys.executable, "-m", "pytest", f.name, "-v"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Check that the test passed
            assert result.returncode == 0
            assert "eval_custom_columns" in result.stdout
            assert "1 passed" in result.stdout

        finally:
            os.unlink(f.name)


def test_pytest_plugin_max_concurrency_option():
    """Test that the --max-concurrency option limits concurrent async evaluations."""
    import time

    # Create a test file with async evaluations that track concurrency
    test_content = """
import asyncio
import time
from pathlib import Path
import doteval
from doteval import Sample
from doteval.evaluators import exact_match

# Track concurrent executions
concurrency_file = Path("concurrency_tracking.txt")
concurrency_file.write_text("0")

dataset = [(f"item{i}", f"item{i}") for i in range(10)]

@doteval.foreach("input,expected", dataset)
async def eval_concurrency_test(input, expected):
    # Increment concurrent counter
    with open("concurrency_tracking.txt", "r") as f:
        current = int(f.read().strip())

    with open("concurrency_tracking.txt", "w") as f:
        f.write(str(current + 1))

    # Record max concurrency seen
    max_file = Path("max_concurrency.txt")
    if max_file.exists():
        with open(max_file, "r") as f:
            max_seen = int(f.read().strip())
        max_seen = max(max_seen, current + 1)
    else:
        max_seen = current + 1

    with open(max_file, "w") as f:
        f.write(str(max_seen))

    # Simulate work
    await asyncio.sleep(0.1)

    # Decrement concurrent counter
    with open("concurrency_tracking.txt", "r") as f:
        current = int(f.read().strip())

    with open("concurrency_tracking.txt", "w") as f:
        f.write(str(current - 1))

    return Sample(prompt=f"Test: {input}", scores=[exact_match(input, expected)])
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_concurrency.py")
        with open(test_file, "w") as f:
            f.write(test_content)

        # Run with max-concurrency=3
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "--max-concurrency", "3", "-v"],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )
        duration = time.time() - start_time

        # Check test passed
        assert result.returncode == 0
        assert "eval_concurrency_test" in result.stdout

        # Check max concurrency was respected
        max_concurrency_file = os.path.join(tmpdir, "max_concurrency.txt")
        with open(max_concurrency_file) as f:
            observed_max = int(f.read().strip())

        # Max concurrent executions should not exceed 3
        assert (
            observed_max <= 3
        ), f"Expected max concurrency <= 3, but got {observed_max}"

        # With 10 items and 0.1s sleep each, if they all ran sequentially it would take ~1s
        # With max concurrency of 3, it should take ~0.4s (10/3 * 0.1)
        # Allow some overhead
        assert (
            duration < 0.8
        ), f"Execution took {duration}s, suggesting concurrency wasn't working"


def test_pytest_plugin_default_max_concurrency():
    """Test that the default max concurrency is used when not specified."""
    # Create a test file with sync evaluations to test the default parameter handling
    test_content = """
import doteval
from doteval import Sample
from doteval.evaluators import exact_match

dataset = [("item1", "item1"), ("item2", "item2")]

@doteval.foreach("input,expected", dataset)
def eval_default_concurrency(input, expected):
    return Sample(prompt=f"Test: {input}", scores=[exact_match(input, expected)])
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_default_concurrency.py")
        with open(test_file, "w") as f:
            f.write(test_content)

        # Run without specifying max-concurrency (should use default)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v"],
            capture_output=True,
            text=True,
            cwd=tmpdir,
        )

        # Check test passed
        assert result.returncode == 0
        assert "eval_default_concurrency" in result.stdout
        assert "1 passed" in result.stdout
