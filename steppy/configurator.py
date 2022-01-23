# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""
import os
import pkg_resources

from configobj import ConfigObj
from configobj.validate import Validator


class Configurator(object):
    """Modular configurator for steppy"""

    spec = {}

    def __init__(self, filepath=None):
        if filepath is None:
            filepath = pkg_resources.resource_stream(
                __name__,
                os.path.join('..', 'conf', 'steppy.conf')
            )
        else:
            filepath = os.path.abspath(filepath)
            print('Using config file %s' % filepath)
        self.filepath = filepath

    def add_configurable(self, clazz):
        if clazz and clazz.configspec:
            print('Adding ``%s`` to configuration...' % clazz.__name__)
            self.spec.update(clazz.configspec)

    def configure(self):
        config = ConfigObj(self.filepath, configspec=self.spec)
        config.validate(Validator())
        return config
