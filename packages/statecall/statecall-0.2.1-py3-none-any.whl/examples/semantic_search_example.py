#!/usr/bin/env python3
"""
Example: Semantic Search with StateCall
This example demonstrates the semantic search capabilities for finding
conversations by meaning, not just keywords.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from statecall.memory import append_to_history, clear_session, list_sessions


def create_sample_conversations():
    """Create some sample conversations for testing semantic search."""
    print("Creating sample conversations...\n")
    
    # Clear any existing sessions
    for session in list_sessions():
        clear_session(session)
    
    # Conversation 1: Python Programming
    session1 = "python-coding"
    conversations1 = [
        ("user", "How do I create a list in Python?"),
        ("assistant", "You can create a list in Python using square brackets: my_list = [1, 2, 3, 'hello']"),
        ("user", "What about dictionaries?"),
        ("assistant", "Dictionaries use curly braces: my_dict = {'key': 'value', 'name': 'John'}"),
        ("user", "How do I iterate through a dictionary?"),
        ("assistant", "You can use: for key, value in my_dict.items(): print(key, value)"),
    ]
    
    for role, content in conversations1:
        append_to_history(session1, role, content)
    
    # Conversation 2: Machine Learning
    session2 = "ml-discussion"
    conversations2 = [
        ("user", "What is supervised learning?"),
        ("assistant", "Supervised learning uses labeled training data to learn a mapping from inputs to outputs"),
        ("user", "Can you explain neural networks?"),
        ("assistant", "Neural networks are computing systems inspired by biological neural networks, with interconnected nodes"),
        ("user", "What about deep learning algorithms?"),
        ("assistant", "Deep learning uses multi-layer neural networks to learn complex patterns in data"),
    ]
    
    for role, content in conversations2:
        append_to_history(session2, role, content)
    
    # Conversation 3: Travel Planning
    session3 = "travel-plans"
    conversations3 = [
        ("user", "I want to plan a vacation to Japan"),
        ("assistant", "Great choice! Japan offers amazing culture, food, and sights. When are you planning to visit?"),
        ("user", "Maybe in spring to see cherry blossoms"),
        ("assistant", "Perfect timing! Cherry blossom season is typically March-May. I recommend booking hotels early."),
        ("user", "What cities should I visit?"),
        ("assistant", "Tokyo and Kyoto are must-sees. Tokyo for modern culture, Kyoto for traditional temples and gardens."),
    ]
    
    for role, content in conversations3:
        append_to_history(session3, role, content)
    
    # Conversation 4: Cooking
    session4 = "cooking-tips"
    conversations4 = [
        ("user", "How do I make a good pasta sauce?"),
        ("assistant", "Start with good tomatoes, garlic, olive oil, and fresh basil. Simmer slowly for depth of flavor."),
        ("user", "What about seasoning?"),
        ("assistant", "Salt, pepper, and a pinch of sugar help balance the acidity. Taste as you go!"),
        ("user", "Any tips for cooking the pasta?"),
        ("assistant", "Use plenty of salted water, cook until al dente, and save some pasta water for the sauce."),
    ]
    
    for role, content in conversations4:
        append_to_history(session4, role, content)
    
    print(f"Created {len(list_sessions())} sample conversations")
    return [session1, session2, session3, session4]


def demo_semantic_search():
    """Demonstrate semantic search across conversations."""
    try:
        from statecall.semantic_search import search_conversations
    except ImportError:
        print("Semantic search is not available. Install with: pip install sentence-transformers")
        return
    
    print("\n=== Semantic Search Demo ===")
    
    # Test queries that should find relevant conversations
    test_queries = [
        "programming and coding",
        "artificial intelligence",
        "vacation planning",
        "cooking recipes",
        "data structures",
        "travel to Asia",
    ]
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        results = search_conversations(query, limit=3, min_similarity=0.2)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. Session: {result['session_id']}")
                print(f"     Role: {result['role']}")
                print(f"     Content: {result['content'][:100]}...")
                print(f"     Similarity: {result['similarity']:.3f}")
        else:
            print("  No results found")


def demo_similar_conversations():
    """Demonstrate finding similar conversations."""
    try:
        from statecall.semantic_search import find_similar_conversations
    except ImportError:
        print("Semantic search is not available.")
        return
    
    print("\n=== Similar Conversations Demo ===")
    
    sessions = list_sessions()
    for session_id in sessions:
        print(f"\nFinding conversations similar to '{session_id}':")
        similar = find_similar_conversations(session_id, threshold=0.3, limit=3)
        
        if similar:
            for sim in similar:
                print(f"  - {sim['session_id']} (similarity: {sim['similarity']:.3f})")
        else:
            print("  No similar conversations found")


def demo_search_in_session():
    """Demonstrate searching within a specific session."""
    try:
        from statecall.semantic_search import search_in_session
    except ImportError:
        print("Semantic search is not available.")
        return
    
    print("\n=== Search Within Session Demo ===")
    
    session_id = "python-coding"
    queries = ["data structures", "loops", "syntax"]
    
    for query in queries:
        print(f"\nSearching in '{session_id}' for: '{query}'")
        results = search_in_session(session_id, query, limit=2, min_similarity=0.2)
        
        if results:
            for result in results:
                print(f"  Message {result['message_index']}: {result['content'][:80]}...")
                print(f"  Similarity: {result['similarity']:.3f}")
        else:
            print("  No results found")


def demo_conversation_themes():
    """Demonstrate extracting themes from conversations."""
    try:
        from statecall.semantic_search import get_conversation_themes
    except ImportError:
        print("Semantic search is not available.")
        return
    
    print("\n=== Conversation Themes Demo ===")
    
    sessions = list_sessions()
    
    for session_id in sessions:
        print(f"\nThemes in '{session_id}':")
        themes = get_conversation_themes(session_id, num_themes=3)
        
        if themes:
            for theme in themes:
                print(f"  Theme {theme['theme_id']} ({theme['message_count']} messages):")
                for msg in theme['representative_messages']:
                    print(f"    - {msg['role']}: {msg['content'][:60]}...")
        else:
            print("  No themes found")


def interactive_search():
    """Interactive semantic search mode."""
    try:
        from statecall.semantic_search import search_conversations
    except ImportError:
        print("Semantic search is not available.")
        return
    
    print("\n=== Interactive Semantic Search ===")
    print("Enter search queries to find relevant conversations.")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            query = input("Search: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            results = search_conversations(query, limit=5, min_similarity=0.2)
            
            if results:
                print(f"\nFound {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. Session: {result['session_id']}")
                    print(f"   Role: {result['role']}")
                    print(f"   Content: {result['content']}")
                    print(f"   Similarity: {result['similarity']:.3f}")
                    print(f"   Timestamp: {result['timestamp']}")
            else:
                print("No results found. Try a different query.")
            
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Run the semantic search demo."""
    print("=== StateCall Semantic Search Example ===\n")
    
    # Check if semantic search is available
    try:
        from statecall import SEMANTIC_SEARCH_AVAILABLE
        if not SEMANTIC_SEARCH_AVAILABLE:
            print("Semantic search is not available.")
            print("Install with: pip install sentence-transformers")
            return
    except ImportError:
        print("StateCall semantic search module not found.")
        return
    
    # Create sample data
    sessions = create_sample_conversations()
    
    # Run demos
    demo_semantic_search()
    demo_similar_conversations()
    demo_search_in_session()
    demo_conversation_themes()
    
    # Interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_search()
    else:
        print("\nTo try interactive search, run:")
        print("python examples/semantic_search_example.py --interactive")


if __name__ == "__main__":
    main() 