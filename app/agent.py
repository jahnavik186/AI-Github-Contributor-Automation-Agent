from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from typing import List
from urllib import parse, request
from urllib.error import HTTPError, URLError

from app.schemas import (
    AnalyzeResponse,
    DiscoverResponse,
    DiscoveredIssue,
    DocsUpdate,
    EndToEndResponse,
    FileChangePreview,
    FixProposal,
    IssuePlanResponse,
    IssueCandidate,
    IssuePrDraftResponse,
    PullRequestDraft,
)


@dataclass(frozen=True)
class RepoPattern:
    keyword: str
    title: str
    severity: str
    file_path: str
    rationale: str


PATTERNS = [
    RepoPattern(
        keyword="api",
        title="Inconsistent API error handling",
        severity="high",
        file_path="src/api/routes.py",
        rationale="Some routes return raw exceptions instead of typed HTTP responses.",
    ),
    RepoPattern(
        keyword="test",
        title="Missing regression tests for edge cases",
        severity="medium",
        file_path="tests/test_regression.py",
        rationale="No coverage found for malformed input and timeout scenarios.",
    ),
    RepoPattern(
        keyword="docs",
        title="README setup steps outdated",
        severity="low",
        file_path="README.md",
        rationale="Installation instructions do not reflect current commands.",
    ),
]

GITHUB_API_BASE = "https://api.github.com"
OPENAI_API_BASE = "https://api.openai.com/v1/chat/completions"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"

GOOD_FIRST_LABELS = {
    "good first issue",
    "good-first-issue",
    "good_first_issue",
    "beginner",
    "starter",
    "easy",
}
INTERMEDIATE_LABELS = {
    "help wanted",
    "enhancement",
    "documentation",
    "docs",
    "tests",
    "refactor",
}
HARD_LABELS = {
    "hard",
    "advanced",
    "complex",
    "performance",
    "research",
    "high priority",
}

FILE_HINT_PATTERN = re.compile(r"\b[\w./-]+\.(?:py|md|rst|txt|js|ts|json|yaml|yml|toml)\b", re.IGNORECASE)


def _infer_change_type(file_path: str) -> str:
    lower_path = file_path.lower()
    if "test" in lower_path or lower_path.startswith("tests/"):
        return "test"
    if lower_path.endswith((".md", ".rst", ".txt")):
        return "docs"
    if lower_path.endswith((".json", ".yaml", ".yml", ".toml")):
        return "config"
    return "code"


def _change_template(file_path: str, likely_changes: List[str], change_type: str) -> tuple[int, str, str]:
    cue = likely_changes[0] if likely_changes else "Apply targeted fix for the issue scenario"
    if change_type == "test":
        return (
            20,
            "Low regression risk after adding focused coverage.",
            (
                f"--- a/{file_path}\n"
                f"+++ b/{file_path}\n"
                "@@ add regression scenario @@\n"
                "- assert old behavior\n"
                "+ assert protected behavior for issue case\n"
                "+ assert no regression for existing happy path"
            ),
        )
    if change_type == "docs":
        return (
            12,
            "Documentation-only update with very low runtime risk.",
            (
                f"--- a/{file_path}\n"
                f"+++ b/{file_path}\n"
                "@@ clarify behavior and usage @@\n"
                "- previous instructions\n"
                "+ updated instructions tied to issue fix\n"
                "+ add verification notes for contributors"
            ),
        )
    if change_type == "config":
        return (
            14,
            "Config/schema updates can impact deployment defaults.",
            (
                f"--- a/{file_path}\n"
                f"+++ b/{file_path}\n"
                "@@ tighten config defaults @@\n"
                "- permissive/legacy option\n"
                "+ safer default aligned with issue requirements\n"
                "+ add inline note for migration impact"
            ),
        )
    return (
        28,
        f"Core logic adjustment expected: {cue}.",
        (
            f"--- a/{file_path}\n"
            f"+++ b/{file_path}\n"
            "@@ implement minimal safe fix @@\n"
            "- return overly broad provider payload\n"
            "+ return scoped payload with required fields only\n"
            "+ add guard clause for unauthorized access path"
        ),
    )


