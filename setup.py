"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from setuptools import setup, find_packages

setup(
    name='steppy',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['mido', 'gevent', 'pyfiglet'],
    extras_require={
        'test': ['pytest', 'tox']
    }
)
