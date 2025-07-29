# A user-friendly tool for converting Markdown to PDF

## Installation

```bash
pip install md2pdf-python
```

## Usage

### Use in CMD

```bash
md2pdf --help

md2pdf tests/demo.md -o tests/output-default.pdf
md2pdf tests/demo.md -o tests/output-default.pdf --html
md2pdf tests/demo.md -o tests/output-styles.pdf --css-file tests/demo.css --mermaid-config tests/demo.json
```

### Use in Python

```python
from md2pdf.core.converter import MD2PDF

md2pdf(input_file='input.md', output_file='output.pdf')
md2pdf(input_file='input.md', output_file='output.pdf', html=True)
md2pdf(input_file='input.md', output_file='output.pdf', css_file='custom.css')
md2pdf(input_file='input.md', output_file='output.pdf', css_file='custom.css', mermaid_config='custom-config.json')
```


**mermaid render** is based on [Mermaid-CLI (mmdc)](https://www.npmjs.com/package/@mermaid-js/mermaid-cli), install it with:
`npm install -g @mermaid-js/mermaid-cli`

## Demo
- INPUT: [demo.md](https://suqingdong.github.io/md2pdf/tests/demo.md)
- OUTPUT-DEFAULT: [output-default.pdf](https://suqingdong.github.io/md2pdf/tests/output-default.pdf)
- OUTPUT-STYLES: [output-styles.pdf](https://suqingdong.github.io/md2pdf/tests/output-styles.pdf)
