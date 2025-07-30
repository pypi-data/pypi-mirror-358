from urllib.parse import unquote_plus, quote_plus
from types import FunctionType
from functools import wraps
import sys
import re
import copy
import inspect
from urllib.parse import urljoin
import fnmatch
from rs4.termcolor import tc
from . import parameters

RX_RULE = re.compile ("(/<(.+?)>)")
RE_RULE_NAME_ONLY = re.compile ("/<(?:[a-z]+?:)?([_0-9a-zA-Z]+?)>")

class Router:
    SPECIAL_UIDS = ("notme", "me", "new")
    def __init__ (self):
        self.route_map = {}
        self.route_map_fancy = {}
        self._route_priority = []
        self._function_names = {}
        self._async_streams = set ()
        self._func_annotations = {}
        self._func_resources = {}
        self._disabled = {}

    # Routing ------------------------------------------------------
    def unroute (self, pattern, response_code = 404):
        self._disabled [pattern] = response_code

    def async_stream (self, f):
        self._async_streams.add (self.get_func_id (f))
        return f

    def route (self, rule, **k):
        def decorator (f):
            self.save_function_spec (f)
            @wraps(f)
            def wrapper (*args, **kwargs):
                return f (*args, **kwargs)
            k ["wrapper"] = wrapper # keep this for protecting oid
            self.add_route (rule, f, **k)
            self._function_names [id (wrapper)] = self.get_func_id (f)
            return wrapper
        return decorator

    def get (self, rule, **k):
        k ["methods"] = ["GET"]
        return self.route (rule, **k)

    def post (self, rule, **k):
        k ["methods"] = ["POST"]
        return self.route (rule, **k)

    def patch (self, rule, **k):
        k ["methods"] = ["PATCH", "OPTIONS"]
        return self.route (rule, **k)

    def put (self, rule, **k):
        k ["methods"] = ["PUT", "OPTIONS"]
        return self.route (rule, **k)

    def delete (self, rule, **k):
        k ["methods"] = ["DELETE", "OPTIONS"]
        return self.route (rule, **k)

    def update_validator (self, func_id):
        # IMP: @route is more later
        for scope, argspec in self._current_validators:
            validators = self._parameter_caches [func_id][scope]
            if func_id in self._func_annotations:
                for k, v in self._func_annotations [func_id].items ():
                    parameters.regroup_type (validators, v, k)
                parameters.merge_types (validators)

            if func_id in self._func_resources:
                resource = self._func_resources [func_id]["__proto__"]
                options = resource [-1]
                if 'injections' in options:
                    for k, v in options.pop ('injections').items ():
                        validators [k] = v

                # if argspec:
                #     if 'defaults' in options:
                #         options ['defaults'].update (argspec.defaults)
                #     else:
                #         options ['defaults'] = argspec.defaults

                # if func_id not in self._websocket_configs:
                if "required" not in validators:
                    validators ["required"] = []
                defaults = options.get ("defaults", {})
                for arg in options ['args']:
                    if arg not in defaults and arg not in validators ["required"]:
                        validators ["required"].append (arg)
                if not validators ["required"]:
                    validators.pop ("required")
        # finally
        self._current_validators = []

    def add_route (self, rule, func, **options):
        if rule and rule [0] != "/":
            raise AssertionError ("Url rule should be starts with '/', {} for {}".format (rule, self.get_func_id (func)))

        func_id = self.get_func_id (func)
        try:
            options ["websocket_sepc"], options ["websocket_timeout"] = self._websocket_configs [func_id]
        except (KeyError, ValueError):
            pass

        options ["func_id"] = func_id
        options ["opts"] = self._mount_option
        options ["route"] = rule
        # options ["overridable"] = self.is_overridable (func)
        options ["overridable"] = "overrides"

        is_alter_routing = id (func) in self._function_names
        is_reloading = False
        if not is_alter_routing:
            if not self._started and not self._reloading and func_id in self._function_names and "argspec" not in options:
                # if options ["overridable"] == 'extends':
                #     return
                # if options ["overridable"] != 'overrides':
                #     self.log ("router `{}` is replaced, you can't access the old".format (tc.magenta (func_id)), "debug")
                self.log ("router {} is replaced, you can't access the old".format (tc.magenta (func_id)), "warn")

            if func_id in self._function_names and "argspec" not in options:
                is_reloading = True
                # reloading, remove old func
                deletable = None
                for k, v in self._function_names.items ():
                    if v == func_id:
                        deletable = k
                        break

                if deletable:
                    del self._function_names [deletable]

        mount_prefix = self._mount_option.get ("point")
        if not mount_prefix:
            mount_prefix = self._mount_option.get ("mount")

        if mount_prefix:
            while mount_prefix:
                if mount_prefix [-1] == "/":
                    mount_prefix = mount_prefix [:-1]
                else:
                    break
            rule = (mount_prefix + rule) or '/'

        try:
            fspec = self._function_specs [func_id]
        except KeyError:
            fspec =  inspect.getfullargspec (func)
            self._function_names [id (func)] = func_id

        if not is_alter_routing and fspec.varargs is not None:
            raise ValueError ("var args is not allowed")

        options ["args"] = fspec.args [1:]
        options ["keywords"] = fspec.varkw

        if fspec.annotations and func_id:
            options ["annotations"] = {k: v.__name__ if hasattr (v, '__name__') else str (v) for k, v in fspec.annotations.items () if k != 'context'}
            self._func_annotations [func_id] = {k: v if isinstance (v, str) else v.__name__ for k, v in fspec.annotations.items () if k != 'context'}

        injections = {}
        if fspec.defaults:
            defaults = {}
            argnames = fspec.args [(len (fspec.args) - len (fspec.defaults)):]
            for i in range (len (fspec.defaults)):
                if type (fspec.defaults[i]) is FunctionType:
                    injections [argnames [i] + '__inject'] = fspec.defaults [i]
                    defaults [argnames [i]] = None
                else:
                    defaults [argnames [i]] = fspec.defaults[i]
            options ["defaults"] = defaults
            options ["injections"] = injections

        use_data_container_validator = False
        methods = options.get ('methods')
        if not methods:
            use_data_container_validator = True
        else:
            for it in ('POST', 'PUT', 'PATCH'):
                if it in methods:
                    use_data_container_validator = True
                    break

        # func_id not in self._websocket_configs and
        if ((func_id not in self._parameter_caches) and (fspec.annotations or injections or use_data_container_validator)):
            func = self.argspec (func)
            self._function_names [id (func)] = func_id
            options ["func_id"] = func_id

        if options.get ("stream", False):
            options ['async_stream'] = True
            self.async_stream (func)

        if "async_stream" not in options:
            options ['async_stream'] = func_id in self._async_streams

        if self._mount_option.get ("authenticate"):
            options ["authenticate"] = self._mount_option ["authenticate"]
        if self._need_authenticate:
            if func.__name__ == self._need_authenticate [0]:
                options ["authenticate"] = self._need_authenticate [1]
            self._need_authenticate = None
        # for backward competable
        if options.get ("authenticate") in (True, 1):
            options ["authenticate"] = self.authenticate or "digest"
        elif options.get ("authenticate") in (False, 0):
            options ["authenticate"] = None
        assert options.get ("authenticate") in self.AUTH_TYPES

        s = rule.find ("/<")
        if s == -1:
            s_rule = rule
            try:
                self.route_map [rule]["__default__"]
            except KeyError:
                pass
            else:
                # IMP: automatically added, but current has priority
                del self.route_map [rule]["__default__"]
            self._function_names [func_id] = (rule,)
            if rule not in self.route_map:
                self.route_map [rule] = {}
            resource = self.route_map [rule]
            proto = (func, func.__name__, func.__code__.co_varnames [1:func.__code__.co_argcount], None, func.__code__.co_argcount - 1, rule, options)

        else:
            prefix = rule [:s]
            s_rule = rule
            rulenames = []
            urlargs = RX_RULE.findall (rule)
            options ["urlargs"] = len (urlargs)

            for r, n in urlargs:
                if n.startswith ("int:"):
                    rulenames.append ((n[4:], n[:3]))
                    rule = rule.replace (r, "/({}|[0-9]+)".format ("|".join (self.SPECIAL_UIDS)))
                elif n.startswith ("float:"):
                    rulenames.append ((n[6:], n [:5]))
                    rule = rule.replace (r, "/({}|[.0-9]+)".format ("|".join (self.SPECIAL_UIDS)))
                elif n.startswith ("path:"):
                    rulenames.append ((n[5:], n [:4]))
                    path_re = []
                    if 'valid_pathes' in options:
                        assert isinstance (options ['valid_pathes'], (list, tuple)), 'valid_pathes should be list or tuple'
                        path_re.append ('(?=(?:{}))'.format ('|'.join (options ['valid_pathes'])))
                    if 'ignore_pathes' in options:
                        assert isinstance (options ['ignore_pathes'], (list, tuple)), 'ignore_pathes should be list or tuple'
                        path_re.append ('(?!(?:{}))'.format ('|'.join (options ['ignore_pathes'])))
                    path_re = ''.join (path_re)
                    rule = rule.replace (r, f"/({path_re}.*)")
                else:
                    rulenames.append ((n, "string"))
                    rule = rule.replace (r, "/([^/]+)")

            for n, t in rulenames:
                assert n in options ['args'], f"router should have paramter `{n}`"

            if len (rulenames) > 1 and rulenames [-1][0] in options.get ("defaults", {}):
                sep = rule.rfind ("/(")
                base = rule [:sep]
                optional = rule [sep:]
                rule = '^{}(?:$|(?:/{}))'.format (base, optional [1:])
            else:
                rule = "^" + rule + "$"

            re_rule = re.compile (rule)
            self._function_names [func_id] = (prefix, re_rule)

            if prefix not in self.route_map_fancy:
                self.route_map_fancy [prefix] = {}
            if re_rule not in self.route_map_fancy [prefix]:
                self.route_map_fancy [prefix][re_rule] = {}

            resource = self.route_map_fancy [prefix][re_rule]
            proto = (func, func.__name__, func.__code__.co_varnames [1:func.__code__.co_argcount], tuple (rulenames), func.__code__.co_argcount - 1, s_rule, options)

            if s >= 0 and s_rule [-1] == ">" and len (rulenames) == 1 and rulenames [0][0] in options.get ("defaults", {}):
                # implicit mount if not exist explicit one
                simple_rule = s_rule [:s]
                if not simple_rule:
                    simple_rule = mount_prefix and mount_prefix + "/" or "/"
                if simple_rule not in self.route_map:
                    options_ = copy.copy (options)
                    options_ ["argspec"] = proto [2:5]
                    self.add_route (simple_rule [len (mount_prefix or ''):], func, **options_)

            self._route_priority.append ((prefix, re_rule))
            self._route_priority.sort (key = lambda x: len (x [0]), reverse = True)

        if "__proto__" in resource:
            methods = set (resource ["__proto__"][-1].get ("methods", []))
        else:
            methods = set (options.get ("methods", []))
            if not methods:
                methods = {"GET", "POST"}
        resource ["__proto__"] = proto
        resource ["__default__"] = proto

        for method in options.get ("methods", methods):
            if method in resource:
                # if options ["overridable"] == 'extends':
                #     continue
                # if options ["overridable"] == 'overrides': # overwrite
                #     pass
                # elif resource [method][-1].get ('overridable') == 'extends': # overwrite
                #     pass
                if not self._started and not self._reloading and method in {"GET", "POST", "DELETE", "PUT", "PATCH"}:
                    self.log ("endpoint {} {} is overridden".format (tc.grey (method), tc.grey (rule)), "info")
            resource [method] = proto
            methods.add (method)

        for proto in resource.values ():
            proto [-1]["methods"] = methods

        self._func_resources [func_id] = resource
        if func_id in self._parameter_caches:
            self.update_validator (func_id)
        return func

    def optimal_proto (self, map, key, func_id, method = '__proto__'):
        for method_ in map [key]:
            if func_id == map [key][method_][6]['func_id']:
                method = method_
                break
        return map [key][method]

    # URL Building ------------------------------------------------
    def _build_static_url (self, path, base):
        if path:
            assert not path.startswith ('/'), 'static path should not start with /'
        try:
            base_path = getattr (self.config, base)
        except AttributeError:
            base_path = '/'
        return urljoin (base_path, path)

    def static (self, path):
        return self._build_static_url (path, 'STATIC_URL')

    def media (self, path):
        return self._build_static_url (path, 'MEDIA_URL')

    def reroute (self, thing):
        if isinstance (thing, FunctionType):
            thing = self._function_names [id (thing)]
        try:
            return self._function_map [thing]
        except KeyError:
            cand = []
            for n, f in self._function_map.items ():
                if n.endswith (thing):
                    cand.append (f)
            if len (cand) == 1:
                self._function_map [thing] = cand [0] # caching
                return cand [0]
            if not cand:
                raise NameError ("{} not found".format (thing))
            raise NameError ("{} is ambiguous name".format (thing))

    def get_urlspecs (self):
        specs = {}
        for k, v in self._function_names.items ():
            if isinstance (k, int):
                continue
            specs [k] = self.urlfor (k, __resource_spec_only__ = True)
        return specs

    def urlfor (self, thing, *args, **kargs):
        if isinstance (thing, FunctionType):
            try:
                thing = self._function_names [id (thing)]
            except KeyError:
                thing = f'{thing.__module__}:{thing.__name__}'

        if not thing or thing.startswith ("/"):
            return self.basepath [:-1] + self.mount_p [:-1] + thing

        try:
            try:
                fpath = self._function_names [thing]
            except KeyError:
                cand = []
                for n, p in self._function_names.items ():
                    if not isinstance (n, str):
                        continue
                    if n.endswith (thing):
                        cand.append (p)

                if len (cand) == 1:
                    self._function_names [thing] = cand [0]  # caching
                    fpath = cand [0]
                else:
                    raise KeyError

            if len (fpath) == 2:
                if not args and not kargs:
                    proto = self.optimal_proto (self.route_map, fpath [0], thing)
                else:
                    proto = self.optimal_proto (self.route_map_fancy [fpath [0]], fpath [1], thing)
            else:
                proto = self.optimal_proto (self.route_map, fpath [0], thing)

        except KeyError:
            raise NameError ("{} not found".format (str (thing)))

        func, name, fuvars, favars, numvars, str_rule, options = proto
        if "__resource_spec_only__" in kargs:
            if 'urlspec' in options:
                return options ['urlspec']

            defaults = options.get ('defaults', {})
            annotations = options.get ('annotations', {})
            args = options.get ('args', [])
            numparams = options.get ('urlargs', 0)
            route = str_rule
            if numparams:
                route = RE_RULE_NAME_ONLY.sub ("/:\\1", route)

            argspecs = self._get_parameter_requirements (thing)
            for scope, argspec in argspecs.items ():
                for k in args:
                    if k not in argspec:
                        argspec [k] = {}
                    if k in annotations:
                        argspec [k]['type'] = annotations [k]
                    if k in defaults:
                        argspec [k]['default'] = defaults [k]
                        try: del argspec [k]['required']
                        except KeyError: pass
                    else:
                        argspec [k]['required'] = True

            options ['urlspec'] = dict (
                methods = list (options.get ('methods', ["GET"])),
                path = self.urlfor (route),
                params = args [:numparams],
                argspecs = argspecs,
            )
            return options ['urlspec']

        if "__resource_path_only__" in kargs:
            if 'baseurl' in options:
                return options ['baseurl']
            url = str_rule
            if favars:
                s = url.find ("<")
                if s != -1:
                    url = url [:s]
            options ['baseurl'] = self.urlfor (url)
            return options ['baseurl']

        params = {}
        try:
            currents = kargs.pop ("__defaults__")
        except KeyError:
            currents = {}
        else:
            for k, v in currents.items ():
                if k in options.get ('args', []):
                    params [k] = v

        if "argspec" in options:
            fuvars, favars, numvars = options ["argspec"]
            if len (args) or favars [0][0] in kargs or favars [0][0] in params:
                n, t = favars[0]
                str_rule += "/<{}{}>".format (t != "string" and (t + ":") or "", favars[0][0])

        function_args = options.get ("args", [])
        has_kargs = options.get ("keywords")
        for i in range (len (args)):
            try:
                name = function_args [i]
            except IndexError:
                raise ValueError ("too many parameters")
            params [name] = args [i]

        for k, v in kargs.items ():
            if not has_kargs and k not in function_args:
                raise ValueError ("parameter {} is not allowed".format (k))
            params [k] = v

        url = str_rule
        if favars: #fancy [(name, type),...]. /fancy/<int:cid>/<cname>
            for n, t in favars:
                omittable = False
                if n not in params:
                    try:
                        params [n] = currents [n]
                    except KeyError:
                        try:
                            params [n] = options ["defaults"][n]
                        except KeyError:
                            raise AssertionError ("Argument '%s' missing" % n)
                        else:
                            omittable = True

                if omittable:
                    url = url.replace ("/<%s%s>" % (t != "string" and t + ":" or "", n), '')
                else:
                    value = quote_plus (str (params [n]))
                    if t == "string":
                        value = value.replace ("+", "_")
                    elif t == "path":
                        value = value.replace ("%2F", "/")
                    url = url.replace ("<%s%s>" % (t != "string" and t + ":" or "", n), value)
                del params [n]

        params = [(k, v) for k, v in params.items () if v is not None] # ignore explicit None
        if params:
            url = url + "?" + "&".join (["%s=%s" % (k, quote_plus (str(v))) for k, v in params])

        return self.urlfor (url)
    build_url = urlfor

    # Routing ------------------------------------------------------
    def get_route_map (self):
        return self.route_map

    def set_route_map (self, route_map):
        self.route_map = route_map

    def get_routed (self, method_chain):
        if not method_chain:
            return
        temp = method_chain
        while 1:
            routed = temp [1]
            if type (routed) is not list:
                return routed
            temp = routed

    def find_route (self, path_info, command):
        if not path_info:
            return self.urlfor ("/"), None

        if path_info in self.route_map:
            try:
                proto = self.route_map [path_info][command]
            except KeyError:
                if command == 'OPTIONS' and self.access_control_allow_origin:
                    proto = self.route_map [path_info]['__proto__']
                else:
                    raise AssertionError
            return proto [0], proto [-1]

        trydir = path_info + "/"
        if trydir in self.route_map:
            return self.urlfor (trydir), None

        raise KeyError

    def verify_rule (self, path_info, rule, protos, command):
        arglist = rule.findall (path_info)
        if not arglist:
            return None, None, None

        try:
            f, n, l, a, c, s, options = protos [command]
        except KeyError:
            if command == 'OPTIONS' and self.access_control_allow_origin:
                f, n, l, a, c, s, options = protos ['__proto__']
            else:
                raise AssertionError

        arglist = arglist [0]
        if type (arglist) is not tuple:
            arglist = (arglist,)

        kargs = {}
        for i in range (len(arglist)):
            an, at = a [i]
            if arglist [i] == '':
                kargs [an] = options ['defaults'][an]
                continue

            if at == "int":
                if arglist [i] in self.SPECIAL_UIDS:
                    kargs [an] = arglist [i]
                else:
                    kargs [an] = int (arglist [i])
            elif at == "float":
                if arglist [i] in self.SPECIAL_UIDS:
                    kargs [an] = arglist [i]
                else:
                    kargs [an] = float (arglist [i])
            elif at == "path":
                kargs [an] = unquote_plus (arglist [i])
            else:
                kargs [an] = unquote_plus (arglist [i])

        return f, options, kargs

    def find_method (self, path_info, command):
        if not (path_info.startswith (self.mount_p) or (path_info + "/").startswith (self.mount_p)):
            return self, None, None, None, 404

        path_info = path_info [self.path_suffix_len:]
        method, kargs = None, {}

        if self._disabled:
            for pattern, respcode in self._disabled.items ():
                if fnmatch.fnmatch (path_info, pattern):
                    return self, None, None, None, respcode

        try:
            try:
                method, options = self.find_route (path_info, command)
            except KeyError:
                for prefix, rule in self._route_priority:
                    if not path_info.startswith (prefix):
                        continue
                    protos = self.route_map_fancy [prefix][rule]
                    try:
                        method, options, kargs = self.verify_rule (path_info, rule, protos, command)
                    except ValueError:
                        return self, None, None, None, 400
                    if method:
                        break

        except AssertionError:
            return self, None, None, None, 405 # method not allowed

        if method is None:
            return self, None, None, None, 404
        if isinstance (method, str):
            return self, method, None, None, 301

        hooks = tuple ([ them [:] for them in self._parent_hooks ])
        # lower version compat.
        for idx, f in enumerate (self._binds_request):
            if f is not None:
                hooks [idx].append (f)

        parts = method.__module__.split (".")
        last_idx = len (parts) - 1
        parent = self._module_tree
        for idx, p in enumerate (parts):
            if p not in parent:
                break

            try:
                fs = parent [p]['#']
                for idx, f in enumerate (fs):
                    if f is not None:
                        hooks [idx].append (f)
            except KeyError:
                pass
            parent = parent [p]

        return (
            self,
            [hooks [0], method, reversed (hooks [1]), reversed (hooks [2]), reversed (hooks [3])],
            kargs,
            options,
            None
        )
