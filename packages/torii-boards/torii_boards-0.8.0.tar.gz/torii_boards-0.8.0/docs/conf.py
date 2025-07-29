# SPDX-License-Identifier: BSD-2-Clause
import datetime
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath('.'))

from torii_boards import __version__ as boards_version

ROOT_DIR = (Path(__file__).parent).parent


project = 'Torii-HDL Boards'
version = boards_version
release = version.split('+')[0]
copyright = f'{datetime.date.today().year}, Shrine Maiden Heavy Industries'
language  = 'en'
docver    = version

extensions = [
	'sphinx.ext.autodoc',
	'sphinx.ext.extlinks',
	'sphinx.ext.githubpages',
	'sphinx.ext.intersphinx',
	'sphinx.ext.napoleon',
	'sphinx.ext.todo',
	'sphinx_inline_tabs',
	'myst_parser',
	'sphinx_copybutton',
	'sphinx_design',
]


source_suffix = {
	'.rst': 'restructuredtext',
	'.md': 'markdown',
}

extlinks = {
	'issue': ('https://github.com/shrine-maiden-heavy-industries/torii-boards/issues/%s', 'torii-boards/%s'),
	'pypi':  ('https://pypi.org/project/%s/', '%s'),
}

pygments_style         = 'default'
pygments_dark_style    = 'monokai'
autodoc_member_order   = 'bysource'
todo_include_todos     = True

intersphinx_mapping = {
	'python': ('https://docs.python.org/3', None),
	'torii': ('https://torii.shmdn.link/', None)
}


napoleon_google_docstring              = False
napoleon_numpy_docstring               = True
napoleon_use_ivar                      = True
napoleon_use_admonition_for_notes      = True
napoleon_use_admonition_for_examples   = True
napoleon_use_admonition_for_references = True
napoleon_custom_sections  = [
	('Attributes', 'params_style'),
	'Platform overrides'
]

myst_heading_anchors = 3

templates_path = [
	'_templates',
]

html_baseurl     = 'https://torii-boards.shmdn.link/'
html_theme       = 'furo'
html_copy_source = False

html_theme_options = {

}

html_static_path = [
	'_static'
]

html_css_files = [
	'css/styles.css'
]

linkcheck_retries = 2
linkcheck_workers = 1 # At the cost of speed try to prevent rate-limiting
linkcheck_ignore  = [
	'https://www.intel.com/content/www/us/en/products/details/fpga/development-tools/quartus-prime.html',
	'https://www.xilinx.com/products/design-tools/ise-design-suite.html',
	'https://www.xilinx.com/products/design-tools/vivado.html',
	# Digilent is being a big meanie
	'https://digilent.com/reference/programmable-logic/genesys-2/start',
	'https://digilent.com/reference/programmable-logic/atlys/start',
]
