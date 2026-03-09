from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Literal


class AnalyzeRequest(BaseModel):
    repo: str = Field(..., examples=["owner/repository"])
    branch: str = Field(default="main")


class IssueCandidate(BaseModel):
    id: str
    title: str
    severity: str
    file_path: str
    rationale: str


class AnalyzeResponse(BaseModel):
    repo: str
    branch: str
    issues: List[IssueCandidate]


class FixProposal(BaseModel):
    issue_id: str
    patch_summary: str
    test_plan: str
    risk_level: str


class PullRequestDraft(BaseModel):
    title: str
    body: str
    changed_files: List[str]


class DocsUpdate(BaseModel):
    section: str
    update_text: str


class EndToEndResponse(BaseModel):
    analyze: AnalyzeResponse
    fixes: List[FixProposal]
    pr_draft: PullRequestDraft
    docs_update: DocsUpdate


class DiscoverRequest(BaseModel):
    topic: str = Field(..., examples=["llm"])
    difficulty: Literal["good_first", "intermediate", "hard"] = "good_first"
    limit: int = Field(default=12, ge=1, le=30)


class DiscoveredIssue(BaseModel):
    repo: str
    issue_number: int
    title: str
    html_url: str
    created_at: str
    updated_at: str
    comments: int
    labels: List[str]
    difficulty: str
    likely_changes: List[str]
    why_match: str


class DiscoverResponse(BaseModel):
    topic: str
    difficulty: str
    repositories_checked: List[str]
    issues: List[DiscoveredIssue]


class IssuePlanRequest(BaseModel):
    repo: str = Field(..., examples=["huggingface/diffusers"])
    issue_number: int = Field(..., ge=1)


class IssuePlanResponse(BaseModel):
    repo: str
    issue_number: int
    title: str
    html_url: str
    labels: List[str]
    likely_changes: List[str]
    suggested_first_steps: List[str]
    effort_level: str
    effort_score: int
    effort_summary: str
    suggestion_source: str
    proposed_file_changes: List["FileChangePreview"]


class IssuePrDraftResponse(BaseModel):
    repo: str
    issue_number: int
    issue_title: str
    pr_title: str
    pr_body: str
    changed_files: List[str]
    effort_level: str
    effort_score: int
    effort_summary: str
    suggestion_source: str
    proposed_file_changes: List["FileChangePreview"]


class FileChangePreview(BaseModel):
    file_path: str
    change_type: str
    estimated_lines_changed: int
    impact: str
    pseudo_diff: str
