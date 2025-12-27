"""
Helper function to parse LLM JSON responses
"""

import json
import re

def parse_llm_json(llm_response: str, default_values: dict = None) -> dict:
    """
    Parse JSON from LLM response
    
    Args:
        llm_response: Raw LLM response text
        default_values: Default values to return if parsing fails
        
    Returns:
        Parsed JSON dict or default values
    """
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', llm_response)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
    except Exception as e:
        print(f"JSON parse error: {e}")
    
    return default_values or {}
