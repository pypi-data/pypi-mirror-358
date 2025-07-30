import os
from ..exceptions import HTTPError

hub = None
IGNORE_HTTP_ERROR = True

try:
    import sentry_sdk
    from sentry_sdk.hub import Hub
    hub = Hub.current
except ImportError:
    pass
else:
    def init (**config):
        sentry_sdk.init (**config)

    def __error__ (context, app, exc_info):
        if hub is None or hub.client is None:
            return

        ctxs = {}
        if isinstance (exc_info [1], HTTPError):
            if IGNORE_HTTP_ERROR:
                return
            httpe = exc_info [1]
            if not httpe.explain:
                return # not important error
            try:
                status_code = int (httpe.status [:3])
            except ValueError:
                return
            if status_code < 400:
                return

            ctxs ['response information'] = dict (
                http_status = httpe.status,
                message = httpe.explain,
                code = httpe.errno
            )

        user = {}
        if context.request.user:
            user ['user'] = str (context.request.user)
            try: user ['name'] = context.request.user.name
            except AttributeError: pass
            try: user ['uid'] = context.request.user.uid
            except AttributeError:
                try: user ['uid'] = context.request.user.id
                except AttributeError:
                    pass
            try: user ['email'] = context.request.user.email
            except AttributeError: pass

        if context.request.args:
            request_args = {}
            if isinstance (context.request.args, dict):
                for k, v in context.request.args.items ():
                    if hasattr (v, 'path'):
                        request_args [k] = v.path
                        continue
                    request_args [k] = v
            else:
                request_args = {'__value__': context.request.args}
            ctxs ['request args'] = request_args

        request_header = {}
        for k, v in context.request.headers.items ():
            if k.lower () in ('authorization', 'cookie'):
                    continue
            request_header [k] = v

        ctxs ['request header'] = request_header
        capture_exception (exc_info, contexts = ctxs, user = user, tags = {"context": "request"})


def capture_exception (exc_info, contexts = None, tags = None, user = None):
    if hub is None or hub.client is None:
        return

    with sentry_sdk.push_scope () as scope:
        if user:
            scope.user = user
        for name, value in (tags or {}).items ():
            scope.set_tag (name, value)
        for name, ctx in (contexts or {}).items ():
            scope.set_context (name, ctx)
        sentry_sdk.capture_exception (exc_info)