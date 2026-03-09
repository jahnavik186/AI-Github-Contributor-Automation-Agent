# Autonomous Open Source Contributor Agent

An AI agent project with backend + UI that ingests real GitHub issues for AI topics and helps you choose what to work on next.

## Capabilities

- Discovers open issues from popular AI open-source repositories
- Filters by difficulty: `good_first`, `intermediate`, `hard`
- Suggests likely code/documentation/test changes needed for a selected issue
- Supports demo pipeline endpoints for analysis, fix ideas, and PR draft generation

## Local Demo with Docker

Build:

```bash
docker build -t github-contributor-agent .
```

Run:

```bash
docker run --rm -p 8000:8000 github-contributor-agent
```

Open:

- UI: http://localhost:8000/
- Health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Real GitHub Ingestion

The app now calls GitHub API directly to discover issues.

Optional for higher API rate limits:

```bash
# Windows PowerShell
$env:GITHUB_TOKEN="your_token_here"
```

## Generative Suggestions for Beginner Issues

For beginner-friendly issues (for example labels like `good first issue`, `beginner`, or low-complexity `help wanted`),
the planner can call a generative model to produce:

- likely code/doc/test changes
- beginner-friendly first steps
- likely touched files
- effort estimate (`easy`/`medium`/`high`)

If no model key is configured or model call fails, the app automatically falls back to deterministic heuristics.

Set model credentials:

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your_openai_api_key"
$env:OPENAI_MODEL="gpt-4.1-mini"  # optional override
```

Use the UI:

1. Enter any Interest Area (for example: `ai agents`, `computer vision`, `robotics`, `fintech`, `healthcare ai`)
2. Select Difficulty (`good_first`, `intermediate`, `hard`)
3. Click `Find Open Issues`
4. Pick issue (repo + issue number) and click `Suggest Changes Needed`

Use API directly:

```bash
curl -X POST http://localhost:8000/api/discover-issues \
  -H "content-type: application/json" \
  -d '{"topic":"ai agents","difficulty":"good_first","limit":10}'
```

```bash
curl -X POST http://localhost:8000/api/plan-issue \
  -H "content-type: application/json" \
  -d '{"repo":"huggingface/diffusers","issue_number":10076}'
```

## API Example

```bash
curl -X POST http://localhost:8000/api/demo \
  -H "content-type: application/json" \
  -d '{"repo":"open-source-labs/api-docs-toolkit","branch":"main"}'
```

## Why this has global appeal

- Developers can accelerate routine maintenance
- Open-source maintainers can reduce issue backlog
- New contributors can get PR-ready scaffolding quickly

## Notes

This app is designed for local showcase and portfolio use. It ingests real issue metadata from GitHub, but it does not auto-merge or directly modify external repositories.
