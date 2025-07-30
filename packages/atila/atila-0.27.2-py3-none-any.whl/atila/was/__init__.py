import os
import time
from hmac import new as hmac
from hashlib import sha1, sha256, md5
import base64
import pickle
import random
import tempfile
from rs4 import pathtool
from rs4 import asyncore
from rs4.misc import producers
from rs4.webkit import jwt, otp
from rs4.protocols.sock.impl.http import http_date
from rs4.protocols.sock.impl.smtp import composer
from skitai import wsgiappservice
from skitai.tasks import utils
from skitai.exceptions import HTTPError
import uuid
from functools import partial
from skitai import DEFAULT_BACKGROUND_TASK_TIMEOUT
from skitai.tasks.derivations import Mask, Tasks
from skitai.tasks.pth import sp_task
from skitai.backbone import http_request, http_response
from .. import cookie, session, mbox
from .output_stream import OutputStream
from .piped_process import PipedProcess
from ..executors.wsgi_executor import after_request_async
from ..import Atila

composer.Composer.SAVE_PATH = os.path.join ("/var/tmp/skitai", "smtpda", "spool")
pathtool.mkdir (composer.Composer.SAVE_PATH)

if os.name == "nt":
    TEMP_DIR = os.path.join (tempfile.gettempdir(), "skitai-gentemp")
else:
    TEMP_DIR = "/var/tmp/skitai/__gentemp"
pathtool.mkdir (TEMP_DIR)


