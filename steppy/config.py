# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""
import os
import pkg_resources

from configobj import ConfigObj
from validate import Validator


class Config(object):
    """Configuration object for steppy:
    - Loads configuration
    - Finds controllers from entry points
    - Instanciates controllers
    - Stores them into ``inputs``, ``outputs``, ``synths`` lists
    """

    spec = {
        'controllers':
            {'__many__':
                {
                    'type': 'string',
                    'port_name': 'string(default=None)'
                }
            },
        'io': {
            'inputs': 'list(default=list())',
            'outputs': 'list(default=list())',
            'synths': 'list(default=list())'
        }
    }

    def __init__(self, sequencer, filepath=None):
        if filepath is None:
            filepath = pkg_resources.resource_stream(
                                    __name__,
                                    os.path.join('..','conf', 'steppy.conf')
                                    )
        else:
            filepath = os.path.abspath(filepath)
            print('Using config file %s' % filepath)
        config = self.parse_config(filepath)
        self.controllers = self.get_controllers_from_config(sequencer, config)
        self.inputs = self.get_ios_from_config(config, 'inputs')
        self.outputs = self.get_ios_from_config(config, 'outputs')
        self.synths = self.get_ios_from_config(config, 'synths')
        # print 'Controllers:', self.controllers
        # print 'Inputs:', self.inputs
        # print 'Outputs:', self.outputs
        # print 'Synths:', self.synths

    def parse_config(self, filepath):
        config = ConfigObj(filepath, configspec=self.spec)
        config.validate(Validator())
        return config

    def discover_controllers(self):
        """Discover controllers registered under entry point ``steppy.controllers``
        Return:
          - A dictionary {controller name: controller class}
        """
        return {ep.name: ep.load() for ep in pkg_resources.iter_entry_points('steppy.controllers')}

    def get_controllers_from_config(self, sequencer, config):
        controllers = {}
        controllers_dict = self.discover_controllers()
        for (cont_name, cont_config) in config['controllers'].items():
            if cont_config['type'] in controllers_dict:
                controllers[cont_name] = self.instanciate_controller(
                    controllers_dict[cont_config['type']],
                    cont_config,
                    sequencer
                )
            else:
                print('Unknown controller type: "%s". Please check "steppy.controllers" entry points' % cont_config['type'])
        return controllers

    def instanciate_controller(self, controller_class, controller_config, sequencer):
        if controller_config['port_name'] is not None:
            args = (controller_config['port_name'],)
        else:
            args = ()
        return controller_class(sequencer, *args)

    def get_ios_from_config(self, config, io_type):
        res = []
        for io in config['io'][io_type]:
            if io in self.controllers:
                res.append(self.controllers[io])
            else:
                print('Unknown %s type: "%s"' % (io_type, io))
        return res
