import base64
import io
import json
import sqlite3
from typing import Any, Optional

from PIL import Image

from doteval.metrics import registry
from doteval.models import EvaluationResult, Sample, Score
from doteval.sessions import Session, SessionStatus
from doteval.storage.base import Storage, _registry

__all__ = ["SQLiteStorage"]


def _serialize_value(value: Any) -> Any:
    """Recursively serialize values, converting PIL Images to base64."""
    if isinstance(value, Image.Image):
        # Convert PIL Image to base64
        buffered = io.BytesIO()
        value.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        return {
            "__type__": "PIL.Image",
            "data": img_base64,
            "mode": value.mode,
            "size": value.size,
        }
    elif isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_serialize_value(item) for item in value]
    elif isinstance(value, tuple):
        return {"__type__": "tuple", "data": [_serialize_value(item) for item in value]}
    else:
        return value


def _deserialize_value(value: Any) -> Any:
    """Recursively deserialize values, converting base64 back to PIL Images."""
    if isinstance(value, dict):
        if value.get("__type__") == "PIL.Image":
            # Convert base64 back to PIL Image
            img_data = base64.b64decode(value["data"])
            img = Image.open(io.BytesIO(img_data))
            return img
        elif value.get("__type__") == "tuple":
            return tuple(_deserialize_value(item) for item in value["data"])
        else:
            return {k: _deserialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_deserialize_value(item) for item in value]
    else:
        return value


