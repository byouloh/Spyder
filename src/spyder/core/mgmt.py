#
# Copyright (c) 2008 Daniel Truemper truemped@googlemail.com
#
# mgmt.py 10-Jan-2011
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# under the License.
#
#

import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream

from spyder.core.constants import *

class ZmqMgmt(object):
    """
    A `ZMQStream` object handling the management sockets.
    """

    def __init__(self, subscriber, publisher, **kwargs):
        """
        Initialize the management interface.

        The `subscriber` socket is the socket used by the Master to send
        commands to the workers. The publisher socket is used to send commands
        to the Master.
        """
        self._masterTopic = kwargs.get('topic', ZMQ_SPYDER_TOPIC)
        self._io_loop = kwargs.get('io_loop', IOLoop.instance())

        self._subscriber = subscriber
        self._subscriber.setsockopt(zmq.SUBSCRIBE, self._masterTopic)

        self._publisher = publisher

        self._callbacks = {}

        self._stream = ZMQStream(self._subscriber, self._io_loop)
        self._stream.on_recv( self._receive )


    def _receive(self, message):
        """
        Main method for receiving management messages.

        `message` is a multipart message where `message[0]` contains the topic,
        `message[1]` is 0 and `message[1]` contains the actual message.
        """
        topic = message[0]

        if self._callbacks.has_key( topic ):
            for cb in self._callbacks[ topic ]:
                if callable(cb):
                    cb( message )

        if message == ZMQ_SPYDER_MGMT_WORKER_QUIT:
            self._stream.stop_on_recv()
            self._publisher.send_multipart(ZMQ_SPYDER_MGMT_WORKER_QUIT_ACK)


    def addCallback(self, topic, callback):
        """
        Add a callback to the specified topic.
        """
        if not callable(callback):
            raise ValueError('callback must be callable')

        if not self._callbacks.has_key( topic ):
            self._callbacks[ topic ] = []

        self._callbacks[topic].append( callback )


