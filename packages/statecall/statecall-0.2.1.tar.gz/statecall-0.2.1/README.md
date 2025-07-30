# StateCall

A simple Python library that adds memory to AI chatbots. StateCall remembers your conversations so AI can reference previous messages.

What it does

Most AI chatbots forget everything when you start a new conversation. StateCall saves your chat history so the AI can remember what you talked about before.

Features

- Works with any AI service (OpenAI, Groq, Claude, etc.)
- Built-in Groq support
- Saves conversations locally on your computer
- No database or internet connection needed
- Simple to use
- Export/import conversations (JSON/CSV)
- Conversation statistics and analytics
- NEW: Semantic search across conversations (find by meaning, not just keywords)

Installation

```bash
pip install statecall
```

Quick start

Basic usage

```python
from statecall.memory import append_to_history, load_context
import openai

openai.api_key = "your-openai-api-key"
session_id = "my-chat"

# Save a message
append_to_history(session_id, "user", "Tell me a joke.")
history = load_context(session_id)

# Get AI response
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=history
)

assistant_msg = response["choices"][0]["message"]["content"]
append_to_history(session_id, "assistant", assistant_msg)

print("AI:", assistant_msg)
```

Using Groq

```python
from statecall.groq_client import GroqClient
from statecall.memory import append_to_history, get_session_history

session_id = "groq-chat"
client = GroqClient(api_key="your-groq-api-key")

append_to_history(session_id, "user", "Who won the World Cup in 2022?")
history = get_session_history(session_id)
response = client.chat(history)

append_to_history(session_id, "assistant", response)
print("AI:", response)
```

Export and Import

Export a conversation to JSON or CSV:

```python
from statecall.memory import export_conversation, import_conversation

# Export to JSON
export_conversation("my-chat", "conversation.json", "json")

# Export to CSV
export_conversation("my-chat", "conversation.csv", "csv")

# Import a conversation
imported_session = import_conversation("conversation.json")
```

Get conversation statistics:

```python
from statecall.memory import get_conversation_stats

stats = get_conversation_stats()
print(f"Total sessions: {stats['total_sessions']}")
print(f"Total messages: {stats['total_messages']}")
```

## Semantic Search (NEW!)

Find conversations by meaning, not just keywords. Requires `sentence-transformers`:

```bash
pip install sentence-transformers
```

Search across all conversations:

```python
from statecall import search_conversations

# Find conversations about programming
results = search_conversations("Python programming and coding")

for result in results:
    print(f"Found in {result['session_id']}: {result['content']}")
    print(f"Similarity: {result['similarity']:.3f}")
```

Find similar conversations:

```python
from statecall import find_similar_conversations

# Find conversations similar to a specific session
similar = find_similar_conversations("my-coding-session", threshold=0.7)

for session in similar:
    print(f"Similar session: {session['session_id']} ({session['similarity']:.3f})")
```

Search within a session:

```python
from statecall import search_in_session

# Search for specific topics within a conversation
results = search_in_session("my-session", "machine learning algorithms")
```

Extract conversation themes:

```python
from statecall import get_conversation_themes

# Get main themes discussed in a conversation
themes = get_conversation_themes("my-session", num_themes=3)

for theme in themes:
    print(f"Theme {theme['theme_id']}: {len(theme['representative_messages'])} messages")
```

How it works

StateCall saves your conversations in local files on your computer:

- `.statecall_history.json` - stores all your messages
- `.statecall_sessions.json` - tracks your chat sessions
- `.statecall_embeddings.json` - caches semantic embeddings for fast search

This way your conversations are saved between app restarts without needing a database.

Examples

Check the `examples/` folder:

- `custom_llm_openai_example.py` - using OpenAI
- `groq_chat_example.py` - using Groq
- `export_import_example.py` - export/import features
- `semantic_search_example.py` - semantic search capabilities

To run an example:

```bash
python examples/groq_chat_example.py
```

License

MIT License
