from typing import List


def detect_intent(message: str, use_case: str) -> str:
    text = message.lower()

    if use_case == "customer_support":
        if any(word in text for word in ["billing", "charged", "charge", "payment", "invoice"]):
            return "billing_issue"
        if any(word in text for word in ["refund", "money back", "return"]):
            return "refund_request"
        if any(word in text for word in ["password", "login", "sign in", "signin"]):
            return "access_issue"
        if any(word in text for word in ["appointment", "schedule", "reschedule", "booking"]):
            return "scheduling"
        return "general_support"

    if use_case == "healthcare_copilot":
        if any(word in text for word in ["symptom", "pain", "fever", "cough", "dizzy"]):
            return "symptom_question"
        if any(word in text for word in ["medication", "medicine", "dose", "tablet", "prescription"]):
            return "medication_question"
        if any(word in text for word in ["follow up", "follow-up", "after visit", "next step"]):
            return "appointment_followup"
        if any(word in text for word in ["care", "guidance", "what should i do", "navigate"]):
            return "care_guidance"
        return "general_support"

    if use_case == "knowledge_assistant":
        if any(word in text for word in ["policy", "policies"]):
            return "policy_lookup"
        if any(word in text for word in ["process", "procedure", "workflow"]):
            return "process_lookup"
        if any(word in text for word in ["document", "wiki", "manual", "guide"]):
            return "document_lookup"
        return "general_support"

    if use_case == "research_assistant":
        if any(word in text for word in ["paper", "literature", "study", "research"]):
            return "literature_lookup"
        if any(word in text for word in ["method", "methodology", "approach", "design"]):
            return "methodology_question"
        if any(word in text for word in ["summary", "summarize", "technical overview"]):
            return "technical_summary"
        return "general_support"

    if use_case == "sales_assistant":
        if any(word in text for word in ["lead", "prospect", "qualification"]):
            return "lead_qualification"
        if any(word in text for word in ["price", "pricing", "cost", "quote"]):
            return "pricing_question"
        if any(word in text for word in ["product", "feature", "capability"]):
            return "product_question"
        if any(word in text for word in ["follow up", "follow-up", "next call", "next meeting"]):
            return "followup_request"
        return "general_support"

    if use_case == "hr_assistant":
        if any(word in text for word in ["leave", "pto", "vacation", "time off"]):
            return "leave_policy_question"
        if any(word in text for word in ["benefits", "insurance", "coverage"]):
            return "benefits_question"
        if any(word in text for word in ["onboarding", "new hire", "joining"]):
            return "onboarding_question"
        if any(word in text for word in ["policy", "employee handbook"]):
            return "policy_lookup"
        return "general_support"

    if use_case == "it_helpdesk":
        if any(word in text for word in ["password reset", "reset password", "forgot password"]):
            return "password_reset"
        if any(word in text for word in ["access", "permission", "permission request"]):
            return "access_request"
        if any(word in text for word in ["laptop", "device", "computer", "screen", "hardware"]):
            return "device_issue"
        if any(word in text for word in ["error", "troubleshoot", "issue", "bug"]):
            return "troubleshooting_request"
        return "general_support"

    if use_case == "operations_assistant":
        if any(word in text for word in ["exception", "failed process", "stuck"]):
            return "workflow_exception"
        if any(word in text for word in ["status", "progress", "where is"]):
            return "process_status_question"
        if any(word in text for word in ["route", "assign", "handoff"]):
            return "task_routing"
        if any(word in text for word in ["escalate", "escalation", "urgent"]):
            return "escalation_request"
        return "general_support"

    return "general_support"


def detect_conversation_signal(message: str) -> str:
    text = message.lower()

    if any(word in text for word in ["urgent", "asap", "immediately", "critical", "today"]):
        return "urgent"

    if any(word in text for word in ["angry", "upset", "frustrated", "terrible", "unacceptable"]):
        return "high_friction"

    if any(word in text for word in ["confused", "unclear", "not sure", "don't understand"]):
        return "needs_guidance"

    if any(word in text for word in ["thanks", "thank you", "great", "awesome", "helpful"]):
        return "positive"

    return "normal"


def recommend_action(intent: str, signal: str, use_case: str) -> str:
    if signal == "urgent":
        return f"prioritize_{intent}"

    if signal == "high_friction":
        return f"handle_{intent}_with_escalation_readiness"

    if use_case == "customer_support":
        return f"resolve_{intent}_workflow"

    if use_case == "healthcare_copilot":
        return f"guide_{intent}_workflow"

    if use_case == "knowledge_assistant":
        return f"retrieve_and_summarize_{intent}"

    if use_case == "research_assistant":
        return f"analyze_and_support_{intent}"

    if use_case == "sales_assistant":
        return f"advance_{intent}_workflow"

    if use_case == "hr_assistant":
        return f"support_{intent}_workflow"

    if use_case == "it_helpdesk":
        return f"triage_{intent}_workflow"

    if use_case == "operations_assistant":
        return f"coordinate_{intent}_workflow"

    return "request_more_information"


def generate_answer(
    message: str,
    intent: str,
    signal: str,
    context: List[str],
    action: str,
    use_case: str,
) -> str:
    prefix = ""
    if signal == "high_friction":
        prefix = "I'm sorry you're dealing with this. "
    elif signal == "urgent":
        prefix = "I understand this is time-sensitive. "
    elif signal == "needs_guidance":
        prefix = "I can break this down step by step. "

    guidance = context[0] if context else ""

    next_step_map = {
        "customer_support": "Capture account details, verify the transaction, and create a priority support ticket.",
        "healthcare_copilot": "Document symptoms with timing and severity and route to the correct care pathway.",
        "knowledge_assistant": "Return the highest-confidence policy snippet with source linkage.",
        "research_assistant": "Summarize evidence quality and call out assumptions before recommendations.",
        "sales_assistant": "Qualify urgency, fit, and buying stage before proposing a follow-up action.",
        "hr_assistant": "Confirm eligibility criteria and return policy-backed next steps.",
        "it_helpdesk": "Validate identity, classify severity, and trigger access/device workflow.",
        "operations_assistant": "Identify owner, blocker, and escalation path with SLA context.",
    }

    scope_map = {
        "customer_support": "billing, refunds, access, and scheduling",
        "healthcare_copilot": "symptom intake, medication questions, and care guidance",
        "knowledge_assistant": "policies, SOPs, and internal docs",
        "research_assistant": "literature retrieval, methods, and technical summaries",
        "sales_assistant": "lead qualification, pricing, and product guidance",
        "hr_assistant": "policy support, onboarding, leave, and benefits",
        "it_helpdesk": "password resets, access, devices, and troubleshooting",
        "operations_assistant": "exceptions, status tracking, routing, and escalation",
    }

    scope = scope_map.get(use_case, "general workflow orchestration")
    next_step = next_step_map.get(use_case, "Ask targeted clarifying questions and route the task.")

    return (
        f"{prefix}Detected intent: '{intent}'. This runtime supports {scope}. "
        f"Recommended action: '{action}'."
        f" Context hint: {guidance}"
        f" Next best step: {next_step}"
    )

