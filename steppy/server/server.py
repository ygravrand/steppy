# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016-2017 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

import gevent
import redis

from flask import Flask, render_template
from flask_sockets import Sockets
from gevent.wsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler


# Inspired from https://github.com/heroku-examples/python-websockets-chat


class ServerBackend(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self, redis, redis_chan):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(redis_chan)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                yield data

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)


class PushingConsole(object):
    """Console pushing messages to remote WebSocket clients via Redis"""

    def __init__(self, redis, redis_chan, terse):
        self.redis = redis
        self.redis_chan = redis_chan
        self.terse = terse

    def start(self):
        pass

    def big_print(self, msg):
        self.redis.publish(self.redis_chan, msg)

    def print_(self, msg):
        if not self.terse:
            self.redis.publish(self.redis_chan, msg)


class Server(object):

    configspec = {
        'server': {
            'host': 'string(default="0.0.0.0")',
            'port': 'integer(default=8080)',
            'redis_url': 'string(default="")',
            'redis_chan': 'string(default="steppy")',
            'terse': 'boolean(default=True)'    # if True, show on the browser BIG messages only
        }
    }

    def __init__(self, config):
        self.redis = None
        self.backend = None
        if config['server'].get('redis_url'):
            self.redis = redis.from_url(config['server']['redis_url'])
            self.redis_chan = config['server']['redis_chan']
            self.backend = ServerBackend(self.redis, self.redis_chan)
        else:
            print('No redis configured, disabling Websockets and remote web console')

        self.flask_host = config['server']['host']
        self.flask_port = config['server']['port']
        self.flask_app = Flask(__name__)
        self.flask_app.add_url_rule('/', 'index', self._index)
        sockets = Sockets(self.flask_app)
        # sockets.add_url_rule('/submit', 'submit', self._inbox)
        sockets.add_url_rule('/status', 'status', self._status)
        self.console = PushingConsole(self.redis, self.redis_chan, config['server']['terse']) if self.redis else None

    def start(self):
        if self.backend:
            self.backend.start()
        gevent.spawn(self.run)

    def run(self):
        print('Remote StepPy console available on http://%s:%s/' % (self.flask_host, self.flask_port))
        http_server = WSGIServer((self.flask_host, self.flask_port), self.flask_app, handler_class=WebSocketHandler)
        http_server.serve_forever()

    def _index(self):
        return render_template('index.html')

    # Not used for now
    def _inbox(self, ws):
        """Receives incoming messages, inserts them into Redis."""
        while not ws.closed:
            # Sleep to prevent *constant* context-switches.
            gevent.sleep(0.1)
            message = ws.receive()

            if message:
                self.redis.publish(self.redis_chan, message)

    def _status(self, ws):
        print('Client connected:', ws.origin)
        self.backend.register(ws)
        self.redis.publish(self.redis_chan, 'Connected')
        while not ws.closed:
            # Context switch while `ChatBackend.start` is running in the background.
            gevent.sleep(0.1)
