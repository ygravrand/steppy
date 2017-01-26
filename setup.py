"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from setuptools import setup, find_packages

setup(
    name='steppy',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['configobj', 'mido', 'gevent', 'pyfiglet'],
    extras_require={
        'test': ['pytest', 'tox']
    },
    entry_points={
        'steppy.controllers': [
            'launchcontrol = steppy.controllers.launchcontrol:LaunchControl',
            'mininova = steppy.controllers.mininova:MiniNova',
            'quneo = steppy.controllers.quneo:Quneo',
            'virtual = steppy.controllers.virtual:Virtual'
        ]
    }
)