class WAS (wsgiappservice.WAS):
    # mehods remap ------------------------------------------------
    def __init__ (self, *args, **kwargs):
        self.app: Atila
        self.request: http_request.http_request
        self.response: http_response.http_response
        self.cookie: cookie.Cookie
        self.mbox: mbox.MessageBox
        self.session: session.Session
        super ().__init__ (*args, **kwargs)

    def __getattr__ (self, name):
        if self.in__dict__ ("app"): # atila app
            attr = self.app.create_on_demand (self, name)
            if attr:
                setattr (self, name, attr)
                return attr

        try:
            return self.objects [name]
        except KeyError:
            raise AttributeError ("'was' hasn't attribute '%s'" % name)

    def make_uid (self, s = None):
        if s is None:
            s = str (uuid.uuid4 ())
        return base64.encodebytes (md5 (s.encode ()).digest ()) [:-3].decode ().replace ('/', '-').replace ('+', '.')

    # Utilities -------------------------------------------------
    @property
    def tempfile (self):
        return self.gentemp ()

    @property
    def flashfile (self):
        return pathtool.FlashFile (self.gentemp ())

    def traceback_info (self, exc_info = None):
        (file, fun, line), t, v, tbinfo = asyncore.compact_traceback (exc_info)
        try:       v = str (v)
        except:    v = repr (v)
        return "%s %s Traceback: %s" % (t, v, tbinfo)

    def gentemp (self):
        return os.path.join (TEMP_DIR, next (tempfile._get_candidate_names()))

    def email (self, subject, snd, rcpt):
        return composer.Composer (subject, snd, rcpt)
    Email = email

    # URL builders -------------------------------------------------
    def _resolve_app (self, thing):
        if isinstance (thing, str):
            if thing.find ("|") != -1:
                name, thing = thing.split ("|", 1)
                app = self.apps [name]
                return app, thing
        return self.app, thing

    def static (self, path):
        app, path = self._resolve_app (path)
        return app.static (path)

    def media (self, path):
        app, path = self._resolve_app (path)
        return app.media (path)

    def reroute (self, thing, *args, **kargs):
        app, thing = self._resolve_app (thing)
        return app.reroute (thing) (self, *args, **kargs)
    pipe = call = route = reroute

    def urlfor (self, thing, *args, **karg):
        # override with resource default args
        app, thing = self._resolve_app (thing)
        return app.urlfor (thing, *args, **karg)
    ab = urlfor

    def urlpatch (self, thing, **karg):
        # override with current args
        defaults = self.request.PARAMS
        defaults.update (self.request.URL)
        karg ["__defaults__"] = defaults
        return self.urlfor (thing, **karg)
    partial = urlpatch

    def baseurl (self, thing):
        # resource path info without parameters
        return self.urlfor (thing, __resource_path_only__ = True)
    basepath = baseurl

    def urlspec (self, thing):
        # resource path info without parameters
        return self.urlfor (thing, __resource_spec_only__ = True)

    def validate (self, **krags):
        self.app.validate (self.request, **krags)

    # event -------------------------------------------------
    def broadcast (self, event, *args, **kargs):
        return self.apps.bus.emit (event, self, *args, **kargs)
    emit = broadcast

    # passowrd en/decrypt -----------------------------------
    def encrypt_password (self, password):
        salt = base64.b64encode(os.urandom (16))
        dig = hmac (password.encode (), salt, sha256).digest()
        signature = base64.b64encode (dig)
        return salt.decode (), signature.decode ()

    def verify_password (self, password, salt, signature):
        dig = hmac (password.encode (), salt.encode (), sha256).digest()
        signature_ = base64.b64encode (dig).decode ()
        return signature == signature_

    # JWT token --------------------------------------------------
    def encode_jwt (self, claim, salt = None, alg = "HS256"):
        assert "exp" in claim, "exp claim required"
        return jwt.gen_token (salt or self.app.salt, claim, alg)

    def decode_jwt (self, token = None, salt = None):
        return self.request.dejwt (token, salt or self.app.salt)
    mkjwt = encode_jwt
    dejwt = decode_jwt

    # otp ---------------------------------------------------
    def generate_otp (self, salt = None):
        return otp.generate (salt or self.app.salt)

    def verify_otp (self, otp_, salt = None):
        return otp.verify (otp_, salt or self.app.salt)

    # onetime token  ----------------------------------------
    def _unserialize_token (self, string):
        def adjust_padding (s):
            paddings = 4 - (len (s) % 4)
            if paddings != 4:
                s += ("=" * paddings)
            return s

        string = string.replace (" ", "+")
        try:
            base64_hash, data = string.split('?', 1)
        except ValueError:
            return
        client_hash = base64.b64decode(adjust_padding (base64_hash))
        data = base64.b64decode(adjust_padding (data))
        mac = hmac (self.app.salt, None, sha1)
        mac.update (data)
        if client_hash != mac.digest():
            return
        return pickle.loads (data)

    def encode_ott (self, obj, timeout = 1200, session_key = None):
        wrapper = {
            'object': obj,
            'timeout': timeout and time.time () + timeout or 0
        }
        if session_key:
            assert timeout, 'session ott require timeout'
            token = hex (random.getrandbits (64))
            tokey = '_{}_token'.format (session_key)
            wrapper ['_session_token'] = (tokey, token)
            self.session.mount (session_key, session_timeout = timeout)
            self.session [tokey] = token
            self.session.mount ()

        data = pickle.dumps (wrapper, 1)
        mac = hmac (self.app.salt, None, sha1)
        mac.update (data)
        return (base64.b64encode (mac.digest()).strip().rstrip (b'=') + b"?" + base64.b64encode (data).strip ().rstrip (b'=')).decode ("utf8")

    def decode_ott (self, string):
        wrapper = self._unserialize_token (string)
        if not wrapper:
            return

        # validation with session
        tokey = None
        has_error = False
        timeout = wrapper ['timeout']
        if timeout and timeout  < time.time ():
            has_error = True

        if not has_error:
            session_token = wrapper.get ('_session_token')
            if session_token:
                # verify with session
                tokey, token = session_token
                self.session.mount (tokey [1:-6])
                if token != self.session.get (tokey):
                    has_error = True

        if has_error:
            if tokey:
                del self.session [tokey]
                self.session.mount ()
            return

        elif tokey:
            self.session.mount ()

        obj = wrapper ['object']
        return obj

    def revoke_ott (self, string):
        # revoke token
        wrapper = self._unserialize_token (string)
        session_token = wrapper.get ('_session_token')
        if not session_token:
            return
        tokey, token = session_token
        self.session.mount (tokey [1:-6])

        if not self.session.get (tokey):
            self.session.mount ()
            return
        del self.session [tokey]
        self.session.expire ()
        self.session.mount ()

    mktoken = token = mkott = encode_ott
    rmtoken = rvott = revoke_ott
    detoken = deott = decode_ott

    # CSRF token ------------------------------------------------------
    CSRF_NAME = "XSRF_TOKEN" #axios compat
    @property
    def csrf_token (self):
        if self.CSRF_NAME in self.cookie:
            self.cookie.remove (self.CSRF_NAME)

        if self.CSRF_NAME not in self.session:
            if self.app.debug:
                tok = '755f2ce13fd3673335d3d21a277359ad'
            else:
                tok = hex (random.getrandbits (128)) [2:]
            self.session [self.CSRF_NAME] = tok
        return self.session [self.CSRF_NAME]

    @property
    def csrf_token_input (self):
        return '<input type="hidden" name="{}" value="{}">'.format (self.CSRF_NAME, self.csrf_token)

    def generate_csrf (self):
        return self.csrf_token

    def remove_csrf (self):
        try:
            del self.session [self.CSRF_NAME]
        except KeyError:
            pass

    def verify_csrf (self, keep = True):
        token = self.request.get_header ('X-{}'.format (self.CSRF_NAME.replace ("_", "-")), self.request.args.get (self.CSRF_NAME))
        if not token:
            return False
        if self.csrf_token == token:
            if not keep:
                del self.session [self.CSRF_NAME]
            return True
        return False
    csrf_verify = verify_csrf

    # async helers -----------------------------------------------
    def to_thread (self, target, *args, **kargs):
        return self.async_executor.loop.run_in_executor (self.thread_executor, target, *args, **kargs)

    def to_process (self, target, *args, **kargs):
        return self.async_executor.loop.run_in_executor (self.process_executor, target, *args, **kargs)


    # response shortcuts -----------------------------------------------
    REDIRECT_TEMPLATE =  (
        "<html><head><title>%s</title></head>"
        "<body><h1>%s</h1>"
        "This document may be found "
        '<a HREF="%s">here</a></body></html>'
    )
    def redirect (self, url, status = "302 Object Moved", body = None, headers = None):
        val = url.split (" ", 1) [0]
        if len (val) == 3 and val.isdigit () and not status.startswith ("302 "):
            temp = url
            url, status = status, temp

        redirect_headers = [
            ("Location", url),
            ("Cache-Control", "max-age=0"),
            ("Expires", http_date.build_http_date (time.time ()))
        ]
        if isinstance (headers, dict):
            headers = list (headers.items ())
        if headers:
            redirect_headers += headers
        if not body:
            body = self.REDIRECT_TEMPLATE % (status, status, url)
        return self.response (status, body, redirect_headers)

    def render (self, template_file, _do_not_use_this_variable_name_ = {}, **karg):
        try:
            return self.app.render (self, template_file, _do_not_use_this_variable_name_, **karg)
        except:
            if self.request.channel:
                raise
            return ''

    def Fault (self, *args, **karg):
        fault = self.response.Fault (*args, **karg)
        try: fault.set_json_encoder (self.app.config.get ("JSON_ENCODER"))
        except AttributeError: pass
        return fault

    def HttpError (self, status = "200 OK", more_info = "", errno = 0, traceback = False):
        return HTTPError (status, more_info, errno, traceback)
    Error = HttpError # lower version compat

    # response extensions --------------------------------------------
    def File (self, *args, **karg):
        return self.response.File (*args, **karg)

    def MountedFile (self, uri):
        return self.request.static_file_translator.translate (self.request, uri)

    def Static (self, uri):
        return self.MountedFile (self.static (uri))

    def Media (self, uri):
        return self.MountedFile (self.media (uri))

    def WebSocketPipedProcess (self, command):
        return PipedProcess (self.stream, command)

    def PipedProcess (self, command, fp):
        return PipedProcess (fp, command)

    def Queue (self, producer, max_size = 8, wait_timeout = 8, use_thread_pool = False):
        thread_pool = use_thread_pool and self.thread_executor or None
        return producers.thread_producer (producer, max_size, wait_timeout, thread_pool)

    # API responses ------------------------------------
    def API (self, *args, **karg):
        self.response.append_header ("Vary", "Accept")
        api = self.response.API (*args, **karg)
        try: api.set_json_encoder (self.app.config.get ("JSON_ENCODER"), self.app.config.get ('PRETTY_JSON', False))
        except AttributeError: pass
        return api

    def render_or_API (self, template_file, _do_not_use_this_variable_name_ = {}, **karg):
        self.response.append_header ("Vary", "Accept")
        if self.request.acceptable ('application/json'):
            return self.API (None, _do_not_use_this_variable_name_, **karg)
        return self.render (template_file, _do_not_use_this_variable_name_ = {}, **karg)

    # Map responses ------------------------------------
    def _mapped_callback (self, was, tasks, status, template_file = None):
        data = tasks.dict (was)
        if template_file:
            return was.render_or_API (template_file, data)
        else:
            return was.API (status, data)

    def _make_tasks (self, mutations, **dispatchables):
        meta = {}
        for k in list (dispatchables.keys ()):
            if k [:2] == '__':
                meta [k [2:]] = dispatchables.pop (k)
        return self.Tasks (mutations, timeout = meta.get ('timeout', 10), meta = meta, **dispatchables)

    def create_output_stream (self, handler, use_thread_pool = False):
        return OutputStream (self, handler, use_thread_pool)

    def Input (self, max_buffer_size = 8192):
        self.env ['wsgi.input'].set_max_buffer_size (max_buffer_size)
        return self.env ['wsgi.input']
    read_input_stream = Input

    def Mapped (self, *tasks):
        try:
            status, tasks = tasks
        except ValueError:
            status, tasks = "200 OK", tasks [0]
        respfunc = partial (self._mapped_callback, status = status)
        return tasks.then (respfunc)

    def render_or_Mapped (self, template_file, tasks):
        self.response.append_header ("Vary", "Accept")
        respfunc = partial (self._mapped_callback, status = '200 OK', template_file = template_file)
        return tasks.then (respfunc)

    def Map (self, *mutations, **dispatchables):
        status = "200 OK"
        if mutations and isinstance (mutations [0], str):
            status, mutations = mutations [0], mutations [1:]
        tasks = self._make_tasks (mutations, **dispatchables)
        respfunc = partial (self._mapped_callback, status = status)
        return tasks.then (respfunc)

    def render_or_Map (self, template_file, *mutations, **dispatchables):
        self.response.append_header ("Vary", "Accept")
        tasks = self._make_tasks (mutations, **dispatchables)
        respfunc = partial (self._mapped_callback, status = '200 OK', template_file = template_file)
        return tasks.then (respfunc)

    # tasks ------------------------------------------------
    def _set_was_id (self, meta):
        meta = meta or {}
        meta ['__was_id'] = self.ID
        meta ["__after_request_async"] = after_request_async
        return meta

    def _set_postprocessor (self, kargs):
        if "meta" not in kargs:
            kargs ["meta"] = {}
        if "__after_request_async" not in kargs ["meta"]:
            kargs ["meta"]["__after_request_async"] = after_request_async
        return kargs

    def _insert_cloned_was (self, args, kargs):
        _was = utils.get_cloned_context (self.ID)
        _was.request.postprocessing = after_request_async
        if args:
            args = (_was,) + args
        else:
            kargs ['args'] = (_was,) + kargs.get ('args', ())
        return _was, args, kargs

    def Tasks (self, *reqs, timeout = 10, meta = None, **kreqs):
        keys = []
        reqs_ = []
        if reqs and isinstance (reqs [0], (list, tuple)):
            reqs = reqs [0]

        for k, v in kreqs.items ():
            keys.append (k)
            reqs_.append (v)
        for v in reqs:
            keys.append (None)
            reqs_.append (v)
        return Tasks (reqs_, timeout, self._set_was_id (meta), keys)

    def Mask (self, data = None, _expt = None, _status_code = None, meta = None, keys = None):
        return Mask (data, _expt, _status_code, meta = self._set_was_id (meta), keys = keys)

    def Thread (self, target, *args, **kargs):
        # also can be Thread (target, args, kwargs, meta)
        kargs = self._set_postprocessor (kargs)
        return self.executors.create_thread (self.ID, target, *args, **kargs)

    def Process (self, target, *args, **kargs):
        kargs = self._set_postprocessor (kargs)
        return self.executors.create_process (self.ID, target, *args, **kargs)

    def ThreadPass (self, target, *args, **kargs):
        _was, args, kargs = self._insert_cloned_was (args, kargs)
        kargs = self._set_postprocessor (kargs)
        return self.executors.create_thread (_was.ID, target, *args, **kargs).then ()
    ThreadFuture = ThreadPass

    def Subprocess (self, cmd, meta = None, filter = None, timeout = DEFAULT_BACKGROUND_TASK_TIMEOUT):
        return sp_task.Task (cmd, self._set_was_id (meta), filter, timeout)