class SQLiteStorage(Storage):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")

            # Sessions table (one row per session)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    name TEXT PRIMARY KEY,
                    metadata TEXT,
                    created_at REAL,
                    status TEXT
                )
                """
            )

            # Tests table (one row per test within a session)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tests (
                    id INTEGER PRIMARY KEY,
                    session_name TEXT,
                    test_name TEXT,
                    FOREIGN KEY(session_name) REFERENCES sessions(name) ON DELETE CASCADE,
                    UNIQUE(session_name, test_name)
                )
                """
            )

            # Results table (one row per evaluation result)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY,
                    test_id INTEGER,
                    item_id INTEGER,
                    dataset_row TEXT,
                    error TEXT,
                    timestamp REAL,
                    prompt TEXT,
                    FOREIGN KEY(test_id) REFERENCES tests(id) ON DELETE CASCADE
                )
                """
            )

            # Scores table (one row per score within a result)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY,
                    result_id INTEGER,
                    evaluator_name TEXT,
                    value TEXT,
                    metrics TEXT,
                    metadata TEXT,
                    FOREIGN KEY(result_id) REFERENCES results(id) ON DELETE CASCADE
                )
                """
            )

            # Locks table for tracking interrupted sessions
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS locks (
                    session_name TEXT PRIMARY KEY,
                    acquired_at REAL DEFAULT (unixepoch('now'))
                )
                """
            )

            # Create indexes for common queries
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_results_test_id ON results(test_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_results_item_id ON results(item_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_scores_result_id ON scores(result_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_scores_evaluator ON scores(evaluator_name)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_scores_value ON scores(value)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_results_error ON results(error)"
            )

    def save(self, session: Session):
        """Save a Session instance to the SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert or update session
            cursor.execute(
                """
                INSERT OR REPLACE INTO sessions (name, metadata, created_at, status)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session.name,
                    json.dumps(session.metadata),
                    session.created_at,
                    session.status.value,
                ),
            )

            # Process each test's results
            for test_name, results in session.results.items():
                # Ensure test exists and get its ID
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO tests (session_name, test_name)
                    VALUES (?, ?)
                    """,
                    (session.name, test_name),
                )

                # Get test_id (works whether we just inserted or it already existed)
                cursor.execute(
                    "SELECT id FROM tests WHERE session_name = ? AND test_name = ?",
                    (session.name, test_name),
                )
                test_id = cursor.fetchone()[0]

                # Delete existing results for this test (for idempotency)
                cursor.execute("DELETE FROM results WHERE test_id = ?", (test_id,))

                # Insert results and scores
                for result in results:
                    cursor.execute(
                        """
                        INSERT INTO results (test_id, item_id, dataset_row, error, timestamp, prompt)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            test_id,
                            result.item_id,
                            json.dumps(_serialize_value(result.dataset_row)),
                            result.error,
                            result.timestamp,
                            result.sample.prompt,
                        ),
                    )
                    result_id = cursor.lastrowid

                    # Insert scores
                    for score in result.sample.scores:
                        cursor.execute(
                            """
                            INSERT INTO scores (result_id, evaluator_name, value, metrics, metadata)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                result_id,
                                score.name,
                                json.dumps(score.value),
                                json.dumps([m.__name__ for m in score.metrics]),
                                json.dumps(score.metadata),
                            ),
                        )

    def load(self, name: str) -> Optional[Session]:
        """Load a Session instance from the SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Load session metadata
            cursor.execute(
                """
                SELECT metadata, created_at, status FROM sessions WHERE name = ?
                """,
                (name,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            metadata_json, created_at, status = row
            session = Session(
                name=name,
                metadata=json.loads(metadata_json),
                created_at=created_at,
                status=SessionStatus(status),
            )

            # Load all tests for this session
            cursor.execute(
                """
                SELECT id, test_name FROM tests WHERE session_name = ?
                """,
                (name,),
            )
            tests = cursor.fetchall()

            for test_id, test_name in tests:
                # Load results for this test
                cursor.execute(
                    """
                    SELECT id, item_id, dataset_row, error, timestamp, prompt
                    FROM results WHERE test_id = ?
                    ORDER BY item_id
                    """,
                    (test_id,),
                )
                results = []

                for result_row in cursor.fetchall():
                    (
                        result_id,
                        item_id,
                        dataset_row_json,
                        error,
                        timestamp,
                        prompt,
                    ) = result_row

                    # Load scores for this result
                    cursor.execute(
                        """
                        SELECT evaluator_name, value, metrics, metadata
                        FROM scores WHERE result_id = ?
                        """,
                        (result_id,),
                    )
                    scores = []

                    for score_row in cursor.fetchall():
                        (
                            evaluator_name,
                            value_json,
                            metrics_json,
                            metadata_json,
                        ) = score_row
                        metrics = [registry[name] for name in json.loads(metrics_json)]
                        score = Score(
                            name=evaluator_name,
                            value=json.loads(value_json),
                            metrics=metrics,
                            metadata=json.loads(metadata_json),
                        )
                        scores.append(score)

                    sample = Sample(prompt=prompt, scores=scores)
                    result = EvaluationResult(
                        sample=sample,
                        item_id=item_id,
                        dataset_row=_deserialize_value(json.loads(dataset_row_json)),
                        error=error,
                        timestamp=timestamp,
                    )
                    results.append(result)

                session.results[test_name] = results

            return session

    def list_names(self) -> list[str]:
        """List all session names"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sessions")
            return [row[0] for row in cursor.fetchall()]

    def rename(self, old_name: str, new_name: str):
        """Rename a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sessions SET name = ? WHERE name = ?", (new_name, old_name)
            )
            cursor.execute(
                "UPDATE tests SET session_name = ? WHERE session_name = ?",
                (new_name, old_name),
            )
            cursor.execute(
                "UPDATE locks SET session_name = ? WHERE session_name = ?",
                (new_name, old_name),
            )

    def delete(self, name: str):
        """Delete a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE name = ?", (name,))
            if cursor.rowcount == 0:
                raise ValueError(f"{name}: session not found.")
            cursor.execute("DELETE FROM locks WHERE session_name = ?", (name,))

    def acquire_lock(self, name: str):
        """Acquire a lock for a session to track it's running"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO locks (session_name) VALUES (?)", (name,))
            except sqlite3.IntegrityError:
                raise RuntimeError(f"Session '{name}' is already locked.")

    def release_lock(self, name: str):
        """Release a lock when session completes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM locks WHERE session_name = ?", (name,))

    def is_locked(self, name: str) -> bool:
        """Check if a session is locked (still running or interrupted)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM locks WHERE session_name = ?", (name,))
            return cursor.fetchone()[0] > 0

    # Query helper methods for error analysis

    def get_failed_results(
        self,
        session_name: str,
        test_name: Optional[str] = None,
        evaluator_name: Optional[str] = None,
    ) -> list[dict]:
        """Get all failed results (score = False or 0) for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = """
                SELECT
                    t.test_name,
                    r.item_id,
                    r.dataset_row,
                    r.error,
                    r.timestamp,
                    s.evaluator_name,
                    s.value,
                    s.metadata
                FROM results r
                JOIN tests t ON r.test_id = t.id
                JOIN scores s ON s.result_id = r.id
                WHERE t.session_name = ?
                AND (s.value = 'false' OR s.value = '0' OR s.value = '0.0')
            """
            params = [session_name]

            if test_name:
                query += " AND t.test_name = ?"
                params.append(test_name)

            if evaluator_name:
                query += " AND s.evaluator_name = ?"
                params.append(evaluator_name)

            query += " ORDER BY t.test_name, r.item_id"

            cursor.execute(query, params)

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "test_name": row[0],
                        "item_id": row[1],
                        "dataset_row": _deserialize_value(json.loads(row[2])),
                        "error": row[3],
                        "timestamp": row[4],
                        "evaluator_name": row[5],
                        "value": json.loads(row[6]),
                        "metadata": json.loads(row[7]),
                    }
                )

            return results

    def get_error_results(
        self, session_name: str, test_name: Optional[str] = None
    ) -> list[dict]:
        """Get all results that had errors during evaluation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = """
                SELECT
                    t.test_name,
                    r.item_id,
                    r.dataset_row,
                    r.error,
                    r.timestamp
                FROM results r
                JOIN tests t ON r.test_id = t.id
                WHERE t.session_name = ?
                AND r.error IS NOT NULL
            """
            params = [session_name]

            if test_name:
                query += " AND t.test_name = ?"
                params.append(test_name)

            query += " ORDER BY t.test_name, r.item_id"

            cursor.execute(query, params)

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "test_name": row[0],
                        "item_id": row[1],
                        "dataset_row": json.loads(row[2]),
                        "error": row[3],
                        "timestamp": row[4],
                    }
                )

            return results


# Register the SQLite backend
_registry.register("sqlite", SQLiteStorage)
