try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'Lyra',
    'version': '0.1',
    'author': 'Caterina Urban',
    'author_email': 'caterina.urban@gmail.com',
    'description': 'Static Program Analyzer for Python Data Science Applications',
    'url': 'http://www.pm.inf.ethz.ch/research/lyra.html',
    'license': 'MPL-2.0',
    'packages': ['abstract_domains', 'core', 'engine', 'frontend', 'semantics', 'tests', 'z3'],
    'install_requires': [
        'graphviz==0.7.1',
        'z3',
    ],
    'scripts': [],
}

setup(**config)
