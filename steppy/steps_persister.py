# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import json
import tempfile

from .note import Note
from .steps import Step


def load(steps, fpath):
    with open(fpath, 'r') as f:
        data = json.loads(f.read())
    steps.steps = [Step(Note(numeric_note=s['numeric_note'],
                             velocity=s['velocity'],
                             duration=s['duration'],
                             channel=s['channel']) if s['note'] else None,
                        on=s['on'], pos=i) for i, s in enumerate(data)]
    print('Loaded from', fpath)


def save(steps, fpath=None):
    if fpath is None:
        fpath = tempfile.mktemp()
    res = []
    with open(fpath, 'w') as f:
        for step in steps.steps:
            dict_ = {'on': step.on, 'note': step.note is not None}
            if step.note:
                dict_['numeric_note'] = step.note.note
                dict_['velocity'] = step.note.velocity
                dict_['duration'] = step.note.duration
                dict_['channel'] = step.note.channel
            res.append(dict_)
        f.write(json.dumps(res))
    print('Saved to', fpath)
