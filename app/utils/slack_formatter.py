"""Convert standard markdown to Slack's mrkdwn format."""

import re


def markdown_to_slack(text: str) -> str:
    """
    Convert standard markdown to Slack's mrkdwn format.

    Slack mrkdwn differences:
    - Bold: *text* (not **text**)
    - Italic: _text_ (same)
    - Strikethrough: ~text~ (same)
    - Headers: Just bold text (no # support)
    - Code blocks: ```code``` (same)

    Args:
        text: Standard markdown text

    Returns:
        Slack mrkdwn formatted text
    """
    # Preserve code blocks first (don't modify content inside them)
    code_blocks = []

    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks) - 1}__"

    # Save code blocks
    text = re.sub(r'```[\s\S]*?```', save_code_block, text)

    # Convert headers (### Header -> *Header*)
    text = re.sub(r'^#{1,6}\s+(.+)$', r'*\1*', text, flags=re.MULTILINE)

    # Convert bold (**text** -> *text*)
    # Be careful not to convert already-single asterisks
    text = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', text)

    # Convert italic with underscores (already compatible)
    # _text_ works in both

    # Convert [text](url) links to <url|text>
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<\2|\1>', text)

    # Convert horizontal rules (--- or ***) to a line of dashes
    text = re.sub(r'^[-*]{3,}$', '─' * 30, text, flags=re.MULTILINE)

    # Restore code blocks
    for i, block in enumerate(code_blocks):
        text = text.replace(f"__CODE_BLOCK_{i}__", block)

    return text
