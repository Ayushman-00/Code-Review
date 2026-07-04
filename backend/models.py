from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    SUGGESTION = "suggestion"


class ReviewRequest(BaseModel):
    pr_url: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "pr_url": "https://github.com/owner/repo/pull/123"
            }
        }
    }


class ReviewIssue(BaseModel):
    severity: Severity
    file: str
    line: Optional[int] = None
    message: str
    fix: Optional[str] = None


class PRInfo(BaseModel):
    title: str
    author: str
    files_changed: int
    additions: int
    deletions: int
    pr_url: str


class ReviewResponse(BaseModel):
    pr_info: PRInfo
    issues: List[ReviewIssue]
    summary: str
    total_issues: int


class ValidatePRResponse(BaseModel):
    valid: bool
    pr_title: Optional[str] = None
    author: Optional[str] = None
    state: Optional[str] = None
    files_changed: Optional[int] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None