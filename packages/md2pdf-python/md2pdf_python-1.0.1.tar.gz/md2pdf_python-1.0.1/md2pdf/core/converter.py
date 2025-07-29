from pathlib import Path

import loguru
import markdown
from weasyprint import HTML
from md2html.core import MD2HTML

from md2pdf import utils, DEFAULT_CSS, MERMAID_CONFIG


class MD2PDF(object):

    def __init__(self):
        self.md = self.init_md()

    def init_md(self):
        return markdown.Markdown(
            extensions=[
                'extra',
                'toc',
                'pymdownx.blocks.definition',
                'pymdownx.blocks.details',
                'pymdownx.b64',
                'pymdownx.emoji',
                'pymdownx.superfences',
                'pymdownx.highlight',
            ],
            extension_configs={
                'pymdownx.highlight': {
                    'use_pygments': True,
                    'linenums': True,
                },
            }
        )

    def convert(
            self,
            md_path: str,
            pdf_path: str,
            write_html: bool = False,
            css_file: str = DEFAULT_CSS,
            mermaid_config: str = MERMAID_CONFIG,
        ):
        """Convert markdown file to PDF.
        
        Args:
            md_path (str): path of markdown file.
            pdf_path (str): path of output PDF file.
        Returns:
            None
        """
        with open(md_path, encoding='utf-8') as f:
            md_text = f.read()

        md_text = utils.process_checkbox(md_text)
        md_text = utils.process_mermaid_block(md_text, config=mermaid_config)
        md_text = utils.process_latex_formula(md_text)

        m2h = MD2HTML(md_text)
        m2h.md = self.md
        html = m2h.convert()

        html = html.replace('</style>', '@page {padding: 0; margin: 0;}</style>')

        if css_file and Path(css_file).exists():
            with open(css_file, encoding='utf-8') as css_f:
                css_content = css_f.read()
            html = html.replace('</style>', f'{css_content}</style>')
        
        if write_html:
            html_path = Path(pdf_path).with_suffix('.html')
            with open(html_path, 'w', encoding='utf-8') as html_f:
                html_f.write(html)
            loguru.logger.debug(f'HTML file saved to: {html_path}')

        HTML(string=html, base_url='.').write_pdf(pdf_path)


if __name__ == '__main__':
    MD2PDF().convert('tests/demo.md', 'output.pdf')