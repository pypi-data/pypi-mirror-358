from . import wsgi_executor, ws_executor
import xmlrpc.client as xmlrpclib
import sys, os
import struct
from rs4 import asynchat
import threading
import copy
from rs4.protocols.sock.impl.grpc.producers import grpc_producer
from rs4.protocols.sock.impl.grpc.discover import find_input
from skitai.backbone.threaded import trigger
from skitai.handlers import collectors
from skitai import version_info, was as the_was
from types import GeneratorType
from rs4.misc.producers import grpc_iter_producer
import asyncio
import inspect

class Executor (wsgi_executor.Executor):
    def __init__ (self, env, get_method):
        wsgi_executor.Executor.__init__ (self, env, get_method)
        self.producer = None
        self.service = None
        self.num_streams = 0

    def respond_async (self, was, task):
        try:
            content = task.fetch ()
        finally:
            was.async_executor.done ()
        return grpc_producer (content, False)

    def __call__ (self):
        request = self.env ["skitai.was"].request
        collector = request.collector
        data = self.env ["wsgi.input"]
        self.input_type = find_input (request.uri [1:])

        servicefullname = self.env ["SCRIPT_NAME"][1:-1]
        methodname = self.env ["PATH_INFO"]
        sfn = servicefullname. split (".")
        packagename = ".".join (sfn [:-1])
        servicename = sfn [-1]

        self.was = self.env ["skitai.was"]
        self.was.response ["grpc-accept-encoding"] = 'identity,gzip'
        self.was.response ["content-type"] = "application/grpc+proto"
        self.was.response.set_trailer ("grpc-status", "0")
        self.was.response.set_trailer ("grpc-message", "ok")

        is_stream = self.input_type [1]
        result = b""
        try:
            current_app, self.service, param, respcode = self.find_method (request, methodname, True)
            if respcode:
                return b""

            if not isinstance (data, list):
                data.set_input_type (self.input_type)
                result = self.chained_exec (self.service, (), {})
            else:
                descriptor = []
                for m in data:
                    f = self.input_type [0]()
                    f.ParseFromString (m)
                    descriptor.append (f)
                if not is_stream:
                    descriptor = descriptor [0]
                result = self.chained_exec (self.service, (descriptor,), {})

        except:
            self.was.traceback ()
            self.was.response.set_trailer ("grpc-status", "2")
            self.was.response.set_trailer ("grpc-message", "internal error")
            self.rollback ()

        else:
            if result:
                if asyncio.iscoroutine (result [0]) and not isinstance (result [0], GeneratorType):
                    assert hasattr (self.was, "async_executor"), "async is not enabled"
                    return self.add_async_task (result [0], False)

            self.commit ()
            if hasattr (result [0], 'SerializeToString'):
                result = grpc_producer (result [0], False)
                for k, v in result.get_headers ():
                    self.was.response [k] = v
            else:
                # sync generator
                result = grpc_iter_producer (result [0])

        return result
