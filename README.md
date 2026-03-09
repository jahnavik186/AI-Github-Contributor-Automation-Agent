# AI GitHub Contributor Automation Agent

[![Docker Pulls](https://img.shields.io/docker/pulls/jahnavik186/ai-github-contributor-automation-agent?style=for-the-badge)](https://hub.docker.com/r/jahnavik186/ai-github-contributor-automation-agent)
[![Docker Image](https://img.shields.io/badge/docker-jahnavik186%2Fai--github--contributor--automation--agent-blue?style=for-the-badge&logo=docker)](https://hub.docker.com/r/jahnavik186/ai-github-contributor-automation-agent)
[![GitHub Stars](https://img.shields.io/github/stars/jahnavik186/AI-Github-Contributor-Automation-Agent?style=for-the-badge)](https://github.com/jahnavik186/AI-Github-Contributor-Automation-Agent)
[![GitHub Forks](https://img.shields.io/github/forks/jahnavik186/AI-Github-Contributor-Automation-Agent?style=for-the-badge)](https://github.com/jahnavik186/AI-Github-Contributor-Automation-Agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](https://opensource.org/licenses/MIT)

Turn real GitHub issues into a clear execution plan in seconds.

This project helps contributors and maintainers discover AI-related open issues, estimate effort, and generate PR-ready implementation guidance with a fallback-safe workflow (heuristics first, optional generative layer).

## Why People Use It

- Find active, relevant GitHub issues quickly
- Filter by practical difficulty (`good_first`, `intermediate`, `hard`)
- Generate concrete next steps before opening an editor
- Draft PR summaries and likely file changes faster

## Quick Start (Docker Hub)

```bash
docker pull jahnavik186/ai-github-contributor-automation-agent:latest
docker run --rm -p 8000:8000 jahnavik186/ai-github-contributor-automation-agent:latest
```

Open:

- UI: http://localhost:8000/
- Health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Build Locally

```bash
docker build -t ai-github-contributor-automation-agent .
docker run --rm -p 8000:8000 ai-github-contributor-automation-agent
```

## Core Capabilities

- Discover issues from real GitHub repositories
- Match issue complexity by difficulty tier
- Suggest code/doc/test changes for a selected issue
- Generate implementation-first PR draft content

## Real GitHub Ingestion

Optional for higher API rate limits:

```bash
# Windows PowerShell
$env:GITHUB_TOKEN="your_token_here"
```

## Optional Generative Planning Layer

For beginner-friendly issues (for example labels like `good first issue`, `beginner`, `help wanted`), the planner can call a generative model to produce:

- likely code/doc/test changes
- beginner-friendly first steps
- likely touched files
- effort estimate (`easy`/`medium`/`high`)

If no model key is configured, or model call fails, the app falls back to deterministic heuristics.

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your_openai_api_key"
$env:OPENAI_MODEL="gpt-4.1-mini"  # optional override
```

## API Examples

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

```bash
curl -X POST http://localhost:8000/api/demo \
  -H "content-type: application/json" \
  -d '{"repo":"open-source-labs/api-docs-toolkit","branch":"main"}'
```

## Notes

This project is designed for local showcase and portfolio use. It ingests real issue metadata from GitHub, but does not auto-merge or directly modify external repositories.
