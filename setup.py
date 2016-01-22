try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'web.py crust - extensions for your web.py app',
    'author': 'Jeff Zellman',
    'url': 'http://github.com/jzellman/webpy-crust',
    'download_url': 'http://github.com/jzellman/webpy-crust',
    'author_email': 'jzellman@gmail.com',
    'version': '0.0.2',
    'install_requires': ['web.py', 'nose'],
    'packages': ['crust'],
    'scripts': [],
    'name': 'webpy-crust'
}

setup(**config)
