# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""
import argparse

from steppy import steps_persister
from steppy.controllers import mininova, quneo, launchcontrol, virtual
from steppy.inputs import Inputs
from steppy.list_interfaces import list_interfaces
from steppy.note import Note
from steppy.outputs import Outputs
from steppy.steps import Steps
from steppy.sequencer import Sequencer
from steppy.tempo import Tempo


def main(fpath=None):
    steps = Steps()
    if fpath is not None:
        steps_persister.load(steps, fpath)
    tempo = Tempo()
    seq = Sequencer(steps, tempo)
    mini = mininova.MiniNova(seq)
    qu = quneo.Quneo(seq)
    lc = launchcontrol.LaunchControl(seq)
    virt = virtual.Virtual(seq)
    seq.add_input_controllers(mini, qu, lc)
    seq.add_output_controllers(mini, qu, lc, virt)
    seq.set_synths(mini, virt)
    seq.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Step sequencer written in Python')
    parser.add_argument('command', nargs='?', default='go', help='list: list interfaces; load: load json dump')
    parser.add_argument('fpath', nargs='?', help='file path')
    args = parser.parse_args()
    if args.command == 'list':
        print(list_interfaces())
    elif args.command == 'load':
        fpath = args.fpath
        main(fpath)
    else:
        main()
