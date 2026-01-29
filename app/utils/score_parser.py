"""Score extraction from Gemini responses."""

import re

# Default threshold, can be overridden via settings
DEFAULT_SCORE_THRESHOLD = 80


def extract_score(response_text: str) -> int | None:
    """
    Extract the overall score from a Gemini response.

    Looks for patterns like:
    - OVERALL SCORE: [85]
    - OVERALL SCORE: 85
    - Overall Score: [85]

    Args:
        response_text: The full response from Gemini

    Returns:
        The extracted score as an integer, or None if not found
    """
    # Pattern to match "OVERALL SCORE" followed by a number (with or without brackets)
    patterns = [
        r"OVERALL\s+SCORE\s*:\s*\[?(\d{1,3})\]?",  # OVERALL SCORE: [85] or OVERALL SCORE: 85
        r"Overall\s+Score\s*:\s*\[?(\d{1,3})\]?",  # Overall Score: [85]
        r"\*\*OVERALL\s+SCORE\*\*\s*:\s*\[?(\d{1,3})\]?",  # **OVERALL SCORE**: [85]
    ]

    for pattern in patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            # Ensure score is within valid range
            if 0 <= score <= 100:
                return score

    return None


def is_approved(score: int | None, threshold: int | None = None) -> bool:
    """
    Check if a score meets the approval threshold.

    Args:
        score: The score to check, or None
        threshold: Optional custom threshold, defaults to settings.score_threshold

    Returns:
        True if score >= threshold, False otherwise
    """
    if score is None:
        return False

    if threshold is None:
        from app.config import settings
        threshold = settings.score_threshold

    return score >= threshold


def extract_virality_tier(response_text: str) -> str | None:
    """
    Extract the predicted virality tier from a Gemini response.

    Args:
        response_text: The full response from Gemini

    Returns:
        The virality tier (e.g., "HIGH", "MEDIUM", "LOW"), or None if not found
    """
    pattern = r"Predicted\s+Virality\s+Tier\s*:\s*\[?(\w+)\]?"
    match = re.search(pattern, response_text, re.IGNORECASE)

    if match:
        return match.group(1).upper()

    return None
