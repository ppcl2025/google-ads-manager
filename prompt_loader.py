"""
Prompt Module Loader

This module handles loading and combining prompt modules based on page/feature type.
Uses file-based modules for easy maintenance and updates.
Includes caching to avoid repeated file I/O.
"""

import os
from pathlib import Path
from datetime import datetime

# Global cache for prompt modules (module_name -> {'content': str, 'timestamp': datetime, 'file_mtime': float})
_prompt_cache = {}


# Module combinations per page/feature
PAGE_PROMPT_CONFIGS = {
    'full': ['core', 'bidding_strategy', 'smart_bidding', 'ad_copy', 
             'offline_conversions', 'mcc_portfolio', 'change_tracking', 'keyword_planner'],
    'ad_copy': ['core', 'ad_copy'],
    'keyword_research': ['core', 'keyword_planner', 'keyword_research'],
    'biweekly_report': ['core', 'biweekly_reporting', 'change_tracking'],
    'qa': ['core'],  # Start minimal, add modules dynamically based on question
    'campaign_analysis': ['core', 'bidding_strategy', 'smart_bidding', 'ad_copy',
                          'offline_conversions', 'mcc_portfolio', 'change_tracking']
}


def load_module(module_name, use_cache=True):
    """
    Load a prompt module from file, with optional caching.
    
    Args:
        module_name: Name of the module (without .md extension)
        use_cache: If True, use cached version if file hasn't changed
        
    Returns:
        str: Module content, or empty string if not found
    """
    # Special handling for 'core' module
    original_name = module_name
    if module_name == 'core':
        module_name = 'core_prompt'
    
    # Determine file path
    core_path = Path(__file__).parent / 'prompts' / 'core' / f'{module_name}.md'
    module_path = Path(__file__).parent / 'prompts' / 'modules' / f'{module_name}.md'
    
    file_path = None
    if core_path.exists():
        file_path = core_path
    elif module_path.exists():
        file_path = module_path
    else:
        print(f"⚠️  Warning: Module '{original_name}' not found")
        return ""
    
    # Check cache
    cache_key = original_name
    if use_cache and cache_key in _prompt_cache:
        cache_entry = _prompt_cache[cache_key]
        try:
            # Check if file has been modified since cache
            current_mtime = file_path.stat().st_mtime
            if current_mtime == cache_entry.get('file_mtime', 0):
                # File hasn't changed, return cached content
                return cache_entry['content']
        except (OSError, AttributeError):
            # File might have been deleted or path issue, fall through to reload
            pass
    
    # Load from file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update cache
        _prompt_cache[cache_key] = {
            'content': content,
            'timestamp': datetime.now(),
            'file_mtime': file_path.stat().st_mtime
        }
        
        return content
    except Exception as e:
        print(f"⚠️  Warning: Error loading module '{original_name}': {e}")
        return ""


def build_prompt(page_type, include_keyword_planner=False, additional_modules=None):
    """
    Build prompt with only needed modules for a specific page/feature.
    
    Args:
        page_type: Type of page/feature ('full', 'ad_copy', 'keyword_research', 
                  'biweekly_report', 'qa', 'campaign_analysis')
        include_keyword_planner: Whether to include keyword planner module (for full analysis)
        additional_modules: List of additional module names to include
        
    Returns:
        str: Combined prompt text
    """
    # Get base modules for this page type
    modules = PAGE_PROMPT_CONFIGS.get(page_type, ['core']).copy()
    
    # Add keyword planner if requested (for full analysis)
    if include_keyword_planner and 'keyword_planner' not in modules:
        modules.append('keyword_planner')
    
    # Add any additional modules
    if additional_modules:
        for module in additional_modules:
            if module not in modules:
                modules.append(module)
    
    # Load and combine modules
    prompt_parts = []
    for module_name in modules:
        module_content = load_module(module_name)
        if module_content:
            prompt_parts.append(module_content)
    
    # Join with double newlines for separation
    return '\n\n'.join(prompt_parts)


def detect_qa_modules(user_question):
    """
    Detect which modules to load for Q&A based on question content.
    
    Args:
        user_question: The user's question text
        
    Returns:
        list: Additional module names to load
    """
    question_lower = user_question.lower()
    additional_modules = []
    
    # Keyword-related questions
    if any(word in question_lower for word in ['keyword', 'match type', 'search term', 'negative keyword']):
        additional_modules.append('keyword_planner')
    
    # Bidding-related questions
    if any(word in question_lower for word in ['bidding', 'bid strategy', 'maximize clicks', 'maximize conversions', 'target cpa']):
        additional_modules.extend(['bidding_strategy', 'smart_bidding'])
    
    # Ad copy questions
    if any(word in question_lower for word in ['ad copy', 'headline', 'description', 'ad text', 'creative']):
        additional_modules.append('ad_copy')
    
    # Conversion tracking questions
    if any(word in question_lower for word in ['conversion', 'offline conversion', 'gclid', 'funnel']):
        additional_modules.append('offline_conversions')
    
    # MCC/portfolio questions
    if any(word in question_lower for word in ['mcc', 'portfolio', 'multi-client', 'shared']):
        additional_modules.append('mcc_portfolio')
    
    # Reporting questions
    if any(word in question_lower for word in ['report', 'client report', 'biweekly']):
        additional_modules.append('biweekly_reporting')
    
    return additional_modules


def get_prompt_for_page(page_type, **kwargs):
    """
    Get the appropriate prompt for a page/feature type.
    
    Args:
        page_type: Type of page ('full', 'ad_copy', 'keyword_research', 
                  'biweekly_report', 'qa', 'campaign_analysis')
        **kwargs: Additional arguments:
            - include_keyword_planner: bool (for full/campaign_analysis)
            - user_question: str (for qa type)
            - additional_modules: list (any additional modules)
            
    Returns:
        str: Combined prompt text
    """
    include_keyword_planner = kwargs.get('include_keyword_planner', False)
    additional_modules = kwargs.get('additional_modules', None)
    
    # For Q&A, detect modules from question
    if page_type == 'qa' and 'user_question' in kwargs:
        detected_modules = detect_qa_modules(kwargs['user_question'])
        if detected_modules:
            if additional_modules:
                additional_modules.extend(detected_modules)
            else:
                additional_modules = detected_modules
    
    return build_prompt(page_type, include_keyword_planner, additional_modules)


# Example usage
if __name__ == '__main__':
    # Test loading different prompt types
    print("Testing prompt loader...\n")
    
    # Test full prompt
    print("1. Full prompt (campaign analysis):")
    full_prompt = get_prompt_for_page('campaign_analysis', include_keyword_planner=True)
    print(f"   Loaded {len(full_prompt)} characters\n")
    
    # Test ad copy prompt
    print("2. Ad copy prompt:")
    ad_copy_prompt = get_prompt_for_page('ad_copy')
    print(f"   Loaded {len(ad_copy_prompt)} characters\n")
    
    # Test keyword research prompt
    print("3. Keyword research prompt:")
    keyword_prompt = get_prompt_for_page('keyword_research')
    print(f"   Loaded {len(keyword_prompt)} characters\n")
    
    # Test Q&A prompt with detection
    print("4. Q&A prompt (bidding question):")
    qa_prompt = get_prompt_for_page('qa', user_question="How do I optimize my bidding strategy?")
    print(f"   Loaded {len(qa_prompt)} characters\n")
    
    print("✅ Prompt loader test complete!")

