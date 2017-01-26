# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import pkg_resources


def discover_controllers(entry_point='steppy.controllers'):
    """Discover controllers registered under given entry point
    In:
      - ``entry_point`` - The entry point under which to register controllers (default: "steppy.controllers")
    Return:
      - A dictionary {controller name: controller class}
    """
    return {ep.name: ep.load() for ep in pkg_resources.iter_entry_points(entry_point)}
