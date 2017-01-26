# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import mido


def list_interfaces():
    return 'Inputs: %s\nOutputs: %s' % \
        (mido.get_input_names(), mido.get_output_names())
