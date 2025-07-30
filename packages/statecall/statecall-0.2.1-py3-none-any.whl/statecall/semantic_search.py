"""
Semantic search functionality for StateCall library.
Enables finding conversations by meaning, not just keywords.
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re

try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from .memory import _load_history_data, list_sessions


class SemanticSearcher:
    """
    Provides semantic search capabilities across conversations.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic searcher.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for semantic search. "
                "Install it with: pip install sentence-transformers"
            )
        
        self.model = SentenceTransformer(model_name)
        self._embeddings_cache = {}
        self._cache_file = ".statecall_embeddings.json"
        self._load_embeddings_cache()
    
    def _load_embeddings_cache(self):
        """Load cached embeddings from file."""
        try:
            with open(self._cache_file, 'r') as f:
                cache_data = json.load(f)
                # Convert lists back to numpy arrays
                for key, value in cache_data.items():
                    if isinstance(value, dict) and 'embedding' in value:
                        value['embedding'] = np.array(value['embedding'])
                self._embeddings_cache = cache_data
        except (FileNotFoundError, json.JSONDecodeError):
            self._embeddings_cache = {}
    
    def _save_embeddings_cache(self):
        """Save embeddings cache to file."""
        # Convert numpy arrays to lists for JSON serialization
        cache_to_save = {}
        for key, value in self._embeddings_cache.items():
            if isinstance(value, dict) and 'embedding' in value:
                cache_copy = value.copy()
                cache_copy['embedding'] = value['embedding'].tolist()
                cache_to_save[key] = cache_copy
            else:
                cache_to_save[key] = value
        
        with open(self._cache_file, 'w') as f:
            json.dump(cache_to_save, f, indent=2)
    
    def _create_message_key(self, session_id: str, message_index: int, content: str) -> str:
        """Create a unique key for a message."""
        # Use content hash for cache invalidation
        content_hash = str(hash(content))
        return f"{session_id}_{message_index}_{content_hash}"
    
    def _get_or_create_embedding(self, text: str, cache_key: str) -> np.ndarray:
        """Get embedding from cache or create new one."""
        if cache_key in self._embeddings_cache:
            return self._embeddings_cache[cache_key]['embedding']
        
        # Create new embedding
        embedding = self.model.encode(text)
        self._embeddings_cache[cache_key] = {
            'embedding': embedding,
            'text': text,
            'created_at': datetime.now().isoformat()
        }
        
        # Save cache periodically (every 10 new embeddings)
        if len(self._embeddings_cache) % 10 == 0:
            self._save_embeddings_cache()
        
        return embedding
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better semantic search."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Limit length to avoid very long texts
        if len(text) > 500:
            text = text[:500] + "..."
        return text
    
    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def search_conversations(self, query: str, limit: int = 10, min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """
        Search for conversations semantically similar to the query.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            min_similarity: Minimum similarity threshold (0-1)
            
        Returns:
            List of matching conversation snippets with metadata
        """
        if not query.strip():
            return []
        
        query = self._preprocess_text(query)
        query_embedding = self.model.encode(query)
        
        history_data = _load_history_data()
        results = []
        
        for session_id, messages in history_data.items():
            for i, message in enumerate(messages):
                content = self._preprocess_text(message['content'])
                cache_key = self._create_message_key(session_id, i, content)
                
                # Get or create embedding for this message
                message_embedding = self._get_or_create_embedding(content, cache_key)
                
                # Calculate similarity
                similarity = self._calculate_similarity(query_embedding, message_embedding)
                
                if similarity >= min_similarity:
                    results.append({
                        'session_id': session_id,
                        'message_index': i,
                        'role': message['role'],
                        'content': message['content'],
                        'timestamp': message.get('timestamp', ''),
                        'similarity': float(similarity),
                        'context': self._get_message_context(session_id, i, messages)
                    })
        
        # Sort by similarity (highest first) and limit results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Save cache after search
        self._save_embeddings_cache()
        
        return results[:limit]
    
    def _get_message_context(self, session_id: str, message_index: int, messages: List[Dict], context_size: int = 2) -> Dict[str, Any]:
        """Get context around a message (previous and next messages)."""
        start_idx = max(0, message_index - context_size)
        end_idx = min(len(messages), message_index + context_size + 1)
        
        context_messages = []
        for i in range(start_idx, end_idx):
            context_messages.append({
                'role': messages[i]['role'],
                'content': messages[i]['content'],
                'is_match': i == message_index
            })
        
        return {
            'before': context_messages[:context_size],
            'match': context_messages[context_size] if len(context_messages) > context_size else None,
            'after': context_messages[context_size + 1:] if len(context_messages) > context_size else []
        }
    
    def find_similar_conversations(self, session_id: str, threshold: float = 0.7, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find conversations similar to a given session.
        
        Args:
            session_id: Session to find similar conversations for
            threshold: Similarity threshold (0-1)
            limit: Maximum number of similar sessions to return
            
        Returns:
            List of similar sessions with similarity scores
        """
        history_data = _load_history_data()
        
        if session_id not in history_data:
            return []
        
        # Get all messages from the target session
        target_messages = history_data[session_id]
        target_text = " ".join([msg['content'] for msg in target_messages])
        target_text = self._preprocess_text(target_text)
        
        # Create embedding for target session
        target_cache_key = f"session_{session_id}_{hash(target_text)}"
        target_embedding = self._get_or_create_embedding(target_text, target_cache_key)
        
        similarities = []
        
        for other_session_id, other_messages in history_data.items():
            if other_session_id == session_id:
                continue
            
            # Get all messages from other session
            other_text = " ".join([msg['content'] for msg in other_messages])
            other_text = self._preprocess_text(other_text)
            
            # Create embedding for other session
            other_cache_key = f"session_{other_session_id}_{hash(other_text)}"
            other_embedding = self._get_or_create_embedding(other_text, other_cache_key)
            
            # Calculate similarity
            similarity = self._calculate_similarity(target_embedding, other_embedding)
            
            if similarity >= threshold:
                similarities.append({
                    'session_id': other_session_id,
                    'similarity': float(similarity),
                    'message_count': len(other_messages),
                    'last_updated': other_messages[-1].get('timestamp', '') if other_messages else ''
                })
        
        # Sort by similarity and limit results
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Save cache
        self._save_embeddings_cache()
        
        return similarities[:limit]
    
    def search_in_session(self, session_id: str, query: str, limit: int = 5, min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """
        Search within a specific session.
        
        Args:
            session_id: Session to search in
            query: Search query
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of matching messages with context
        """
        if not query.strip():
            return []
        
        query = self._preprocess_text(query)
        query_embedding = self.model.encode(query)
        
        history_data = _load_history_data()
        
        if session_id not in history_data:
            return []
        
        messages = history_data[session_id]
        results = []
        
        for i, message in enumerate(messages):
            content = self._preprocess_text(message['content'])
            cache_key = self._create_message_key(session_id, i, content)
            
            message_embedding = self._get_or_create_embedding(content, cache_key)
            similarity = self._calculate_similarity(query_embedding, message_embedding)
            
            if similarity >= min_similarity:
                results.append({
                    'message_index': i,
                    'role': message['role'],
                    'content': message['content'],
                    'timestamp': message.get('timestamp', ''),
                    'similarity': float(similarity),
                    'context': self._get_message_context(session_id, i, messages)
                })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        self._save_embeddings_cache()
        
        return results[:limit]
    
    def get_conversation_themes(self, session_id: str, num_themes: int = 5) -> List[Dict[str, Any]]:
        """
        Extract main themes from a conversation using clustering.
        
        Args:
            session_id: Session to analyze
            num_themes: Number of themes to extract
            
        Returns:
            List of themes with representative messages
        """
        history_data = _load_history_data()
        
        if session_id not in history_data:
            return []
        
        messages = history_data[session_id]
        if len(messages) < 2:
            return []
        
        # Get embeddings for all messages
        embeddings = []
        message_data = []
        
        for i, message in enumerate(messages):
            content = self._preprocess_text(message['content'])
            cache_key = self._create_message_key(session_id, i, content)
            
            embedding = self._get_or_create_embedding(content, cache_key)
            embeddings.append(embedding)
            message_data.append({
                'index': i,
                'content': message['content'],
                'role': message['role'],
                'timestamp': message.get('timestamp', '')
            })
        
        # Simple clustering based on similarity
        embeddings = np.array(embeddings)
        themes = []
        used_indices = set()
        
        for i in range(min(num_themes, len(embeddings))):
            if i in used_indices:
                continue
            
            # Find the message most similar to others (potential theme center)
            similarities = []
            for j in range(len(embeddings)):
                if j not in used_indices:
                    sim = self._calculate_similarity(embeddings[i], embeddings[j])
                    similarities.append((j, sim))
            
            # Sort by similarity and take top messages for this theme
            similarities.sort(key=lambda x: x[1], reverse=True)
            theme_messages = []
            
            for msg_idx, sim in similarities[:3]:  # Top 3 similar messages
                if msg_idx not in used_indices:
                    theme_messages.append({
                        **message_data[msg_idx],
                        'similarity_to_theme': float(sim)
                    })
                    used_indices.add(msg_idx)
            
            if theme_messages:
                themes.append({
                    'theme_id': i + 1,
                    'representative_messages': theme_messages,
                    'message_count': len(theme_messages)
                })
        
        self._save_embeddings_cache()
        return themes


# Convenience functions for easy access
_searcher = None

def get_searcher() -> SemanticSearcher:
    """Get or create the global semantic searcher instance."""
    global _searcher
    if _searcher is None:
        _searcher = SemanticSearcher()
    return _searcher


def search_conversations(query: str, limit: int = 10, min_similarity: float = 0.3) -> List[Dict[str, Any]]:
    """
    Search for conversations semantically similar to the query.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        min_similarity: Minimum similarity threshold (0-1)
        
    Returns:
        List of matching conversation snippets with metadata
    """
    searcher = get_searcher()
    return searcher.search_conversations(query, limit, min_similarity)


def find_similar_conversations(session_id: str, threshold: float = 0.7, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Find conversations similar to a given session.
    
    Args:
        session_id: Session to find similar conversations for
        threshold: Similarity threshold (0-1)
        limit: Maximum number of similar sessions to return
        
    Returns:
        List of similar sessions with similarity scores
    """
    searcher = get_searcher()
    return searcher.find_similar_conversations(session_id, threshold, limit)


def search_in_session(session_id: str, query: str, limit: int = 5, min_similarity: float = 0.3) -> List[Dict[str, Any]]:
    """
    Search within a specific session.
    
    Args:
        session_id: Session to search in
        query: Search query
        limit: Maximum number of results
        min_similarity: Minimum similarity threshold
        
    Returns:
        List of matching messages with context
    """
    searcher = get_searcher()
    return searcher.search_in_session(session_id, query, limit, min_similarity)


def get_conversation_themes(session_id: str, num_themes: int = 5) -> List[Dict[str, Any]]:
    """
    Extract main themes from a conversation.
    
    Args:
        session_id: Session to analyze
        num_themes: Number of themes to extract
        
    Returns:
        List of themes with representative messages
    """
    searcher = get_searcher()
    return searcher.get_conversation_themes(session_id, num_themes)