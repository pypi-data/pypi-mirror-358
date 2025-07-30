from .stream_collector import StreamCollector
from skitai.handlers.collectors import FormCollector
from skitai import counter
import struct
import time
import asyncio
from rs4.misc import compressors
import threading
import sys

class GRPCCollector (FormCollector):
    stream_id = counter.counter ()
    def __init__ (self, handler, request, *args):
        super ().__init__ (handler, request, *args)
        self.ch = request.channel
        self.stream_id.inc ()
        self._compressed = None
        self._decompressor = compressors.GZipDecompressor ()
        self._msg_length = 0
        self.buffer = b""
        self.msgs = []

    def close (self):
        self.handler.continue_request (self.request, self.msgs)

    def start_collect (self):
        self.ch.set_terminator (1)

    def collect_incoming_data (self, data):
        self.buffer += data

    def handle_message (self, msg):
        self.msgs.append (msg)

    def found_terminator (self):
        if not self.buffer:
            self.close ()
            return

        buf, self.buffer = self.buffer, b""
        if self._compressed is None:
            self._compressed = struct.unpack ("!B", buf)[0]
            self.ch.set_terminator (4)

        elif self._msg_length == 0:
            self._msg_length = struct.unpack ("!I", buf)[0]
            if self._msg_length:
                self.ch.set_terminator (self._msg_length)
            else:
                self.ch.set_terminator (1)
                self._compressed = None

        else:
            if self._compressed:
                buf = self._decompressor.decompress (buf) + self._decompressor.flush ()
            self._compressed = None
            self._msg_length = 0
            self.handle_message (buf)
            self.ch.set_terminator (1)


class GRPCAsyncStreamCollector (GRPCCollector, StreamCollector):
    DEFAULT_BUFFER_SIZE = 1
    END_DATA = None
    stream_id = counter.counter ()

    def __init__ (self, handler, request, *args):
        GRPCCollector.__init__ (self, handler, request, *args)
        self.initialize_stream_variables ()
        self.input_type = None
        self.mq = asyncio.Queue ()
        self.loop = asyncio.get_event_loop ()

    def set_input_type (self, input_type):
        self.input_type = input_type

    def is_input_stream (self):
        return self.input_type [1]

    async def get (self):
        return await self.mq.get ()

    def start_collect (self):
        self.request.channel.set_terminator (1)

    def handle_message (self, msg):
        f = self.input_type [0]()
        f.ParseFromString (msg)
        self.loop.call_soon_threadsafe (self.mq.put_nowait, f)

    def close (self):
        if self.closed:
            return
        self.request.collector = None
        self.loop.call_soon_threadsafe (self.mq.put_nowait, None)
        self.closed = True

