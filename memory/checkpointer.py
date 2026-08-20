import os

DB_PATH = os.path.join(os.path.dirname(__file__), "checkpoints.db")


def get_sqlite_checkpointer():
    """Return LangGraph checkpointer for state persistence."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        import sqlite3
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        return SqliteSaver(conn)
    except Exception:
        try:
            from langgraph.checkpoint.memory import MemorySaver
            return MemorySaver()
        except Exception:
            return None
