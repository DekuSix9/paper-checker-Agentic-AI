import os
import json
import time
import functools
from datetime import datetime
from typing import Callable, Any, Dict, List, Optional

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "execution.json")

# Model pricing per 1k tokens (approximate standard pricing)
MODEL_PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    "default": {"input": 0.002, "output": 0.008}
}


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


class StructuredLogger:
    """Structured JSON Logger for multi-agent execution tracing."""

    @staticmethod
    def log(agent_name: str, action: str, details: Dict[str, Any], level: str = "INFO") -> Dict[str, Any]:
        ensure_log_dir()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "level": level,
            "action": action,
            "details": details
        }
        
        try:
            with open(LOG_FILE, "r+", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                except Exception:
                    logs = []
                logs.append(entry)
                f.seek(0)
                json.dump(logs, f, indent=2)
                f.truncate()
        except Exception as e:
            print(f"[StructuredLogger Error] {e}")

        return entry

    @staticmethod
    def get_logs(level_filter: Optional[str] = None, agent_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        ensure_log_dir()
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
            
            if level_filter and level_filter != "ALL":
                logs = [l for l in logs if l.get("level") == level_filter]
            if agent_filter and agent_filter != "ALL":
                logs = [l for l in logs if l.get("agent") == agent_filter]
            return logs
        except Exception:
            return []


def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str = "gpt-4o-mini") -> float:
    """Calculate USD cost from token counts."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
    cost = (prompt_tokens / 1000.0 * pricing["input"]) + (completion_tokens / 1000.0 * pricing["output"])
    return round(cost, 6)


def retry_with_backoff(retries: int = 3, backoff_factor: float = 1.5, agent_name: str = "agent"):
    """Decorator to retry flaky LLM/tool functions with exponential backoff."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_err = None
            delay = 1.0
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    StructuredLogger.log(
                        agent_name=agent_name,
                        action="retry_attempt",
                        details={"attempt": attempt, "error": str(e)},
                        level="WARNING"
                    )
                    if attempt < retries:
                        time.sleep(delay)
                        delay *= backoff_factor
            
            StructuredLogger.log(
                agent_name=agent_name,
                action="execution_failed",
                details={"error": str(last_err)},
                level="ERROR"
            )
            raise last_err
        return wrapper
    return decorator
