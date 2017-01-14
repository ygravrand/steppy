# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

from controllers import discover_controllers


class ControllersConfig(object):
    """Controllers configurator for steppy:
      - Loads controllers and io configuration
      - Finds controllers from entry points
      - Creates controller instances
      - Stores them into ``inputs``, ``outputs``, ``synths`` lists
    """

    configspec = {
        'controllers': {
            '__many__':
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

    def __init__(self, config):
        self.config = config
        self.inputs = []
        self.outputs = []
        self.synths = []

    def init_controllers(self, sequencer):
        controllers = {}
        controllers_dict = discover_controllers()
        for (cont_name, cont_config) in self.config['controllers'].items():
            if cont_config['type'] in controllers_dict:
                controllers[cont_name] = self._create_controller(
                    controllers_dict[cont_config['type']],
                    cont_config,
                    sequencer
                )
            else:
                print('Unknown controller type: "%s". Please check "steppy.controllers" entry points' % cont_config['type'])
        self.inputs = self._get_ios(controllers, 'inputs')
        self.outputs = self._get_ios(controllers, 'outputs')
        self.synths = self._get_ios(controllers, 'synths')

    def _create_controller(self, controller_class, controller_config, sequencer):
        if controller_config['port_name'] is not None:
            args = (controller_config['port_name'],)
        else:
            args = ()
        return controller_class(sequencer, *args)

    def _get_ios(self, controllers, io_type):
        res = []
        for io in self.config['io'][io_type]:
            if io in controllers:
                res.append(controllers[io])
            else:
                print('Unknown %s type: "%s"' % (io_type, io))
        return res