def _build_file_change_previews(changed_files: List[str], likely_changes: List[str]) -> List[FileChangePreview]:
    previews: List[FileChangePreview] = []
    for file_path in changed_files:
        change_type = _infer_change_type(file_path=file_path)
        estimated_lines, impact, pseudo_diff = _change_template(
            file_path=file_path,
            likely_changes=likely_changes,
            change_type=change_type,
        )
        previews.append(
            FileChangePreview(
                file_path=file_path,
                change_type=change_type,
                estimated_lines_changed=estimated_lines,
                impact=impact,
                pseudo_diff=pseudo_diff,
            )
        )
    return previews


def _estimate_effort(
    changed_files: List[str], likely_changes: List[str], labels: List[str], comments: int
) -> tuple[str, int, str]:
    score = 1
    score += min(4, len(changed_files))
    score += min(2, len(likely_changes))
    score += 2 if comments >= 10 else 0
    hard_hits = {"hard", "advanced", "complex", "performance", "high priority"}
    good_first_hits = {"good first issue", "good-first-issue", "good_first_issue", "beginner", "easy"}
    label_set = {label.lower() for label in labels}
    if label_set & hard_hits:
        score += 2
    if label_set & good_first_hits:
        score = max(1, score - 1)

    if score <= 4:
        return "easy", score, "Likely a small, focused fix with limited file touch points."
    if score <= 7:
        return "medium", score, "Moderate scope: code + tests/docs updates are likely required."
    return "high", score, "Broader change set expected; budget time for validation and iteration."


def _github_get_json(path: str, query: dict[str, str | int] | None = None) -> dict | list:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    query_string = f"?{parse.urlencode(query)}" if query else ""
    url = f"{GITHUB_API_BASE}{path}{query_string}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ai-github-contributor-automation-agent",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = request.Request(url=url, headers=headers, method="GET")
    try:
        with request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API error {exc.code} for {url}: {message}") from exc
    except URLError as exc:
        raise RuntimeError(f"GitHub API connection failed for {url}: {exc}") from exc


def _search_issues(global_query: str, per_page: int = 10) -> List[dict]:
    try:
        payload = _github_get_json(
            "/search/issues",
            query={"q": global_query, "sort": "updated", "order": "desc", "per_page": per_page},
        )
    except RuntimeError as exc:
        text = str(exc)
        if "GitHub API error 422" in text:
            return []
        raise
    if not isinstance(payload, dict):
        return []
    return [item for item in payload.get("items", []) if isinstance(item, dict)]


def _is_beginner_friendly(labels: List[str], comments: int) -> bool:
    label_set = {label.lower() for label in labels}
    if label_set & GOOD_FIRST_LABELS:
        return True
    return bool(label_set & {"help wanted", "documentation", "docs", "tests"}) and comments <= 8


