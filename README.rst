StepPy: a step sequencer in Python
==================================
.. image:: https://travis-ci.org/ygravrand/steppy.svg?branch=master


Using this project, one can:

- Make a MIDI device play a sequence of notes using Python
- Modify and turn notes on / off to create a sequence
- Switch between "step by step" and "live" modes
- Change tempo in real time

Abstractions allow programmers to customize the behaviour for a particular controller.

Bindings are already available for:

- Keith Mc Millen's Quneo ®
- Novation Launch Control ®
- Novation MiniNova ®
- The virtual midi bus available on Mac OS X, to connect to software sequencers

Genesis
=======
This project was demonstrated @ Pycon-Fr 2016.

The slides are available `here
<https://speakerdeck.com/ygravrand/informatique-musicale-creer-un-sequenceur-pas-a-pas-avec-python>`_ (soon on this repository).

I will soon post a demonstration video.


Installation and usage
======================
To install the package and run it:

- Run ``pip install -e .`` or ``python setup.py develop``
- Connect a supported controller on an USB port
- Run ``python -m steppy.main`` or ``python -m steppy.main load examples/mozart.json``

To run tests:

- Run ``pip install -e .[test]``
- Run ``py.test``


Roadmap
=======
- Configuration and entry points to activate controllers
- Chords handling (especially important for a drum machine...)
- Multi track
- Load / save to midi
- External tempo sync
- Reactive Web interface (iPad, ...)
