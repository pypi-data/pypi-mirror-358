import re
import os
import json
import base64
import shutil
import tempfile
import subprocess

import loguru

from md2pdf import MERMAID_CONFIG


def mermaid_to_data_url(mermaid_code: str, config=MERMAID_CONFIG) -> str:
    """convert mermaid code to data URL format

    Args:
        mermaid_code (str): mermaid code
    Returns:
        str: data URL format of the mermaid diagram as an image
    """
    if shutil.which('mmdc') is None:
        return f'```mermaid\n{mermaid_code}\n```'

    with tempfile.NamedTemporaryFile(suffix='.mmd', delete=False) as mmd_file:
        mmd_file.write(mermaid_code.encode('utf-8'))
        mmd_file_path = mmd_file.name
        png_file_path = mmd_file_path.replace('.mmd', '.png')
    cmd = f'mmdc -i {mmd_file_path} -o {png_file_path}'

    if config and os.path.exists(config):
        try:
            data = json.load(open(config, 'r', encoding='utf-8'))
            cmd += f' -c {config}'
            if data.get('backgroundColor'):
                cmd += f' --backgroundColor {data["backgroundColor"]}'
        except json.JSONDecodeError:
            loguru.logger.warning(f'invalid JSON config file: {config}')
            pass
    
    loguru.logger.debug(f'>>> run command: {cmd}')

    res = subprocess.run(cmd, shell=True, check=True, text=True)
    if res.returncode != 0:
        return f'```mermaid\n{mermaid_code}\n```'
    
    with open(png_file_path, 'rb') as png_file:
        png_data = png_file.read()
        b64_data = base64.b64encode(png_data).decode('utf-8')
        data_url = f"data:image/png;base64,{b64_data}"
        return f'<img src="{data_url}" alt="Mermaid Diagram" style="display:block; margin:0 auto;">'

    # delete temporary files
    os.unlink(mmd_file_path)
    os.unlink(png_file_path)


def process_mermaid_block(md_text: str, config=MERMAID_CONFIG) -> str:
    """process mermaid blocks with mmdc and convert to data URL format
    
    Args:
        md_text (str): markdown text
    Returns:
        str: processed markdown text with mermaid blocks replaced by data URLs
    """
    def replace_mermaid_block(match):
        content = match.group(1).strip()
        data_url = mermaid_to_data_url(content, config=config)
        return data_url

    # search for mermaid blocks and replace them with data URLs
    md_text = re.sub(r'```mermaid\s*([\s\S]+?)\s*```', replace_mermaid_block, md_text)

    return md_text
