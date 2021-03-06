# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""
import argparse

from steppy import steps_persister
from steppy.configurator import Configurator
from steppy.console import Console
from steppy.controllers_config import ControllersConfig
from steppy.list_interfaces import list_interfaces
from steppy.steps import Steps
from steppy.sequencer import Sequencer
from steppy.server import Server
from steppy.tempo import Tempo


def main(fpath=None, server=False, configfile=None):
    tempo = Tempo()

    configurator = Configurator(configfile)
    configurator.add_configurable(Server)
    configurator.add_configurable(Console)
    configurator.add_configurable(ControllersConfig)
    config = configurator.configure()

    if server:
        server = Server(config)
        console = server.console or Console(config)
    else:
        server = None
        console = Console(config)
    steps = Steps(console)
    if fpath is not None:
        steps_persister.load(steps, fpath)

    seq = Sequencer(server, console, steps, tempo, ControllersConfig(config))

    seq.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Step sequencer written in Python')
    parser.add_argument('command', nargs='?', default='go', help='list: list interfaces; load: load json dump')
    parser.add_argument('fpath', nargs='?', help='file path')
    parser.add_argument('-c', '--config', help='Configuration file')
    parser.add_argument('-s', '--server', action='store_true', help='Launch server (needs redis)')
    args = parser.parse_args()
    if args.command == 'list':
        print(list_interfaces())
    elif args.command == 'load':
        fpath = args.fpath
        main(fpath, server=args.server, configfile=args.config)
    else:
        main(server=args.server, configfile=args.config)
