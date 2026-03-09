from typing import Dict, List

SESSION_MEMORY: Dict[str, List[str]] = {}


def add_message(session_id: str, message: str) -> None:
    SESSION_MEMORY.setdefault(session_id, []).append(message)


def get_messages(session_id: str, limit: int = 5) -> List[str]:
    return SESSION_MEMORY.get(session_id, [])[-limit:]


def clear_messages(session_id: str) -> None:
    if session_id in SESSION_MEMORY:
        del SESSION_MEMORY[session_id]