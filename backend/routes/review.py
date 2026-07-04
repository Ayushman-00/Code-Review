import os
from fastapi import APIRouter, HTTPException
from models import ReviewRequest, ReviewResponse, PRInfo
from services import github as github_service
from services import groq as groq_service

router = APIRouter()


@router.post(
    "/review",
    response_model=ReviewResponse,
    summary="Review a GitHub PR",
    description=(
        "Submit a public GitHub PR URL and receive an AI-powered code review "
        "with issues categorised by severity, file, line number, and suggested fix."
    ),
    responses={
        400: {"description": "Invalid PR URL format"},
        422: {"description": "PR not accessible or no reviewable diff found"},
        502: {"description": "GitHub API error"},
        503: {"description": "AI review service unavailable"},
    },
)
async def review_pr(request: ReviewRequest):
    # ── Step 1: Parse and validate the PR URL ─────────────────────────────
    try:
        owner, repo, pr_number = github_service.parse_pr_url(request.pr_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # ── Step 2: Fetch PR metadata + changed files from GitHub ─────────────
    github_token = os.getenv("GITHUB_TOKEN")

    try:
        pr_data = await github_service.fetch_pr_info(owner, repo, pr_number, github_token)
        pr_files = await github_service.fetch_pr_files(owner, repo, pr_number, github_token)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch PR data from GitHub: {exc}",
        )

    # ── Step 3: Format the diff for the AI ───────────────────────────────
    diff = github_service.format_diff_for_review(pr_files)

    if not diff.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "No reviewable code changes found in this PR. "
                "The diff may consist entirely of binary or empty files."
            ),
        )

    # ── Step 4: Run AI review via Groq ────────────────────────────────────
    try:
        raw_review = await groq_service.review_code(
            diff=diff,
            pr_title=pr_data.get("title", "Untitled PR"),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"AI review service is currently unavailable: {exc}",
        )

    # ── Step 5: Parse AI response into typed models ───────────────────────
    issues = groq_service.parse_issues(raw_review.get("issues", []))

    pr_info = PRInfo(
        title=pr_data.get("title", "Untitled"),
        author=pr_data.get("user", {}).get("login", "unknown"),
        files_changed=pr_data.get("changed_files", len(pr_files)),
        additions=pr_data.get("additions", 0),
        deletions=pr_data.get("deletions", 0),
        pr_url=request.pr_url,
    )

    return ReviewResponse(
        pr_info=pr_info,
        issues=issues,
        summary=raw_review.get("summary", "Review completed."),
        total_issues=len(issues),
    )