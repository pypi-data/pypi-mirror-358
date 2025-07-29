# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['orchestra',
 'orchestra._internals',
 'orchestra._internals.common',
 'orchestra._internals.common.models',
 'orchestra._internals.elements',
 'orchestra._internals.rpc',
 'orchestra._internals.rpc.orchestra',
 'orchestra._internals.watcher',
 'orchestra.elements',
 'orchestra.elements.models',
 'orchestra.models']

package_data = \
{'': ['*']}

install_requires = \
['bson>=0.5.10,<0.6.0',
 'futurist>=2.4.1,<3.0.0',
 'grpcio>=1.56.0,<2.0.0',
 'orjson>=3.9.1,<4.0.0',
 'protobuf>=4.23.3,<5.0.0',
 'pydantic[dotenv]>=1.10.9,<2.0.0']

setup_kwargs = {
    'name': 'cthingsco-orchestra',
    'version': '0.4.4',
    'description': 'Orchestra SDK and bindings for Python.',
    'long_description': 'Orchestra\n=========\n\n**Orchestra** is a Python library for easy integration with CTHINGS.CO® Orchestra\'s IoT "Element" Twin and Telemetry functionalities.\n',
    'author': 'CTHINGS.CO',
    'author_email': 'contact@cthings.co',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
