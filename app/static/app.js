const difficultyEl = document.getElementById("difficulty");
const interestAreaEl = document.getElementById("interestArea");
const limitEl = document.getElementById("limit");
const issueListEl = document.getElementById("issueList");
const outputEl = document.getElementById("output");
const discoverBtn = document.getElementById("discoverBtn");

async function post(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const err = await response.json();
      if (err.detail) {
        message = `${message} - ${err.detail}`;
      }
    } catch (_ignored) {}
    throw new Error(message);
  }

  return response.json();
}

function renderIssues(issues) {
  issueListEl.innerHTML = "";
  if (!issues.length) {
    issueListEl.innerHTML = '<p class="muted">No matching open issues found for this level right now.</p>';
    return;
  }

  issues.forEach((issue) => {
    const button = document.createElement("button");
    button.className = "issue-item";
    button.type = "button";
    button.innerHTML = `
      <strong>${issue.repo} #${issue.issue_number}</strong>
      <span>${issue.title}</span>
      <small>${issue.labels.join(", ") || "no labels"} | comments: ${issue.comments}</small>
    `;
    button.addEventListener("click", () => showIssuePlan(issue.repo, issue.issue_number));
    issueListEl.appendChild(button);
  });
}

async function discoverIssues() {
  discoverBtn.disabled = true;
  outputEl.innerHTML = '<p class="muted">Fetching open issues...</p>';
  issueListEl.innerHTML = '<p class="muted">Loading...</p>';

  try {
    const level = difficultyEl.value;
    const data = await post("/api/discover-issues", {
      topic: interestAreaEl.value.trim() || "AI",
      difficulty: level,
      limit: Number.parseInt(limitEl.value, 10) || 12,
    });
    renderIssues(data.issues);
    outputEl.innerHTML = '<p class="muted">Issues loaded. Click one issue to view plan details.</p>';
  } catch (error) {
    issueListEl.innerHTML = '<p class="muted">Failed to load issues.</p>';
    outputEl.innerHTML = `<p class="muted">Error: ${error.message}</p>`;
  } finally {
    discoverBtn.disabled = false;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderList(items) {
  if (!items || !items.length) {
    return '<p class="muted">No items.</p>';
  }
  return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function renderEffort(level, score, summary) {
  const normalized = (level || "medium").toLowerCase();
  return `
    <div class="effort-row">
      <span class="effort-badge effort-${normalized}">${escapeHtml(normalized.toUpperCase())}</span>
      <span class="effort-score">Score: ${Number(score) || 0}/10</span>
      <span class="effort-summary">${escapeHtml(summary || "")}</span>
    </div>
  `;
}

function renderSource(source) {
  const label = source === "generative_model" ? "Generative model" : "Heuristic fallback";
  const cls = source === "generative_model" ? "source-ai" : "source-heuristic";
  return `<span class="source-badge ${cls}">${escapeHtml(label)}</span>`;
}

function renderFileChanges(changes) {
  if (!changes || !changes.length) {
    return '<p class="muted">No file-level change preview available.</p>';
  }
  return changes
    .map(
      (change) => `
      <article class="file-change">
        <div class="file-change-head">
          <strong>${escapeHtml(change.file_path)}</strong>
          <span class="chip">${escapeHtml(change.change_type)}</span>
          <span class="chip">${Number(change.estimated_lines_changed) || 0} lines</span>
        </div>
        <p class="impact">${escapeHtml(change.impact || "")}</p>
        <pre class="diff">${escapeHtml(change.pseudo_diff || "")}</pre>
      </article>
    `
    )
    .join("");
}

function renderIssuePlan(plan, prDraft) {
  outputEl.innerHTML = `
    <section class="plan-block">
      <h3>${escapeHtml(plan.repo)} #${plan.issue_number}: ${escapeHtml(plan.title)}</h3>
      <p><a href="${escapeHtml(plan.html_url)}" target="_blank" rel="noreferrer">Open GitHub issue</a></p>
      ${renderSource(plan.suggestion_source)}
      ${renderEffort(plan.effort_level, plan.effort_score, plan.effort_summary)}
      <h4>Likely Changes</h4>
      ${renderList(plan.likely_changes)}
      <h4>Suggested First Steps</h4>
      ${renderList(plan.suggested_first_steps)}
      <h4>Proposed File-Level Diffs</h4>
      ${renderFileChanges(plan.proposed_file_changes)}
    </section>
    <section class="plan-block">
      <h3>PR Draft</h3>
      <p><strong>Title:</strong> ${escapeHtml(prDraft.pr_title)}</p>
      ${renderSource(prDraft.suggestion_source)}
      ${renderEffort(prDraft.effort_level, prDraft.effort_score, prDraft.effort_summary)}
      <h4>Likely Changed Files</h4>
      ${renderList(prDraft.changed_files)}
      <h4>PR Body Preview</h4>
      <pre class="diff">${escapeHtml(prDraft.pr_body)}</pre>
    </section>
  `;
}

async function showIssuePlan(repo, issueNumber) {
  outputEl.innerHTML = `<p class="muted">Analyzing ${repo}#${issueNumber}...</p>`;
  try {
    const [plan, prDraft] = await Promise.all([
      post("/api/plan-issue", { repo, issue_number: issueNumber }),
      post("/api/create-pr-from-issue", { repo, issue_number: issueNumber }),
    ]);
    renderIssuePlan(plan, prDraft);
  } catch (error) {
    outputEl.innerHTML = `<p class="muted">Error: ${error.message}</p>`;
  }
}

discoverBtn.addEventListener("click", discoverIssues);
