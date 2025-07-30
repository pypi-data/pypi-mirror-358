from . import wsgi_executor
from skitai.backbone.http_response import catch
import asyncio
from skitai.utility import deallocate_was
from skitai.exceptions import HTTPError

class Executor (wsgi_executor.Executor):
    def respond_async (self, was, task):
        try:
            content = task.fetch ()
            if content and type (content) is not tuple:
                content = (content,)
                was.stream.send (*content)
        except:
            was.traceback ()
            was.stream.channel and was.stream.channel.close ()
        finally:
            was.async_executor.done ()
            deallocate_was (was)

    def is_async_executor_running (self):
        try:
            assert hasattr (self.was, "async_executor"), "async is not enabled"
        except AssertionError:
            raise HTTPError ("500 Internal Server Error", "async executor not found")

    def __call__ (self):
        self.was = self.env ["skitai.was"]
        current_app, wsfunc = self.env.get ("stream.handler")
        content = wsfunc (self.was, **self.env.get ("stream.params", {}))

        if not asyncio.iscoroutine (content):
            return content

        # async session route
        self.is_async_executor_running ()
        self.add_async_task (content)
