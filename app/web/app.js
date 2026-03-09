const useCaseEl = document.getElementById("useCase");
const sessionIdEl = document.getElementById("sessionId");
const userIdEl = document.getElementById("userId");
const messageEl = document.getElementById("message");
const outputEl = document.getElementById("output");
const runBtn = document.getElementById("runBtn");
const scenarioBtn = document.getElementById("scenarioBtn");

let scenarios = [];

async function init() {
  const useCaseData = await fetchJSON("/use-cases");
  Object.entries(useCaseData.use_cases).forEach(([key, value]) => {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = `${key} - ${value.category}`;
    useCaseEl.append(option);
  });

  const scenarioData = await fetchJSON("/demo-scenarios");
  scenarios = scenarioData.scenarios;
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

runBtn.addEventListener("click", async () => {
  runBtn.disabled = true;
  outputEl.textContent = "Running workflow...";

  const body = {
    user_id: userIdEl.value,
    session_id: sessionIdEl.value,
    message: messageEl.value,
    use_case: useCaseEl.value,
    use_retrieval: true,
    metadata: {
      channel: "web-ui",
    },
  };

  try {
    const data = await fetchJSON("/agent/run", {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(body),
    });
    outputEl.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    outputEl.textContent = `Error: ${error.message}`;
  } finally {
    runBtn.disabled = false;
  }
});

scenarioBtn.addEventListener("click", () => {
  if (!scenarios.length) {
    return;
  }
  const randomScenario = scenarios[Math.floor(Math.random() * scenarios.length)];
  useCaseEl.value = randomScenario.use_case;
  messageEl.value = randomScenario.message;
  outputEl.textContent = `Loaded scenario: ${randomScenario.title}`;
});

init().catch((error) => {
  outputEl.textContent = `Initialization error: ${error.message}`;
});

