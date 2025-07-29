import re


def process_latex_formula(md_text: str) -> str:
    """Process LaTeX formulas in markdown text, converting block and inline formulas to appropriate formats.

    Args:
        md_text (str): Markdown text containing LaTeX formulas.
    Returns:
        str: Processed markdown text with LaTeX formulas converted to code blocks or inline formats
    """
    def replace_block_formula(match):
        formula = match.group(1).strip()
        return f'```latex\n$$\n{formula}\n$$\n```'

    def replace_inline_formula(match):
        formula = match.group(1).strip()
        return f'`${formula}$`'

    # payattention to the order: process block formulas first, then inline formulas to avoid conflicts
    md_text = re.sub(r'\$\$\s*([\s\S]+?)\s*\$\$', replace_block_formula, md_text)
    md_text = re.sub(r'(?<!\$)\$(.+?)\$(?!\$)', replace_inline_formula, md_text)

    return md_text
