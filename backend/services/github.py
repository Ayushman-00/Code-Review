import re
import httpx
from typing import Optional, Tuple

GITHUB_API_BASE = "https://api.github.com"
MAX_FILES_TO_REVIEW = 10      # cap to stay within Groq token limits
MAX_PATCH_LENGTH = 3000        # truncate huge diffs per file


def parse_pr_url(pr_url: str) -> Tuple[str, str, int]:
    """Extract owner, repo, and PR number from a GitHub PR URL."""
    pattern = r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.match(pattern, pr_url.strip())
    if not match:
        raise ValueError(
            "Invalid GitHub PR URL. Expected format: "
            "https://github.com/owner/repo/pull/123"
        )
    owner, repo, pr_number = match.groups()
    return owner, repo, int(pr_number)


def _build_headers(token: Optional[str]) -> dict:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def fetch_pr_info(
    owner: str, repo: str, pr_number: int, token: Optional[str] = None
) -> dict:
    """Fetch PR metadata (title, author, stats) from GitHub API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}",
            headers=_build_headers(token),
        )

    if response.status_code == 404:
        raise ValueError("PR not found. Make sure the repository is public and the PR URL is correct.")
    if response.status_code == 403:
        raise ValueError(
            "GitHub API rate limit exceeded. "
            "Add a GITHUB_TOKEN to your .env file to increase the limit."
        )
    if response.status_code != 200:
        raise ValueError(f"GitHub API returned an unexpected status: {response.status_code}")

    return response.json()


async def fetch_pr_files(
    owner: str, repo: str, pr_number: int, token: Optional[str] = None
) -> list:
    """Fetch the list of files changed in the PR, including their diffs."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/files",
            headers=_build_headers(token),
        )
    response.raise_for_status()
    return response.json()


def format_diff_for_review(files: list) -> str:
    """
    Convert raw GitHub file objects into a clean, token-efficient
    string suitable for sending to an LLM.
    """
    formatted_blocks = []
    skipped = 0

    for file in files[:MAX_FILES_TO_REVIEW]:
        filename = file.get("filename", "unknown")
        status = file.get("status", "modified")       # added | modified | removed
        patch = file.get("patch", "")

        if not patch:
            skipped += 1
            continue

        # Truncate very large patches to keep token usage sane
        if len(patch) > MAX_PATCH_LENGTH:
            patch = patch[:MAX_PATCH_LENGTH] + "\n... [diff truncated for length]"

        formatted_blocks.append(
            f"=== {filename} ({status}) ===\n{patch}\n"
        )

    if not formatted_blocks:
        return ""

    header = f"[Showing {len(formatted_blocks)} file(s)"
    if skipped:
        header += f", {skipped} binary/empty file(s) skipped"
    if len(files) > MAX_FILES_TO_REVIEW:
        header += f", {len(files) - MAX_FILES_TO_REVIEW} file(s) omitted due to limit"
    header += "]\n\n"

    return header + "\n".join(formatted_blocks)