try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'web.py-crust - Various extensions and niceties for web.py',
    'author': 'Jeff Zellman',
    'url': 'http://github.com/jzellman/webpy-crust',
    'download_url': 'http://github.com/jzellman/webpy-crust',
    'author_email': 'jzellman@gmail.com',
    'version': '0.0.3',
    'install_requires': [],
    'packages': ['crust'],
    'scripts': [],
    'name': 'webpy-crust'
}

setup(**config)
