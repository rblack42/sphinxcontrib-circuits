import re
import os
import sys
import sphinx_rtd_theme
sys.path.insert(0,'../src')
sys.path.insert(0, '.')
import circuits.__about__ as about
version = about.__version__
author = about.__author__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx_exts.rail',
]
if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling'
    spelling_show_suggestions = True,
    spelling_lang = 'en_US'

source_suffix = '.rst'
master_doc = 'index'
project = u'Circuits'
copyright = u'2014, %s' % author
version = release = version
today_fmt = '%B %d, %Y'

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {}
html_title = "rstParser"
html_short_title = ""
html_logo = '_static/images/ACClogo.png'
html_static_path = ['_static']
html_last_updated_fmt = '%b %d, %Y'
html_show_sourcelink = False
html_show_sphinx = True
html_show_copyright = True

