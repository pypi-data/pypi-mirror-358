# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['limepkg_scrive',
 'limepkg_scrive.translations',
 'limepkg_scrive.web_components']

package_data = \
{'': ['*']}

install_requires = \
['lime-crm>=2.526.0,<3.0.0']

entry_points = \
{'lime_plugins': ['limepkg-scrive = limepkg_scrive']}

setup_kwargs = {
    'name': 'limepkg-scrive',
    'version': '3.0.0rc0',
    'description': 'Lime CRM package',
    'long_description': 'None',
    'author': 'Author',
    'author_email': 'author@lime.tech',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