def _openai_json_plan(
    repo: str,
    issue_number: int,
    title: str,
    body: str,
    labels: List[str],
    comments: int,
) -> dict | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL
    excerpt = body[:5000]
    prompt = (
        "You are a senior open-source mentor. Suggest beginner-friendly implementation guidance.\n"
        "Return strict JSON with keys:\n"
        "likely_changes (array of 1-4 short strings),\n"
        "suggested_first_steps (array of 3-5 short strings),\n"
        "changed_files (array of 1-8 file paths),\n"
        "effort_level (easy|medium|high),\n"
        "effort_score (integer 1-10),\n"
        "effort_summary (short string).\n"
        "Keep recommendations minimal and safe.\n\n"
        f"Repo: {repo}\n"
        f"Issue number: {issue_number}\n"
        f"Issue title: {title}\n"
        f"Labels: {', '.join(labels) if labels else 'none'}\n"
        f"Comments: {comments}\n"
        f"Issue body:\n{excerpt}"
    )

    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": "Return JSON only. No markdown."},
            {"role": "user", "content": prompt},
        ],
    }

    req = request.Request(
        url=OPENAI_API_BASE,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

    try:
        content = raw["choices"][0]["message"]["content"]
        parsed = json.loads(content)
    except Exception:
        return None

    if not isinstance(parsed, dict):
        return None
    return parsed


def _normalize_ai_plan(ai_plan: dict | None) -> tuple[List[str], List[str], List[str], tuple[str, int, str]] | None:
    if not ai_plan:
        return None

    likely_changes = [str(item).strip() for item in ai_plan.get("likely_changes", []) if str(item).strip()][:4]
    first_steps = [str(item).strip() for item in ai_plan.get("suggested_first_steps", []) if str(item).strip()][:5]
    changed_files = [str(item).strip() for item in ai_plan.get("changed_files", []) if str(item).strip()][:8]
    effort_level = str(ai_plan.get("effort_level", "medium")).lower().strip()
    effort_score = ai_plan.get("effort_score", 5)
    effort_summary = str(ai_plan.get("effort_summary", "")).strip()

    if effort_level not in {"easy", "medium", "high"}:
        effort_level = "medium"
    if not isinstance(effort_score, int):
        try:
            effort_score = int(effort_score)
        except Exception:
            effort_score = 5
    effort_score = max(1, min(10, effort_score))

    if not likely_changes or not first_steps or not changed_files or not effort_summary:
        return None

    return likely_changes, first_steps, changed_files, (effort_level, effort_score, effort_summary)


def _label_names(raw_issue: dict) -> List[str]:
    return [str(item.get("name", "")).strip() for item in raw_issue.get("labels", []) if item.get("name")]


def _is_pull_request(raw_issue: dict) -> bool:
    return "pull_request" in raw_issue


def _matches_difficulty(label_set: set[str], difficulty: str) -> tuple[bool, str]:
    if difficulty == "good_first":
        ok = bool(label_set & GOOD_FIRST_LABELS)
        return ok, "labeled beginner-friendly"
    if difficulty == "hard":
        ok = bool(label_set & HARD_LABELS)
        return ok, "labeled advanced/complex"

    if label_set & HARD_LABELS:
        return False, ""
    if label_set & GOOD_FIRST_LABELS:
        return False, ""
    ok = bool(label_set & INTERMEDIATE_LABELS) or bool(label_set)
    return ok, "moderate scope based on issue labels"


def _likely_changes(title: str, body: str, labels: List[str]) -> List[str]:
    hints: List[str] = []
    lowered_title = title.lower()
    lowered_body = body.lower()
    lowered_labels = {label.lower() for label in labels}

    if "docs" in lowered_labels or "documentation" in lowered_labels or "readme" in lowered_title:
        hints.append("Update README/docs content and related usage examples")
    if "test" in lowered_title or "tests" in lowered_labels or "regression" in lowered_body:
        hints.append("Add or adjust unit/integration tests for the reported behavior")
    if any(token in lowered_title for token in ["bug", "error", "fix", "exception"]):
        hints.append("Patch source logic where the bug occurs and add guard/error handling")
    if any(token in lowered_labels for token in ["performance", "complex", "advanced", "hard"]):
        hints.append("Benchmark current behavior before optimization and compare after changes")
    if any(token in lowered_title for token in ["ui", "frontend", "display"]):
        hints.append("Modify frontend components/styles and verify behavior on desktop and mobile")

    matched_files = []
    for match in FILE_HINT_PATTERN.finditer(body):
        file_hint = match.group(0)
        if file_hint not in matched_files:
            matched_files.append(file_hint)
    if matched_files:
        hints.append("Issue body references files; inspect the mentioned paths first")

    if not hints:
        hints.append("Read issue discussion, identify smallest reproducible fix, and add focused tests")
    return hints[:4]


def _normalize_topic_query(topic: str) -> str:
    cleaned = topic.strip().lower()
    if not cleaned:
        return "artificial intelligence"
    tokens = re.findall(r"[a-zA-Z0-9+#.-]+", cleaned)[:6]
    return " ".join(tokens) if tokens else "artificial intelligence"


def discover_issues(topic: str, difficulty: str, limit: int) -> DiscoverResponse:
    normalized_topic = _normalize_topic_query(topic)
    discovered: List[DiscoveredIssue] = []
    seen_keys: set[str] = set()
    per_query_limit = min(30, max(10, limit))

    query_templates: List[str] = []
    if difficulty == "good_first":
        query_templates = [
            f'is:issue is:open archived:false no:assignee "{normalized_topic}" label:"good first issue"',
            f'is:issue is:open archived:false no:assignee "{normalized_topic}" label:beginner',
            f'is:issue is:open archived:false no:assignee "{normalized_topic}" label:"help wanted"',
        ]
    elif difficulty == "hard":
        query_templates = [
            f'is:issue is:open archived:false "{normalized_topic}" label:performance',
            f'is:issue is:open archived:false "{normalized_topic}" label:complex',
            f'is:issue is:open archived:false "{normalized_topic}" label:research',
        ]
    else:
        query_templates = [
            f'is:issue is:open archived:false "{normalized_topic}" -label:"good first issue"',
            f'is:issue is:open archived:false "{normalized_topic}" label:enhancement',
            f'is:issue is:open archived:false "{normalized_topic}" label:bug',
        ]

    raw_issues: List[dict] = []
    for query in query_templates:
        raw_issues.extend(_search_issues(global_query=query, per_page=per_query_limit))

    for raw_issue in raw_issues:
        if _is_pull_request(raw_issue):
            continue
        repo = str(raw_issue.get("repository_url", "")).replace("https://api.github.com/repos/", "").strip()
        if not repo:
            continue
        key = f"{repo}#{raw_issue.get('number')}"
        if key in seen_keys:
            continue
        labels = _label_names(raw_issue)
        label_set = {label.lower() for label in labels}
        match, why = _matches_difficulty(label_set=label_set, difficulty=difficulty)
        if not match and difficulty == "good_first":
            is_beginnerish = bool(label_set & {"help wanted", "documentation", "docs", "tests", "question"})
            low_comments = int(raw_issue.get("comments", 0)) <= 5
            match = is_beginnerish and low_comments
            if match:
                why = "beginner-like fallback (low discussion and newcomer-friendly labels)"
        if not match and difficulty == "hard":
            high_discussion = int(raw_issue.get("comments", 0)) >= 15
            complex_words = any(
                token in str(raw_issue.get("title", "")).lower()
                for token in ["performance", "scal", "distributed", "refactor", "architecture", "optimiz"]
            )
            match = high_discussion or complex_words
            if match:
                why = "hard fallback (high discussion or complex-scope keywords)"
        if not match:
            continue

        issue = DiscoveredIssue(
            repo=repo,
            issue_number=int(raw_issue["number"]),
            title=str(raw_issue["title"]),
            html_url=str(raw_issue["html_url"]),
            created_at=str(raw_issue["created_at"]),
            updated_at=str(raw_issue["updated_at"]),
            comments=int(raw_issue.get("comments", 0)),
            labels=labels,
            difficulty=difficulty,
            likely_changes=_likely_changes(
                title=str(raw_issue["title"]),
                body=str(raw_issue.get("body") or ""),
                labels=labels,
            ),
            why_match=why,
        )
        discovered.append(issue)
        seen_keys.add(key)
        if len(discovered) >= limit:
            break

    checked_repos = sorted({item.repo for item in discovered})[:100]
    return DiscoverResponse(
        topic=normalized_topic,
        difficulty=difficulty,
        repositories_checked=checked_repos,
        issues=discovered,
    )


def plan_issue_changes(repo: str, issue_number: int) -> IssuePlanResponse:
    raw_issue = _github_get_json(f"/repos/{repo}/issues/{issue_number}")
    if _is_pull_request(raw_issue):
        raise ValueError("Selected item is a pull request, not an issue")
    labels = _label_names(raw_issue)
    issue_title = str(raw_issue.get("title", ""))
    issue_body = str(raw_issue.get("body") or "")
    comments = int(raw_issue.get("comments", 0))
    likely_changes = _likely_changes(
        title=issue_title,
        body=issue_body,
        labels=labels,
    )
    first_steps = [
        "Reproduce or understand expected behavior from issue description/comments",
        "Locate impacted files/modules and implement the smallest safe change",
        "Add/update tests to cover the scenario and verify no regression",
        "Prepare PR summary with what changed, why, and validation evidence",
    ]
    file_hints = [m.group(0) for m in FILE_HINT_PATTERN.finditer(issue_body)]
    changed_files = sorted(set(file_hints))[:8]
    if not changed_files:
        changed_files = ["tests/", "README.md"]
    suggestion_source = "heuristic"
    ai_plan = None
    if _is_beginner_friendly(labels=labels, comments=comments):
        ai_plan = _normalize_ai_plan(
            _openai_json_plan(
                repo=repo,
                issue_number=issue_number,
                title=issue_title,
                body=issue_body,
                labels=labels,
                comments=comments,
            )
        )
    if ai_plan:
        likely_changes, first_steps, changed_files, effort = ai_plan
        effort_level, effort_score, effort_summary = effort
        suggestion_source = "generative_model"
    else:
        effort_level, effort_score, effort_summary = _estimate_effort(
            changed_files=changed_files,
            likely_changes=likely_changes,
            labels=labels,
            comments=comments,
        )
    proposed_file_changes = _build_file_change_previews(changed_files=changed_files, likely_changes=likely_changes)

    return IssuePlanResponse(
        repo=repo,
        issue_number=issue_number,
        title=issue_title,
        html_url=str(raw_issue.get("html_url", "")),
        labels=labels,
        likely_changes=likely_changes,
        suggested_first_steps=first_steps,
        effort_level=effort_level,
        effort_score=effort_score,
        effort_summary=effort_summary,
        suggestion_source=suggestion_source,
        proposed_file_changes=proposed_file_changes,
    )


def create_pr_draft_from_issue(repo: str, issue_number: int) -> IssuePrDraftResponse:
    raw_issue = _github_get_json(f"/repos/{repo}/issues/{issue_number}")
    if _is_pull_request(raw_issue):
        raise ValueError("Selected item is a pull request, not an issue")

    title = str(raw_issue.get("title", ""))
    body = str(raw_issue.get("body") or "")
    labels = _label_names(raw_issue)
    comments = int(raw_issue.get("comments", 0))
    likely_changes = _likely_changes(title=title, body=body, labels=labels)
    file_hints = [m.group(0) for m in FILE_HINT_PATTERN.finditer(body)]
    changed_files = sorted(set(file_hints))[:8]
    if not changed_files:
        changed_files = ["tests/", "README.md"]
    first_steps = [
        "Reproduce or understand expected behavior from issue description/comments",
        "Locate impacted files/modules and implement the smallest safe change",
        "Add/update tests to cover the scenario and verify no regression",
        "Prepare PR summary with what changed, why, and validation evidence",
    ]
    suggestion_source = "heuristic"
    ai_plan = None
    if _is_beginner_friendly(labels=labels, comments=comments):
        ai_plan = _normalize_ai_plan(
            _openai_json_plan(
                repo=repo,
                issue_number=issue_number,
                title=title,
                body=body,
                labels=labels,
                comments=comments,
            )
        )
    if ai_plan:
        likely_changes, first_steps, changed_files, effort = ai_plan
        effort_level, effort_score, effort_summary = effort
        suggestion_source = "generative_model"
    else:
        effort_level, effort_score, effort_summary = _estimate_effort(
            changed_files=changed_files,
            likely_changes=likely_changes,
            labels=labels,
            comments=comments,
        )
    proposed_file_changes = _build_file_change_previews(changed_files=changed_files, likely_changes=likely_changes)

    pr_title = f"fix: resolve #{issue_number} - {title[:72]}"
    changes_bullets = "\n".join(f"- {item}" for item in likely_changes)
    files_bullets = "\n".join(f"- `{path}`" for path in changed_files)
    pr_body = (
        "## Summary\n"
        f"Closes #{issue_number}.\n\n"
        "## Proposed Approach\n"
        f"{changes_bullets}\n\n"
        "## Beginner-Friendly Implementation Steps\n"
        + "\n".join(f"- {step}" for step in first_steps)
        + "\n\n"
        "## Likely Touched Files\n"
        f"{files_bullets}\n\n"
        "## Validation Plan\n"
        "- Add/update focused tests for the issue scenario\n"
        "- Run project test suite for impacted modules\n"
        "- Update docs/comments if behavior changed"
    )

    return IssuePrDraftResponse(
        repo=repo,
        issue_number=issue_number,
        issue_title=title,
        pr_title=pr_title,
        pr_body=pr_body,
        changed_files=changed_files,
        effort_level=effort_level,
        effort_score=effort_score,
        effort_summary=effort_summary,
        suggestion_source=suggestion_source,
        proposed_file_changes=proposed_file_changes,
    )


def detect_issues(repo: str, branch: str) -> AnalyzeResponse:
    lowered = repo.lower()
    matches: List[IssueCandidate] = []

    for index, pattern in enumerate(PATTERNS, start=1):
        if pattern.keyword in lowered or len(matches) < 2:
            matches.append(
                IssueCandidate(
                    id=f"ISSUE-{index}",
                    title=pattern.title,
                    severity=pattern.severity,
                    file_path=pattern.file_path,
                    rationale=pattern.rationale,
                )
            )

    # Keep results deterministic and compact for demos.
    issues = matches[:3]
    return AnalyzeResponse(repo=repo, branch=branch, issues=issues)


def propose_fixes(issues: List[IssueCandidate]) -> List[FixProposal]:
    return [
        FixProposal(
            issue_id=issue.id,
            patch_summary=(
                f"Refactor {issue.file_path} to address '{issue.title}' with guarded logic and explicit error mapping."
            ),
            test_plan="Add unit tests for failure paths and one integration test for happy-path.",
            risk_level="medium" if issue.severity in {"high", "medium"} else "low",
        )
        for issue in issues
    ]


def generate_pr(repo: str, fixes: List[FixProposal], issues: List[IssueCandidate]) -> PullRequestDraft:
    changed_files = sorted({issue.file_path for issue in issues} | {"README.md"})
    bullet_lines = "\n".join([f"- {fix.issue_id}: {fix.patch_summary}" for fix in fixes])

    return PullRequestDraft(
        title=f"feat(agent): autonomous maintenance updates for {repo}",
        body=(
            "## Summary\n"
            "This PR was drafted by the AI GitHub Contributor Automation Agent.\n\n"
            "## Proposed Fixes\n"
            f"{bullet_lines}\n\n"
            "## Validation\n"
            "- Added/updated tests for impacted workflows\n"
            "- Updated documentation for new behavior"
        ),
        changed_files=changed_files,
    )


def update_docs(repo: str, issues: List[IssueCandidate]) -> DocsUpdate:
    issue_titles = ", ".join(issue.title for issue in issues)
    return DocsUpdate(
        section="README > Maintenance and Contribution",
        update_text=(
            f"For {repo}, the contributor agent now auto-detects issues ({issue_titles}) and drafts PR-ready fixes."
        ),
    )


def run_end_to_end(repo: str, branch: str) -> EndToEndResponse:
    analysis = detect_issues(repo=repo, branch=branch)
    fixes = propose_fixes(analysis.issues)
    pr_draft = generate_pr(repo=repo, fixes=fixes, issues=analysis.issues)
    docs = update_docs(repo=repo, issues=analysis.issues)
    return EndToEndResponse(analyze=analysis, fixes=fixes, pr_draft=pr_draft, docs_update=docs)
