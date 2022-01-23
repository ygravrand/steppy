StepPy: a step sequencer in Python
==================================
.. image:: https://travis-ci.org/ygravrand/steppy.svg?branch=master
   :target: https://travis-ci.org/ygravrand/steppy


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
<https://speakerdeck.com/ygravrand/build-a-step-sequencer-using-python-fosdem-17>`_ (soon on this repository).

First demo:

.. image:: http://img.youtube.com/vi/j3N0pPi5eu4/0.jpg
   :width: 320px
   :height: 240px
   :alt: "First StepPy demo"
   :align: center
   :target: https://youtu.be/j3N0pPi5eu4


Installation and usage
======================
To install the package and run StepPy:

- Install ``python``, ``virtualenv`` and make sure you have a C compiler, portmidi and python headers: e.g. ``sudo apt-get install -y git python3 python3-virtualenv libpython3-dev libportmidi-dev build-essential`` on Debian/Ubuntu
- Clone this repository and ``cd`` into it
- Create a ``virtualenv``: ``virtualenv --python=python3 .venv; source .venv/bin/activate``
- Run ``pip install -r requirements.txt`` and ``pip install -e .``
- Connect a supported controller on an USB port
- Run ``python -m steppy.main`` or ``python -m steppy.main load examples/mozart.json``

To run tests:

- Run ``pip install -e .[test]``
- Run ``py.test``


Integrated web server (experimental)
====================================

StepPy ships with an integrated ``gevent``-based web server with real time updates via Websockets.

To use this server (only works with python 2 for now):

- Install ``redis`` and ``python2`` along with other dependencies: e.g. ``sudo apt-get install -y git python virtualenv libpython-dev libportmidi-dev build-essential redis-server``
- Clone this repository: ``git clone https://github.com/ygravrand/steppy; cd steppy``
- Create a ``virtualenv``: ``virtualenv .venv2; source .venv2/bin/activate``
- Run ``pip install -e .``
- Connect a supported controller on an USB port
- Launch ``redis`` if not already launched: ``redis-server --bind 127.0.0.1 --daemonize yes``
- Run ``python -m steppy.main -s`` or ``python -m steppy.main -s load examples/mozart.json``


Troubleshooting
===============

- Run ``python -m steppy.main list``, this will list the detected inputs and outputs
- Edit ``conf/steppy.conf`` and add the corresponding names to a ``port_name`` parameter.

  For example::

    [[launchcontrol1]]
    type = launchcontrol
    port_name = Launch Control MIDI 1

- On Mac OS X, problems have been reported with system upgrades, resulting in errors like `this one <https://github.com/olemb/mido/issues/44>`_.
  A solution could be to modify ``<venv>/lib/python2.7/site-packages/mido/backends/portmidi_init.py`` to specify the absolute location of the library::


    if sys.platform == 'darwin':
        dll_name = ctypes.util.find_library('/usr/local/lib/libportmidi.dylib')

  See `this discussion <http://stackoverflow.com/questions/32905322/oserror-dlopenlibsystem-dylib-6-image-not-found>`_ for details.



Roadmap
=======
- Chords handling (especially important for a drum machine...)
- Multi track
- Load / save to midi
- External tempo sync
- Reactive Web interface (iPad, ...)
