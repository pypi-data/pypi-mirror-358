from datetime import datetime
import unike as package

pkg_name = package.__name__
pkg_file = package.__file__
pkg_version = package.__version__

project = 'UniKE'
author = 'CPU-DS'
copyright = f'2024-{datetime.now().year}, {author}'

github_user = author
github_repo = 'UniKE'
github_version = 'main'

github_url = f'https://github.com/{github_user}/{github_repo}/'
gh_page_url = f'https://github.com/CPU-DS'
# gh_page_url = f'https://{github_user}.github.io/{github_repo}/'

html_baseurl = gh_page_url
html_context = {
    'display_github': True,
    'github_user': github_user,
    'github_repo': github_repo,
    'github_version': github_version,
    "conf_py_path": "/docs/",
}

html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'display_version': True,
    
    'github_url': github_url,
    # 'github_url': gh_page_url,

    'doc_items': {
        'AD-KGE': 'https://github.com/CPU-DS/AD-KGE',
        'UniKE': 'https://unike.readthedocs.io/zh-cn/latest/',
    },

    'logo': '',
    'logo_dark': '_static/images/logo-dark.png',
    'logo_icon': '',
}

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_gallery.gen_gallery',
    'sphinx_copybutton',
    'sphinxcontrib.jquery',
    'sphinxcontrib.bibtex',
    'sphinx-prompt',
    'sphinx.ext.mathjax',
    'sphinxcontrib.katex',
]

sphinx_gallery_conf = {
     'examples_dirs': ['../examples'],
     'gallery_dirs': ['examples'],
}

autosummary_generate = True
bibtex_bibfiles = ['refs.bib']

autodoc_mock_imports = ['torch', 'dgl', 'numpy', 'tqdm', 'wandb', 'accelerate']

intersphinx_mapping = {
    'rtd': ('https://docs.readthedocs.io/en/stable/', None),
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'torch': ('https://pytorch.org/docs/stable/', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'dgl': ('https://docs.dgl.ai/', None),
}

intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

epub_show_urls = 'footnote'

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'trojanzoo_sphinx_theme'

html_static_path = ['_static']

language = 'zh'