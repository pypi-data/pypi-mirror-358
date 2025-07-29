import time

import click
import loguru

from md2pdf import version_info, DEFAULT_CSS, MERMAID_CONFIG
from md2pdf.core.converter import MD2PDF


CONTEXT_SETTINGS = dict(
    help_option_names=['-?', '-h', '--help'],
    max_content_width=120,
)

epilog = click.style('''
\n\b
examples:
    {prog} input.md -o output.pdf
    {prog} input.md -o output.pdf --html
    {prog} input.md -o output.pdf --css-file custom.css
    {prog} input.md -o output.pdf --css-file custom.css --mermaid-config custom-config.json

contact: {author}<{author_email}>
''', fg='yellow').format(**version_info)

@click.command(
    name=version_info['prog'],
    help=click.style(version_info['desc'], italic=True, fg='cyan', bold=True),
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
    epilog=epilog,
)
@click.argument('input_md')
@click.option('-o', '--output', help='the output PDF file path', default='output.pdf', show_default=True)
@click.option('--css-file', help='the css file for styling the PDF', default=DEFAULT_CSS, show_default=True)
@click.option('--mermaid-config', help='the config file for mmdc', default=MERMAID_CONFIG, show_default=True)
@click.option('--html', is_flag=True, help='write HTML file')
def cli(input_md, output, css_file, html, mermaid_config):
    start_time = time.time()
    loguru.logger.debug(f'''input arguments:
        input_md:\t{input_md}
        output:\t\t{output}
        write_html:\t{html}
        css_file:\t{css_file}
        mermaid_config:\t{mermaid_config}
    ''')
    MD2PDF().convert(input_md, output, css_file=css_file, write_html=html, mermaid_config=mermaid_config)
    loguru.logger.debug(f'PDF file saved to: {output}')
    loguru.logger.debug(f'time elapsed: {time.time() - start_time:.2f} seconds')


def main():
    cli()


if __name__ == '__main__':
    main()
