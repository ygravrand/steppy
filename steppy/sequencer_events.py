# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import traceback


class SequencerEvents(object):

    START = 'start'              # Global start
    STOP = 'stop'                # Global stop
    PAUSE = 'pause'              # Pause on a step
    RESUME = 'resume'            # Resume step
    STEP_BEGIN = 'step_begin'    # Beginning of a step
    STEP_END = 'step_end'        # End of a step

    def __init__(self):
        self.listeners = {}

    def on(self, event, controller, fun):
        listeners = self.listeners.setdefault(event, [])
        listeners.append((controller, fun))

    def set_event(self, event, args, enabled_controllers):
        for (controller, fun) in self.listeners.get(event, []):
            if controller in enabled_controllers:
                try:
                    fun(*args)
                except Exception as e:
                    print('Exception calling listener "%s" with arguments "%s"' %
                          (fun, args))
                    traceback.print_exc()
