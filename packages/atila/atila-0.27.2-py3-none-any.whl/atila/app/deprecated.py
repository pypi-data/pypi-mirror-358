from functools import wraps
import os
import time, threading
import re
import inspect
import skitai
import sys
from ..events import *
from rs4.annotations import deprecated
import atila
import asyncio

class Deprecated:
    # app life cycling -------------------------------------------
    # 2021. 5. 8, integrate into evbus. use app.on ('before_mount') etc
    # 2022. 3. 27 these methods are used only by simple app mount mode
    # 2022. 4. 1 deprecated
    # 2022. 10. 1 reinstead for app testing
    # Automation ------------------------------------------------------
    @deprecated ("use @app.depends (on_request, on_response)")
    def run_before (self, *funcs):
        def decorator(f):
            self.save_function_spec (f)
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                for func in funcs:
                    response = func (was)
                    if response is not None:
                        return response
                return f (was, *args, **kwargs)
            return wrapper
        return decorator

    @deprecated ("use @app.depends (on_request, on_response)")
    def run_after (self, *funcs):
        def decorator(f):
            self.save_function_spec (f)
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                response = f (was, *args, **kwargs)
                for func in funcs:
                    func (was)
                return response
            return wrapper
        return decorator

    @deprecated ('use permission_required ([MEMBER_TYPE])')
    def staff_member_required (self, f):
        return self.permission_required (['staff']) (f)
