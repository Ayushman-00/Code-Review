import os
from fastapi import APIRouter, HTTPException, Query
from models import ValidatePRResponse
from services import github as github_service

router = APIRouter()


@router.get(
    "/github/validate",
    response_model=ValidatePRResponse,
    summary="Validate a GitHub PR URL",
    description=(
        "Check that a PR URL is correctly formatted and the PR is accessible "
        "before submitting it for a full review. Useful for frontend pre-validation."
    ),
    responses={
        400: {"description": "Malformed PR URL"},
        422: {"description": "PR not found or not accessible"},
        502: {"description": "GitHub API error"},
    },
)
async def validate_pr(
    pr_url: str = Query(..., description="Full GitHub PR URL to validate"),
):
    # Parse URL format first
    try:
        owner, repo, pr_number = github_service.parse_pr_url(pr_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Hit GitHub to confirm the PR exists and is readable
    github_token = os.getenv("GITHUB_TOKEN")

    try:
        pr_data = await github_service.fetch_pr_info(owner, repo, pr_number, github_token)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return ValidatePRResponse(
        valid=True,
        pr_title=pr_data.get("title"),
        author=pr_data.get("user", {}).get("login"),
        state=pr_data.get("state"),
        files_changed=pr_data.get("changed_files"),
    )