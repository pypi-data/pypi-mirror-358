import re


def process_checkbox(md_text: str, checked_symbol: str = '☑', unchecked_symbol: str = '☐') -> str:
    """Process checkboxes in markdown text, converting them to appropriate symbols.

    Args:
        md_text (str): Markdown text containing checkboxes.
        checked_symbol (str): Symbol to use for checked checkboxes.
        unchecked_symbol (str): Symbol to use for unchecked checkboxes.
    Returns:
        str: Processed markdown text with checkboxes converted to symbols.
    """
    # payattension to the order: process completed checkboxes first, then incomplete ones to avoid conflicts
    md_text = re.sub(r'^(\s)*- \[x\]', r'\1' + checked_symbol, md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^(\s)*- \[ \]', r'\1' + unchecked_symbol, md_text, flags=re.MULTILINE)
    return md_text
