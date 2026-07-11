import os
import json
import re
import asyncio
from groq import Groq
from typing import List
from models import ReviewIssue, Severity
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

REVIEW_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a staff-level software engineer at a top tech company.
Review the PR diff below and identify ONLY real, specific issues — not generic advice.

For every issue you find, you MUST reference:
- The exact filename
- The exact line number if visible
- What the actual bug/risk is in plain English
- A concrete corrected code snippet

Categorise each issue as:
- critical  → will cause a bug, crash, security hole, or data loss RIGHT NOW
- warning   → won't crash today but is a ticking time bomb (memory leak, race condition, no auth check)
- suggestion → cleaner way to write it, nothing will break if ignored

REJECT these as issues (do not report them):
- Stylistic preferences (single vs double quotes, tabs vs spaces)
- Missing comments on obvious code
- "Consider using X instead of Y" without a real reason

You MUST respond ONLY in this exact JSON format, no markdown, no extra text:
{
  "issues": [
    {
      "severity": "critical" | "warning" | "suggestion",
      "file": "exact/path/file.py",
      "line": 42,
      "message": "Specific problem explained in one sentence",
      "fix": "exact corrected code snippet"
    }
  ],
  "summary": "2 sentences: what this PR does well, and the single most important thing to fix"
}

If the PR is genuinely clean, return empty issues array. Do not invent problems."""



async def review_code(diff: str, pr_title: str) -> dict:
    """
    Send a formatted PR diff to Groq (Llama 3 70B) and return
    a structured JSON review object.
    """
    user_prompt = f"""Review this GitHub Pull Request:

PR Title: {pr_title}

Code Changes:
{diff}

Return your structured JSON review now."""

    response = client.chat.completions.create(
        model=REVIEW_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,    # low temperature = consistent, focused output
        max_tokens=2048,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if the model adds them despite instructions
    raw = re.sub(r"```(?:json)?|```", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Graceful fallback — surface whatever the model said as the summary
        return {
            "issues": [],
            "summary": raw[:500] if raw else "Review completed but the response could not be parsed.",
        }


def parse_issues(raw_issues: list) -> List[ReviewIssue]:
    """
    Convert the raw list of issue dicts from the AI response
    into validated ReviewIssue Pydantic models.
    Malformed entries are silently skipped to prevent a single
    bad item from crashing the whole response.
    """
    issues: List[ReviewIssue] = []

    for item in raw_issues:
        try:
            severity_raw = str(item.get("severity", "suggestion")).lower()
            if severity_raw not in {"critical", "warning", "suggestion"}:
                severity_raw = "suggestion"

            issues.append(
                ReviewIssue(
                    severity=Severity(severity_raw),
                    file=item.get("file", "unknown"),
                    line=item.get("line"),
                    message=item.get("message", "No description provided."),
                    fix=item.get("fix"),
                )
            )
        except Exception:
            continue     # skip any malformed issue rather than crashing

    return issues