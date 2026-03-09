from typing import Dict, List

USE_CASES = {
    "customer_support": {
        "category": "service",
        "description": "Inbound support automation for billing, refunds, access issues, scheduling, and escalation workflows.",
        "supported_intents": [
            "billing_issue",
            "refund_request",
            "access_issue",
            "scheduling",
            "general_support",
        ],
        "tool_candidates": [
            "ticketing_api",
            "billing_system",
            "crm_update",
            "knowledge_base_search",
        ],
    },
    "healthcare_copilot": {
        "category": "healthcare",
        "description": "Clinical and patient support workflow for care guidance, symptom triage support, medication questions, and follow-up summaries.",
        "supported_intents": [
            "symptom_question",
            "medication_question",
            "appointment_followup",
            "care_guidance",
            "general_support",
        ],
        "tool_candidates": [
            "clinical_guideline_retriever",
            "ehr_summary_service",
            "care_navigation_api",
            "patient_message_router",
        ],
    },
    "knowledge_assistant": {
        "category": "enterprise",
        "description": "Enterprise knowledge assistant for documents, policies, SOPs, process guidance, and internal Q&A.",
        "supported_intents": [
            "policy_lookup",
            "process_lookup",
            "document_lookup",
            "general_support",
        ],
        "tool_candidates": [
            "document_search",
            "wiki_lookup",
            "enterprise_search_api",
        ],
    },
    "research_assistant": {
        "category": "research",
        "description": "Research workflow for literature guidance, methodology assistance, evidence retrieval, and technical summaries.",
        "supported_intents": [
            "literature_lookup",
            "methodology_question",
            "technical_summary",
            "general_support",
        ],
        "tool_candidates": [
            "paper_search",
            "citation_lookup",
            "document_retriever",
        ],
    },
    "sales_assistant": {
        "category": "business",
        "description": "Sales support assistant for lead qualification, objection handling, product information, and follow-up recommendations.",
        "supported_intents": [
            "lead_qualification",
            "pricing_question",
            "product_question",
            "followup_request",
            "general_support",
        ],
        "tool_candidates": [
            "crm_lookup",
            "pricing_catalog_api",
            "product_knowledge_search",
            "sales_notes_updater",
        ],
    },
    "hr_assistant": {
        "category": "people_ops",
        "description": "HR assistant for policy questions, leave guidance, onboarding support, and employee process navigation.",
        "supported_intents": [
            "leave_policy_question",
            "benefits_question",
            "onboarding_question",
            "policy_lookup",
            "general_support",
        ],
        "tool_candidates": [
            "hr_policy_search",
            "employee_handbook_lookup",
            "hr_ticketing_api",
        ],
    },
    "it_helpdesk": {
        "category": "it",
        "description": "IT helpdesk assistant for password reset, access requests, device issues, and troubleshooting workflows.",
        "supported_intents": [
            "password_reset",
            "access_request",
            "device_issue",
            "troubleshooting_request",
            "general_support",
        ],
        "tool_candidates": [
            "identity_access_api",
            "device_inventory_lookup",
            "it_ticketing_system",
            "kb_search",
        ],
    },
    "operations_assistant": {
        "category": "operations",
        "description": "Operations workflow assistant for process exceptions, task routing, issue escalation, and workflow coordination.",
        "supported_intents": [
            "workflow_exception",
            "process_status_question",
            "task_routing",
            "escalation_request",
            "general_support",
        ],
        "tool_candidates": [
            "workflow_engine",
            "task_queue_api",
            "ops_dashboard_lookup",
            "incident_tracker",
        ],
    },
}

DEMO_SCENARIOS: List[Dict[str, str]] = [
    {
        "title": "SaaS Billing Escalation",
        "use_case": "customer_support",
        "message": "I was charged twice for my annual subscription and this is urgent.",
        "outcome": "Routes to billing workflow with escalation readiness and refund verification context.",
    },
    {
        "title": "Care Navigation Follow-up",
        "use_case": "healthcare_copilot",
        "message": "I have a fever after discharge and I am not sure what to do next.",
        "outcome": "Flags guidance signal and suggests structured follow-up communication.",
    },
    {
        "title": "Enterprise Policy Copilot",
        "use_case": "knowledge_assistant",
        "message": "Where is the policy for contractor system access approvals?",
        "outcome": "Detects policy lookup and surfaces concise document guidance.",
    },
    {
        "title": "IT Access Workflow",
        "use_case": "it_helpdesk",
        "message": "I need access to the finance dashboard before tomorrow morning.",
        "outcome": "Detects access request, urgency, and suggests identity workflow actions.",
    },
]

