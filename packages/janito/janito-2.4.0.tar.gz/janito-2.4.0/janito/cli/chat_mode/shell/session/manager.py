import os
import json
from datetime import datetime

# --- Session ID generation ---
_current_session_id = None


def generate_session_id():
    # Use seconds since start of year, encode as base36 for shortness
    now = datetime.now()
    start_of_year = datetime(now.year, 1, 1)
    seconds = int((now - start_of_year).total_seconds())
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    n = seconds
    while n:
        n, r = divmod(n, 36)
        out = chars[r] + out
    return out or "0"


def reset_session_id():
    global _current_session_id
    _current_session_id = None


def get_session_id():
    global _current_session_id
    if _current_session_id is None:
        _current_session_id = generate_session_id()
    return _current_session_id


def set_role(role):
    """Set the current role."""
    # No longer needed: from janito.cli.runtime_config import RuntimeConfig
    rc = RuntimeConfig()
    rc.role = role
    rc.save()


def load_last_summary(path=".janito/last_conversation.json"):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def load_last_conversation(path=".janito/last_conversation.json"):
    if not os.path.exists(path):
        return [], [], None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    messages = data.get("messages", [])
    prompts = data.get("prompts", [])
    usage = data.get("last_usage_info")
    return messages, prompts, usage


def load_conversation_by_session_id(session_id):
    path = os.path.join(".janito", "chat_history", f"{session_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Session file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    messages = data.get("messages", [])
    prompts = data.get("prompts", [])
    usage = data.get("last_usage_info")
    return messages, prompts, usage


def save_conversation(messages, prompts, usage_info=None, path=None):
    # Do not save if only one message and it is a system message (noop session)
    if (
        isinstance(messages, list)
        and len(messages) == 1
        and messages[0].get("role") == "system"
    ):
        return

    if path is None:
        session_id = get_session_id()
        path = os.path.join(".janito", "chat_history", f"{session_id}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {"messages": messages, "prompts": prompts, "last_usage_info": usage_info}

    def usage_serializer(obj):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict"):
            return obj.__dict__
        return str(obj)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=usage_serializer)
        f.write("\n")


def last_conversation_exists(path=".janito/last_conversation.json"):
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        messages = data.get("messages", [])
        return bool(messages)
    except Exception:
        return False
