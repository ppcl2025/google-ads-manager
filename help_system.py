"""
Help System for Google Ads Account Manager
Loads documentation and provides AI-powered answers using Claude
"""

from pathlib import Path
import re
from typing import Dict, List, Tuple


def load_documentation() -> Dict[str, str]:
    """
    Load all markdown files from docs folder.
    
    Returns:
        Dictionary mapping document names to their content
    """
    docs = {}
    docs_path = Path(__file__).parent / 'docs'
    
    if not docs_path.exists():
        return docs
    
    for md_file in sorted(docs_path.glob('*.md')):
        # Skip README.md as it's just an index
        if md_file.name == 'README.md':
            continue
            
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Use filename without extension as key
                doc_name = md_file.stem
                docs[doc_name] = content
        except Exception as e:
            print(f"Warning: Could not load {md_file.name}: {e}")
    
    return docs


def find_relevant_docs(query: str, docs_dict: Dict[str, str], top_n: int = 3) -> List[Tuple[str, str, int]]:
    """
    Find most relevant documents using keyword matching.
    
    Args:
        query: User's question
        docs_dict: Dictionary of document names to content
        top_n: Number of top documents to return
    
    Returns:
        List of tuples: (doc_name, content, relevance_score), sorted by relevance
    """
    query_lower = query.lower()
    query_words = set(re.findall(r'\b\w+\b', query_lower))
    
    relevance_scores = []
    
    for doc_name, content in docs_dict.items():
        content_lower = content.lower()
        
        # Calculate relevance score
        # Count exact word matches
        word_matches = sum(1 for word in query_words if word in content_lower)
        
        # Bonus for phrase matches (2+ consecutive words)
        phrase_bonus = 0
        query_phrases = []
        words_list = list(query_words)
        if len(words_list) >= 2:
            # Check for 2-word phrases
            for i in range(len(words_list) - 1):
                phrase = f"{words_list[i]} {words_list[i+1]}"
                if phrase in content_lower:
                    phrase_bonus += 2
        
        # Bonus for title/header matches (lines starting with #)
        header_matches = 0
        for word in query_words:
            # Check if word appears in headers
            header_pattern = rf'^#+\s+.*\b{re.escape(word)}\b'
            if re.search(header_pattern, content, re.MULTILINE | re.IGNORECASE):
                header_matches += 1
        
        total_score = word_matches + phrase_bonus + (header_matches * 2)
        
        if total_score > 0:
            relevance_scores.append((doc_name, content, total_score))
    
    # Sort by relevance score (descending) and return top N
    relevance_scores.sort(key=lambda x: x[2], reverse=True)
    return relevance_scores[:top_n]


def format_docs_for_prompt(relevant_docs: List[Tuple[str, str, int]]) -> str:
    """
    Format relevant documents for inclusion in Claude prompt.
    
    Args:
        relevant_docs: List of (doc_name, content, score) tuples
    
    Returns:
        Formatted string with document contents
    """
    if not relevant_docs:
        return "No relevant documentation found."
    
    formatted = []
    for doc_name, content, score in relevant_docs:
        # Clean up document name for display
        display_name = doc_name.replace('_', ' ').title()
        
        # Truncate very long documents (keep first 8000 chars to stay within token limits)
        content_preview = content[:8000]
        if len(content) > 8000:
            content_preview += "\n\n[... content truncated ...]"
        
        formatted.append(f"=== {display_name} ===\n{content_preview}\n")
    
    return "\n".join(formatted)


def get_document_citations(relevant_docs: List[Tuple[str, str, int]]) -> List[str]:
    """
    Get list of document names for citation.
    
    Args:
        relevant_docs: List of (doc_name, content, score) tuples
    
    Returns:
        List of formatted document names
    """
    citations = []
    for doc_name, _, score in relevant_docs:
        display_name = doc_name.replace('_', ' ').title()
        citations.append(f"{display_name} (relevance: {score})")
    return citations


def create_help_prompt(user_question: str, relevant_docs: str) -> str:
    """
    Create the prompt for Claude to answer help questions.
    
    Args:
        user_question: User's question
        relevant_docs: Formatted documentation content
    
    Returns:
        Complete prompt string
    """
    prompt = f"""You are a helpful documentation assistant for the Google Ads Account Manager - AI Agent web application.

The user asked: "{user_question}"

Here is relevant documentation from the app's documentation:

{relevant_docs}

Please provide a clear, concise answer based on the documentation above. Follow these guidelines:

1. **Answer directly** - Provide a helpful, actionable answer
2. **Cite sources** - At the end, mention which document(s) you referenced (e.g., "Source: User Guide, Setup Guide")
3. **Be specific** - Include step-by-step instructions when relevant
4. **Stay focused** - Only answer what's in the documentation. If the answer isn't there, say so
5. **Format nicely** - Use markdown formatting (headers, lists, code blocks) for readability
6. **Keep it concise** - Aim for 2-4 paragraphs unless the question requires more detail

Answer:"""
    
    return prompt


def get_suggested_questions() -> List[str]:
    """
    Get list of suggested questions for the help chat.
    
    Returns:
        List of suggested question strings
    """
    return [
        "How do I run a campaign analysis?",
        "What is change tracking and how does it work?",
        "How do I set up geo-targeting for keyword research?",
        "How do I export a biweekly report to PDF?",
        "What Claude model should I use?",
        "How do I create a new sub-account?",
        "How does automatic change detection work?",
        "What's the difference between Campaign Analysis and Ad Copy Optimization?",
        "How do I save reports to Google Drive?",
        "How do I authenticate with Google Ads API?",
        "What is the modular prompt system?",
        "How do I use Keyword Research with campaign geo-targeting?"
    ]

