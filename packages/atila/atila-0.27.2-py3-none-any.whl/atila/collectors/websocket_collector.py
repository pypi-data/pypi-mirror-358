from .grpc_collector import GRPCAsyncStreamCollector
from io import BytesIO
from rs4.protocols.sock.impl.ws import *
from rs4.protocols.sock.impl.ws.collector import Collector as BaseWebsocketCollector
import atila
import asyncio

class WebsocketAsyncCollector (BaseWebsocketCollector, GRPCAsyncStreamCollector):
    def __init__ (self, handler, request, *args):
        self.handler = handler
        self.request = request
        self.content_length = -1

        self.msgs = []
        self.rfile = BytesIO ()
        self.masks = b""
        self.has_masks = True
        self.buf = b""
        self.payload_length = 0
        self.opcode = None
        self.default_op_code = OPCODE_TEXT
        self.ch = self.channel = request.channel
        self.initialize_stream_variables ()
        self.mq = asyncio.Queue ()
        self.loop = asyncio.get_event_loop ()

    def collect_incoming_data (self, data):
        if not data:
            # closed connection
            self.close ()
            return

        if self.masks or (not self.has_masks and self.payload_length):
            self.rfile.write (data)
        else:
            self.buf += data

    def start_collect (self):
        self.channel.set_terminator (2)

    def handle_message (self, msg):
        self.loop.call_soon_threadsafe (self.mq.put_nowait, msg)
