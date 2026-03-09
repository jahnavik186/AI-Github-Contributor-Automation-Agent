import re
from typing import Dict, List

DOCUMENTS_BY_USE_CASE: Dict[str, List[str]] = {
    "customer_support": [
        "Billing issues should include charge amount, date, and account identifier.",
        "Duplicate charges may require manual review and escalation.",
        "Refund requests typically require transaction verification.",
        "Password reset workflows should confirm the account email before proceeding.",
        "High-friction customer interactions may need human escalation.",
    ],
    "healthcare_copilot": [
        "Clinical support should avoid diagnosis and instead organize information and next steps.",
        "Medication questions should capture medication name, dose, and timing.",
        "Symptom-related workflows should identify urgency, timing, and severity.",
        "Care guidance workflows should structure the issue and recommended next step.",
        "Follow-up summaries should capture the main concern and action items.",
    ],
    "knowledge_assistant": [
        "Knowledge assistants should retrieve the most relevant internal policy or document snippet.",
        "Enterprise assistants should summarize documentation clearly and concisely.",
        "Process guidance should return next steps and source references when possible.",
    ],
    "research_assistant": [
        "Research assistants should summarize relevant evidence before presenting conclusions.",
        "Methodology support should highlight study design, assumptions, and limitations.",
        "Technical summaries should balance clarity, depth, and traceability.",
    ],
    "sales_assistant": [
        "Lead qualification workflows should capture company, need, urgency, and fit.",
        "Pricing workflows should clarify product scope and pricing context.",
        "Sales assistants should summarize next best action for follow-up.",
    ],
    "hr_assistant": [
        "HR policy workflows should retrieve the most relevant handbook or policy guidance.",
        "Benefits questions should identify plan type, eligibility, and timeline.",
        "Onboarding requests should be routed based on employee stage and required tasks.",
    ],
    "it_helpdesk": [
        "Password reset workflows should verify identity before proceeding.",
        "Device issues should capture device type, symptoms, and urgency.",
        "Access requests should identify system, role, and business justification.",
    ],
    "operations_assistant": [
        "Operations assistants should identify process bottlenecks and escalation paths.",
        "Workflow exceptions should include current state, owner, and next step.",
        "Task routing workflows should clarify team, priority, and dependency.",
    ],
}


def retrieve_context(query: str, use_case: str, top_k: int = 3) -> List[str]:
    documents = DOCUMENTS_BY_USE_CASE.get(use_case, DOCUMENTS_BY_USE_CASE["customer_support"])
    query_terms = set(re.findall(r"\w+", query.lower()))
    scored_docs = []

    for doc in documents:
        doc_terms = set(re.findall(r"\w+", doc.lower()))
        score = len(query_terms.intersection(doc_terms))
        scored_docs.append((score, doc))

    scored_docs.sort(reverse=True, key=lambda item: item[0])
    results = [doc for score, doc in scored_docs[:top_k] if score > 0]

    return results or documents[:1]