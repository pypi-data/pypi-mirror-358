from typing import Optional, Tuple
import os

def validate_api_token() -> Tuple[bool, str]:
    """
    Validates if the ClickUp API token is present in environment variables.
    
    Returns:
        Tuple[bool, str]: (is_valid, token_or_error_message)
    """
    api_token = os.getenv("CLICKUP_API_TOKEN")
    
    if not api_token:
        return False, "Error: CLICKUP_API_TOKEN environment variable not set"
    
    return True, api_token