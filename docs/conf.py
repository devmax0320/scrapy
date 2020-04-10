# -*- coding: utf-8 -*-
#
# Scrapy documentation build configuration file, created by
# sphinx-quickstart on Mon Nov 24 12:02:52 2008.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys
from datetime import datetime
from os import path
from pathlib import Path

# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
sys.path.append(path.join(path.dirname(__file__), "_ext"))
sys.path.insert(0, path.dirname(path.dirname(__file__)))


# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'hoverxref.extension',
    'notfound.extension',
    'scrapydocs',
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Scrapy'
copyright = '2008–{}, Scrapy developers'.format(datetime.now().year)

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
try:
    version_path = Path(__file__).parent.absolute().parent.joinpath("scrapy/VERSION")
    version = version_path.read_text().strip()
    release = version.rsplit(".", 1)[0]
except Exception:
    version = ''
    release = ''

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
language = 'en'

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
#unused_docs = []

exclude_patterns = ['build']

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = ['.build']

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# Options for HTML output
# -----------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
# Add path to the RTD explicitly to robustify builds (otherwise might
# fail in a clean Debian build env)
import sphinx_rtd_theme
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


# The style sheet to use for HTML and HTML Help pages. A file of that name
# must exist either in Sphinx' static/ path, or in one of the custom paths
# given in html_static_path.
# html_style = 'scrapydoc.css'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_use_modindex = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, the reST sources are included in the HTML build as _sources/<name>.
html_copy_source = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'Scrapydoc'


# Options for LaTeX output
# ------------------------

# The paper size ('letter' or 'a4').
#latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [
  ('index', 'Scrapy.tex', 'Scrapy Documentation',
   'Scrapy developers', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_use_modindex = True


# Options for the linkcheck builder
# ---------------------------------

# A list of regular expressions that match URIs that should not be checked when
# doing a linkcheck build.
linkcheck_ignore = [
    'http://localhost:\d+', 'http://hg.scrapy.org',
    'http://directory.google.com/'
]


# Options for the Coverage extension
# ----------------------------------
coverage_ignore_pyobjects = [
    # Contract’s add_pre_hook and add_post_hook are not documented because
    # they should be transparent to contract developers, for whom pre_hook and
    # post_hook should be the actual concern.
    r'\bContract\.add_(pre|post)_hook$',

    # ContractsManager is an internal class, developers are not expected to
    # interact with it directly in any way.
    r'\bContractsManager\b$',

    # For default contracts we only want to document their general purpose in
    # their __init__ method, the methods they reimplement to achieve that purpose
    # should be irrelevant to developers using those contracts.
    r'\w+Contract\.(adjust_request_args|(pre|post)_process)$',

    # Methods of downloader middlewares are not documented, only the classes
    # themselves, since downloader middlewares are controlled through Scrapy
    # settings.
    r'^scrapy\.downloadermiddlewares\.\w*?\.(\w*?Middleware|DownloaderStats)\.',

    # Base classes of downloader middlewares are implementation details that
    # are not meant for users.
    r'^scrapy\.downloadermiddlewares\.\w*?\.Base\w*?Middleware',

    # Private exception used by the command-line interface implementation.
    r'^scrapy\.exceptions\.UsageError',

    # Methods of BaseItemExporter subclasses are only documented in
    # BaseItemExporter.
    r'^scrapy\.exporters\.(?!BaseItemExporter\b)\w*?\.',

    # Extension behavior is only modified through settings. Methods of
    # extension classes, as well as helper functions, are implementation
    # details that are not documented.
    r'^scrapy\.extensions\.[a-z]\w*?\.[A-Z]\w*?\.',  # methods
    r'^scrapy\.extensions\.[a-z]\w*?\.[a-z]',  # helper functions

    # Never documented before, and deprecated now.
    r'^scrapy\.item\.DictItem$',
    r'^scrapy\.linkextractors\.FilteringLinkExtractor$',

    # Implementation detail of LxmlLinkExtractor
    r'^scrapy\.linkextractors\.lxmlhtml\.LxmlParserLinkExtractor',
]


# Options for the InterSphinx extension
# -------------------------------------

intersphinx_mapping = {
    'coverage': ('https://coverage.readthedocs.io/en/stable', None),
    'cssselect': ('https://cssselect.readthedocs.io/en/latest', None),
    'pytest': ('https://docs.pytest.org/en/latest', None),
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master', None),
    'tox': ('https://tox.readthedocs.io/en/latest', None),
    'twisted': ('https://twistedmatrix.com/documents/current', None),
    'twistedapi': ('https://twistedmatrix.com/documents/current/api', None),
}


# Options for sphinx-hoverxref options
# ------------------------------------

hoverxref_auto_ref = True
hoverxref_project = "scrapy"
hoverxref_version = release
