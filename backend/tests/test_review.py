"""
Tests for the AI Code Reviewer backend.
Run with:  pytest tests/ -v
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from services.github import parse_pr_url, format_diff_for_review
from services.groq import parse_issues
from models import Severity

client = TestClient(app)


# ── URL parsing ───────────────────────────────────────────────────────────────

class TestParsePRUrl:
    def test_valid_url(self):
        owner, repo, number = parse_pr_url("https://github.com/facebook/react/pull/99")
        assert owner == "facebook"
        assert repo == "react"
        assert number == 99

    def test_trailing_slash(self):
        owner, repo, number = parse_pr_url("https://github.com/torvalds/linux/pull/1/")
        assert owner == "torvalds"

    def test_invalid_url_raises(self):
        with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
            parse_pr_url("https://github.com/no-pull-segment")

    def test_non_github_url_raises(self):
        with pytest.raises(ValueError):
            parse_pr_url("https://gitlab.com/owner/repo/merge_requests/1")


# ── Diff formatting ───────────────────────────────────────────────────────────

class TestFormatDiff:
    def test_basic_formatting(self):
        files = [
            {"filename": "app.py", "status": "modified", "patch": "+ print('hello')"}
        ]
        result = format_diff_for_review(files)
        assert "app.py" in result
        assert "modified" in result
        assert "print('hello')" in result

    def test_skips_files_with_no_patch(self):
        files = [
            {"filename": "image.png", "status": "added", "patch": ""},
        ]
        result = format_diff_for_review(files)
        assert result == ""

    def test_limits_to_10_files(self):
        files = [
            {"filename": f"file{i}.py", "status": "modified", "patch": f"+ line {i}"}
            for i in range(15)
        ]
        result = format_diff_for_review(files)
        # Only first 10 should appear
        assert "file9.py" in result
        assert "file10.py" not in result


# ── Issue parsing ─────────────────────────────────────────────────────────────

class TestParseIssues:
    def test_valid_issues(self):
        raw = [
            {"severity": "critical", "file": "auth.py", "line": 10,
             "message": "SQL injection risk", "fix": "Use parameterised queries"},
            {"severity": "warning", "file": "utils.py", "line": None,
             "message": "Missing error handling", "fix": "Wrap in try/except"},
        ]
        issues = parse_issues(raw)
        assert len(issues) == 2
        assert issues[0].severity == Severity.CRITICAL
        assert issues[1].severity == Severity.WARNING

    def test_unknown_severity_defaults_to_suggestion(self):
        raw = [{"severity": "unknown", "file": "x.py", "message": "Something"}]
        issues = parse_issues(raw)
        assert issues[0].severity == Severity.SUGGESTION

    def test_malformed_item_is_skipped(self):
        raw = [None, {"severity": "critical", "file": "ok.py", "message": "Real issue"}]
        issues = parse_issues(raw)
        assert len(issues) == 1

    def test_empty_list(self):
        assert parse_issues([]) == []


# ── API endpoints ─────────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_root_returns_ok(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestValidateEndpoint:
    def test_invalid_url_returns_400(self):
        response = client.get("/api/github/validate?pr_url=not-a-url")
        assert response.status_code == 400

    @patch("routes.github.github_service.fetch_pr_info", new_callable=AsyncMock)
    def test_valid_pr_returns_200(self, mock_fetch):
        mock_fetch.return_value = {
            "title": "Fix login bug",
            "user": {"login": "devuser"},
            "state": "open",
            "changed_files": 3,
        }
        response = client.get(
            "/api/github/validate?pr_url=https://github.com/owner/repo/pull/1"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["pr_title"] == "Fix login bug"


class TestReviewEndpoint:
    def test_missing_body_returns_422(self):
        response = client.post("/api/review", json={})
        assert response.status_code == 422

    def test_bad_pr_url_returns_400(self):
        response = client.post("/api/review", json={"pr_url": "not-a-pr-url"})
        assert response.status_code == 400

    @patch("routes.review.github_service.fetch_pr_info", new_callable=AsyncMock)
    @patch("routes.review.github_service.fetch_pr_files", new_callable=AsyncMock)
    @patch("routes.review.groq_service.review_code", new_callable=AsyncMock)
    def test_successful_review(self, mock_ai, mock_files, mock_info):
        mock_info.return_value = {
            "title": "Add feature X",
            "user": {"login": "alice"},
            "changed_files": 1,
            "additions": 10,
            "deletions": 2,
        }
        mock_files.return_value = [
            {"filename": "main.py", "status": "modified",
             "patch": "+ def hello():\n+     print('hi')"}
        ]
        mock_ai.return_value = {
            "issues": [
                {"severity": "suggestion", "file": "main.py", "line": 1,
                 "message": "Add a docstring", "fix": 'def hello():\n    """Greet the user."""\n    print("hi")'}
            ],
            "summary": "Clean PR with minor style improvements needed.",
        }

        response = client.post(
            "/api/review",
            json={"pr_url": "https://github.com/owner/repo/pull/1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_issues"] == 1
        assert data["issues"][0]["severity"] == "suggestion"
        assert data["pr_info"]["author"] == "alice"