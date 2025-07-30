# Primitive Task Definition

from rs4.protocols.sock.impl.ws import *
from ..exceptions import HTTPError
from skitai.utility import make_pushables
import sys
from ..wastuff.api import API
from rs4.protocols.sock.impl.ws import *
import inspect
from . import utils

DEFAULT_TIMEOUT = 30

class Revoke:
    pass


def postprocessing (was, content = None, expt = None):
    try:
        f = was.request.postprocessing
    except AttributeError:
        pass
    else:
        f and f (was, content, expt)

def add_async_generator (was, asyncgen):
    async def wrap_asyncgen ():
        was.stream = True # IMP: set cloned was
        response = was.response
        channel = response.request.channel
        expt = None
        content_len = 0
        if response.get_header ('content-type') is None:
            response.set_header ('Content-Type', 'text/html')
        response.set_header ('Transfer-Encoding', 'chunked')
        channel.push (response.build_reply_header ().encode ())

        try:
            async for data in asyncgen:
                if isinstance (data, str):
                    data = data.encode ()
                _dlen = len (data)
                content_len += _dlen
                channel.push (('%x' % _dlen).encode ("utf8") + b"\r\n" + data + b'\r\n')
        except:
            expt = sys.exc_info ()
            was.traceback ()

        postprocessing (was, None, expt)
        channel.push (b'0\r\n\r\n')
        response.log (content_len)
        channel.current_request = None
        channel.set_terminator (b"\r\n\r\n")

    return was.async_executor.put ((
        was,
        wrap_asyncgen (),
        lambda x, y: None,
        was.request.postprocessing if hasattr (was.request, 'postprocessing') else None,
        False
    ))


class Task:
    # basic methods --------------------------------------
    def get_timeout (self):
        return self._timeout

    def set_timeout (self, timeout):
        self._timeout = timeout

    def returning (self, returning):
        # coreauest.then (callback).returning ("201 Created")
        return returning

    # implementables --------------------------------------
    def then (self, func, was):
        # usally return self and chaing with returning ()
        raise NotImplementedError

    def cache (self, cache = 60, cache_if = (200,)):
        raise NotImplementedError

    def dispatch (self, cache = None, cache_if = (200,), timeout = None):
        # response object with data
        raise NotImplementedError

    def wait (self, timeout = None):
        # response object without data
        raise NotImplementedError

    def commit (self, timeout = None):
        # return None. if error had been occured will be raised
        raise NotImplementedError

    def fetch (self, cache = None, cache_if = (200,), timeout = None):
        # return data. if error had been occured will be raised
        raise NotImplementedError

    def one (self, cache = None, cache_if = (200,), timeout = None):
        # return data with only one element. if error had been occured will be raised
        raise NotImplementedError

    def _get_was (self):
        _was = utils.get_cloned_context (self.meta ['__was_id'])
        _was.request.postprocessing = self.meta ['__after_request_async']
        if "coro" in self.meta: # deciving `was` object
            utils.deceive_context (_was, self.meta ["coro"])
        return _was

    def _late_respond (self, tasks_or_content):
        if hasattr (self._was, 'stream'):
            self._fulfilled (self._was, tasks_or_content)
            return

        # NEED self._fulfilled and self._was
        if not hasattr (self._was, 'response'):
            # already responsed: SEE app2.map_in_thread
            return

        response = self._was.response
        content = None
        expt  = None

        try:
            if self._fulfilled == 'self':
                content = tasks_or_content.fetch ()
            else:
                content = self._fulfilled (self._was, tasks_or_content)
            self._fulfilled = None

        except MemoryError:
            raise

        except HTTPError as e:
            response.start_response (e.status)
            content = content or response.build_error_template (e.explain or (self._was.app.debug and e.exc_info), e.errno, was = self._was)
            expt = sys.exc_info ()

        except:
            self._was.traceback ()
            response.start_response ("500 Application Error")
            content = content or response.build_error_template (self._was.app.debug and sys.exc_info () or None, 0, was = self._was)
            expt = sys.exc_info ()

        if isinstance (content, API) and self._was.env.get ('ATILA_SET_SEPC'):
            content.set_spec (self._was.app)

        if inspect.isasyncgen (content):
            return add_async_generator (self._was, content)

        will_be_push = make_pushables (response, content)
        if will_be_push is None:
            return # future
        postprocessing (self._was, content, expt)


class response (Task):
    pass
