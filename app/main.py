from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.agent import (
    create_pr_draft_from_issue,
    detect_issues,
    discover_issues,
    generate_pr,
    plan_issue_changes,
    propose_fixes,
    run_end_to_end,
    update_docs,
)
from app.schemas import AnalyzeRequest, DiscoverRequest, IssuePlanRequest

app = FastAPI(
    title="Autonomous Open Source Contributor Agent",
    version="1.0.0",
    description="Detect issues, propose fixes, generate PR drafts, and update docs for open-source repositories.",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def home() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "github-contributor-agent"}


@app.post("/api/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    return detect_issues(repo=payload.repo, branch=payload.branch).model_dump()


@app.post("/api/propose-fixes")
def propose(payload: AnalyzeRequest) -> dict:
    analysis = detect_issues(repo=payload.repo, branch=payload.branch)
    fixes = propose_fixes(analysis.issues)
    return {"repo": payload.repo, "fixes": [fix.model_dump() for fix in fixes]}


@app.post("/api/generate-pr")
def generate(payload: AnalyzeRequest) -> dict:
    analysis = detect_issues(repo=payload.repo, branch=payload.branch)
    fixes = propose_fixes(analysis.issues)
    pr = generate_pr(repo=payload.repo, fixes=fixes, issues=analysis.issues)
    return pr.model_dump()


@app.post("/api/update-docs")
def docs(payload: AnalyzeRequest) -> dict:
    analysis = detect_issues(repo=payload.repo, branch=payload.branch)
    doc_change = update_docs(repo=payload.repo, issues=analysis.issues)
    return doc_change.model_dump()


@app.post("/api/demo")
def demo(payload: AnalyzeRequest) -> dict:
    return run_end_to_end(repo=payload.repo, branch=payload.branch).model_dump()


@app.post("/api/discover-issues")
def discover(payload: DiscoverRequest) -> dict:
    try:
        return discover_issues(
            topic=payload.topic,
            difficulty=payload.difficulty,
            limit=payload.limit,
        ).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/plan-issue")
def plan_issue(payload: IssuePlanRequest) -> dict:
    try:
        return plan_issue_changes(repo=payload.repo, issue_number=payload.issue_number).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/create-pr-from-issue")
def create_pr_from_issue(payload: IssuePlanRequest) -> dict:
    try:
        return create_pr_draft_from_issue(repo=payload.repo, issue_number=payload.issue_number).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
