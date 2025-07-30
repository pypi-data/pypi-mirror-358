"""
StateCall - A lightweight library to add memory to stateless LLM APIs
"""

from .memory import (
    append_to_history,
    load_context,
    get_session_history,
    clear_session,
    list_sessions,
    get_session_info,
    export_conversation,
    import_conversation,
    export_all_conversations,
    get_conversation_stats,
)
from .groq_client import GroqClient

# Semantic search functions (optional dependency)
try:
    from .semantic_search import (
        search_conversations,
        find_similar_conversations,
        search_in_session,
        get_conversation_themes,
    )
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    SEMANTIC_SEARCH_AVAILABLE = False

__version__ = "0.2.1"
__author__ = "Kavish Soningra"

__all__ = [
    "append_to_history",
    "load_context", 
    "get_session_history",
    "clear_session",
    "list_sessions",
    "get_session_info",
    "export_conversation",
    "import_conversation",
    "export_all_conversations",
    "get_conversation_stats",
    "GroqClient",
]

# Add semantic search functions to __all__ if available
if SEMANTIC_SEARCH_AVAILABLE:
    __all__.extend([
        "search_conversations",
        "find_similar_conversations", 
        "search_in_session",
        "get_conversation_themes",
        "SEMANTIC_SEARCH_AVAILABLE",
    ]) 