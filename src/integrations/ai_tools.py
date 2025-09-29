"""
AI tool integrations for content generation.

This module provides interfaces to various AI services for content generation.
"""

from typing import Optional, Dict, List
import re


def extract_structured_content_with_ai(scraped_content: str, feature_name: str) -> Dict[str, List[str]]:
    """
    Extract structured information from scraped documentation using AI-powered analysis.

    In production, this would call Claude/GPT. For demo mode, uses intelligent parsing.

    Args:
        scraped_content: Raw scraped documentation text
        feature_name: Name of the feature for context

    Returns:
        Dictionary with use_cases, key_capabilities, benefits, and requirements
    """

    # This is a sophisticated extraction that mimics LLM behavior
    # In production, replace with actual LLM API call

    result = {
        'use_cases': [],
        'key_capabilities': [],
        'benefits': [],
        'technical_requirements': []
    }

    # Limit content size for processing
    content = scraped_content[:3000]

    # Extract use cases - look for common patterns
    use_case_patterns = [
        r'(?:use cases?|applications?|scenarios?)[:\s]+([^.!?]+[.!?])',
        r'(?:used for|ideal for|perfect for|great for)[:\s]+([^.!?]+[.!?])',
        r'(?:enables?|allows?)[^.]+?(?:to|for)\s+([^.!?]{20,120}[.!?])'
    ]

    for pattern in use_case_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches[:3]:
            clean = match.strip()
            if 20 < len(clean) < 150:
                # Split on common delimiters
                items = re.split(r'[,;]\s*(?:and\s+)?', clean)
                for item in items:
                    item = item.strip().rstrip('.,;')
                    if 15 < len(item) < 120:
                        result['use_cases'].append(item)
        if len(result['use_cases']) >= 5:
            break

    # Extract key capabilities - look for action verbs
    capability_verbs = ['allows you to', 'enables you to', 'allows', 'enables', 'provides',
                       'supports', 'handles', 'manages', 'simplifies', 'automates',
                       'integrates', 'offers', 'delivers', 'ensures', 'can act like']

    # Split on periods followed by space and capital letter
    sentences = re.split(r'\.\s+(?=[A-Z])', content)

    for sentence in sentences[:25]:
        sentence = sentence.strip()
        if len(sentence) < 30:
            continue

        for verb in capability_verbs:
            if verb in sentence.lower():
                # Extract the full capability sentence
                clean = sentence

                # Remove common document prefixes
                for prefix in ['The feature ', 'It ', 'The ' + feature_name]:
                    if clean.startswith(prefix):
                        clean = clean[len(prefix):].strip()
                        break

                # Capitalize first letter if needed
                if clean and clean[0].islower():
                    clean = clean[0].upper() + clean[1:]

                # Add period if missing
                if clean and not clean.endswith(('.', '!', '?')):
                    clean += '.'

                # Good capability statement - be more lenient on length
                if 50 < len(clean) < 250 and verb.lower() in clean.lower():
                    result['key_capabilities'].append(clean)
                    if len(result['key_capabilities']) >= 6:
                        break
                break  # Only one verb per sentence

        if len(result['key_capabilities']) >= 6:
            break

    # Extract benefits - look for outcome language
    benefit_keywords = ['reduce', 'improve', 'increase', 'faster', 'easier', 'better',
                       'eliminate', 'streamline', 'optimize', 'enhance', 'boost']

    for sentence in sentences[:25]:
        for keyword in benefit_keywords:
            if keyword in sentence.lower():
                clean = sentence.strip()
                # Look for quantified benefits
                if any(char.isdigit() or '%' in clean for char in clean) or len(clean) > 30:
                    if 25 < len(clean) < 150:
                        result['benefits'].append(clean)
                        if len(result['benefits']) >= 5:
                            break
                break
        if len(result['benefits']) >= 5:
            break

    # Extract technical requirements
    if 'prerequisite' in content.lower() or 'requirement' in content.lower() or 'must' in content.lower():
        req_section_start = content.lower().find('prerequisite')
        if req_section_start < 0:
            req_section_start = content.lower().find('requirement')
        if req_section_start < 0:
            req_section_start = 0

        req_content = content[req_section_start:req_section_start + 800]
        req_sentences = re.split(r'[.!?]+\s+', req_content)

        for sentence in req_sentences[:10]:
            if any(word in sentence.lower() for word in ['must', 'require', 'need', 'should have']):
                clean = sentence.strip()
                if 25 < len(clean) < 140:
                    result['technical_requirements'].append(clean)
                    if len(result['technical_requirements']) >= 4:
                        break

    return result


def claude_generate(prompt: str, feature_context: Optional[str] = None) -> str:
    """
    Generate content using Claude AI.

    Args:
        prompt: The generation prompt
        feature_context: Optional feature context

    Returns:
        Generated content
    """
    # Placeholder implementation - will be replaced with actual AI integration
    return f"Generated content for prompt: {prompt[:50]}..."