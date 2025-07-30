from __future__ import annotations
import re
import inspect
from functools import wraps
import json
import types as types_
import re
import skitai
from rs4.annotations import copy_class
from skitai.exceptions import HTTPError

from ..collectors.multipart_collector import FileWrapper

def regroup_type (specs, tname, fname):
    tgrp = tname + 's'
    if tgrp not in specs:
        specs [tgrp] = []
    fname not in specs [tgrp] and specs [tgrp].append (fname)

def merge_types (specs):
    for k in list (specs.keys ()):
        if type (specs [k]) is not type:
            continue
        if k.endswith ('__regex') and isinstance (specs [k], str):
            specs [f'{k [:-7]}__search'] = re.compile (specs [k])
            continue
        if k.endswith ('__iregex') and isinstance (specs [k], str):
            specs [f'{k [:-8]}__search'] = re.compile (specs [k], re.I)
            continue
        if k.endswith ('__nregex') and isinstance (specs [k], str):
            specs [f'{k [:-8]}__nsearch'] = re.compile (specs [k])
            continue
        if k.endswith ('__inregex') and isinstance (specs [k], str):
            specs [f'{k [:-9]}__nsearch'] = re.compile (specs [k], re.I)
            continue
        typ = specs.pop (k)
        regroup_type (specs, typ.__name__, k)


class ArgSpec:
    PREFIEND_PARAMS = None
    def __init__ (self, spec_class):
        if ArgSpec.PREFIEND_PARAMS is None:
            ArgSpec.PREFIEND_PARAMS = [f'__{it}__' for it in Parameters.PARAM_CUSTOM_TYPES.union (Parameters.PARAM_TYPES)]

        self.specs = {"required": []}
        self.defaults = {}
        self.fields = set ()

        for it in dir (spec_class):
            val = getattr (spec_class, it)
            if it in ArgSpec.PREFIEND_PARAMS:
                op = it [2:-2]
                self.specs [op] = val
                for each in val:
                    self.fields.add (each)
            elif it.startswith ('__'):
                continue
            elif '__' in it:
                self.specs [it] = val
                self.fields.add (it.split ('__', 1) [0])
            else:
                self.defaults [it] = val
                typ = type (val)
                if isinstance (typ, (str, int, bool, list, tuple, dict, float)) and it not in self.specs:
                    regroup_type (self.specs, typ.__name__, it)
                self.fields.add (it)

        if hasattr (spec_class, "__annotations__"):
            _d = {}
            for k, v in spec_class.__annotations__.items ():
                regroup_type (self.specs, v if isinstance (v, str) else v.__name__, k)
                self.fields.add (k)
            self.specs.update (_d)

        for k in self.fields:
            if k in self.defaults or k in self.specs ['required']:
                continue
            self.specs ['required'].append (k)

        merge_types (self.specs)

    def set_default (self, validators, validatable_args, kwargs):
        if not self.defaults:
            return
        protected = validators.get ("protected", [])
        editables = validators.get ("editables", [])
        for k, v in self.defaults.items ():
            if protected and k in protected:
                continue
            if editables and k not in editables:
                continue
            if k not in validatable_args:
                kwargs [k] = validatable_args [k] = v

def _datamodel (*_cls):
    related_models = None
    def wrap (cls):
        def set_list_item (k, item):
            try:
                attr = getattr (cls, k)
            except AttributeError:
                setattr (cls, k, [item])
            else:
                item not in attr and attr.append (item)

        setattr (cls, '__related_models__', related_models)
        for model in related_models:
            for k, v in model.get_field_spec ().items ():
                type = v ['type']
                if type in ('int', 'str', 'bool', 'float', 'list', 'file'):
                    set_list_item (f'__{type}s__', k)
                elif type == 'email':
                    setattr (cls, f'{k}__search', Parameters.RX_EMAIL)
                elif type == 'uuid':
                    setattr (cls, f'{k}__search', Parameters.RX_UUID)
                elif type == 'url':
                    setattr (cls, f'{k}__search', Parameters.RX_URL)

                if 'null' not in v and 'default' not in v:
                    set_list_item ('__required__', k)
                else:
                    setattr (cls, k, None)
                if 'maxlen' in v:
                    setattr (cls, f'{k}__len__lte', v ['maxlen'])
                if 'choices' in v:
                    setattr (cls, f'{k}__codein', v ['choices'])
                if 'default' in v:
                    setattr (cls, k, v ['default'])
        return cls

    if hasattr (_cls [0], "get_field_spec"):
        related_models = _cls
        return wrap

    return _cls [0]


class Parameters:
    RX_EMAIL = re.compile (r"^[a-z0-9][-.a-z0-9]*@[-a-z0-9]+\.[-.a-z0-9]{2,}[a-z]$", re.I)
    RX_URL = re.compile (r"^https?://[-a-z0-9]+\.[-.a-z0-9]{2,}[a-z]", re.I)
    RX_UUID = re.compile (r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
    RX_UNSAFE = re.compile (r"(<script[\s>]|['\"=]\s*javascript:|\son[:a-z]+\s*=\s*|&#x[0-9a-f]{2};|┻━┻)", re.I)
    RX_INVALID_PASSWORD = re.compile ('^(.{0,7}|[^0-9]*|[a-zA-Z0-9]*)$')
    PARAM_CUSTOM_TYPES = {'computed', 'required', 'protected', 'manyof', 'oneof', 'editables', 'optional'}
    PARAM_TYPES = {
        'ints', 'floats', 'lists', 'dicts', 'bools', 'strs', 'files',
        'ranges', 'safes', 'notags', 'jsons', 'emails', 'uuids',
        'urls', 'querystrings', 'passwords',
        'strings', 'booleans',
    }
    RX_TYPEMAP = {
        'emails': RX_EMAIL,
        'uuids': RX_UUID,
        'urls': RX_URL,
    }
    RX_TYPEMAP_NEG = {
        'safes': RX_UNSAFE,
        'passwords': RX_INVALID_PASSWORD,
    }

    OPS = {
        "lte": lambda val, fd, cond: val > cond and 'parameter {} should less than or equal to {}'.format (fd, cond) or None,
        "lt": lambda val, fd, cond: val >= cond and 'parameter {} should less than {}'.format (fd, cond) or None,
        "gte": lambda val, fd, cond: val < cond and 'parameter {} should greater than or equal to {}'.format (fd, cond) or None,
        "gt": lambda val, fd, cond: val <= cond and 'parameter {} should greater than {}'.format (fd, cond) or None,

        "between": lambda val, fd, cond: not (cond [0] <= val <= cond [1]) and 'parameter {} should be between {} ~ {}'.format (fd, cond [0], cond [1]) or None,
        "in": lambda val, fd, cond: val not in cond and 'parameter {} should be one of {}'.format (fd, cond) or None,
        "notin": lambda val, fd, cond: val in cond and 'parameter {} should be not one of {}'.format (fd, cond) or None,

        "codein": lambda val, fd, cond: val not in [it [0] for it in cond] and 'parameter {} should be one of {}'.format (fd, [it [0] for it in cond]) or None,
        "codenotin": lambda val, fd, cond: val in [it [0] for it in cond] and 'parameter {} should be not one of {}'.format (fd, [it [0] for it in cond]) or None,

        "eq": lambda val, fd, cond: val != cond and 'parameter {} should be {}'.format (fd, cond) or None,
        "ieq": lambda val, fd, cond: val.lower () != cond.lower () and 'parameter {} should be {}'.format (fd, cond) or None,
        "neq":  lambda val, fd, cond: val == cond and 'parameter {} should not be {}'.format (fd, cond) or None,
        "ineq":  lambda val, fd, cond: val.lower () == cond.lower () and 'parameter {} should not be {}'.format (fd, cond) or None,

        "contains": lambda val, fd, cond: val.find (cond) == -1 and 'parameter {} should contain {}'.format (fd, cond) or None,
        "icontains": lambda val, fd, cond: val.lower ().find (cond.lower ()) == -1 and 'parameter {} should contain {}'.format (fd, cond) or None,
        "ncontains": lambda val, fd, cond: val.find (cond) != -1 and 'parameter {} should not contain {}'.format (fd, cond) or None,
        "incontains": lambda val, fd, cond: val.lower ().find (cond.lower ()) != -1 and 'parameter {} should not contain {}'.format (fd, cond) or None,

        "startswith": lambda val, fd, cond: not val.startswith (cond) and 'parameter {} should start with {}'.format (fd, cond) or None,
        "istartswith": lambda val, fd, cond: not val.lower ().startswith (cond.lower ()) and 'parameter {} should start with {}'.format (fd, cond) or None,
        "nstartswith": lambda val, fd, cond: val.startswith (cond) and 'parameter {} should not start with {}'.format (fd, cond) or None,
        "instartswith": lambda val, fd, cond: val.lower ().startswith (cond.lower ()) and 'parameter {} should not start with {}'.format (fd, cond) or None,

        "endswith": lambda val, fd, cond: not val.endswith (cond) and 'parameter {} should end with {}'.format (fd, cond) or None,
        "iendswith": lambda val, fd, cond: not val.lower ().endswith (cond.lower ()) and 'parameter {} should start with {}'.format (fd, cond) or None,
        "inendswith": lambda val, fd, cond: val.lower ().endswith (cond.lower ()) and 'parameter {} should not start with {}'.format (fd, cond) or None,
        "nendswith": lambda val, fd, cond: val.endswith (cond) and 'parameter {} should not end with {}'.format (fd, cond) or None,

        "regex": lambda val, fd, cond: not re.compile (cond).search (val) and 'parameter {} should match with regular expression {}'.format (fd, cond) or None,
        "iregex": lambda val, fd, cond: not re.compile (cond, re.I).search (val) and 'parameter {} should match with regular expression {} with case insensitivity'.format (fd, cond) or None,

        "nregex": lambda val, fd, cond: re.compile (cond).search (val) and 'parameter {} should not match with regular expression {}'.format (fd, cond) or None,
        "inregex": lambda val, fd, cond: re.compile (cond, re.I).search (val) and 'parameter {} should not match with regular expression {} with case insensitivity'.format (fd, cond) or None,

        "match": lambda val, fd, cond: not cond.match (val) and 'parameter {} should match with regular expression {}'.format (fd, cond) or None,
        "search": lambda val, fd, cond: not cond.search (val) and 'parameter {} should match with regular expression {}'.format (fd, cond) or None,

        "nmatch": lambda val, fd, cond: cond.match (val) and 'parameter {} should not match with regular expression {}'.format (fd, cond) or None,
        "nsearch": lambda val, fd, cond: cond.search (val) and 'parameter {} should not match with regular expression {}'.format (fd, cond) or None,
    }

    # django compat
    OPS ["range"] = OPS ["between"]
    OPS ["exact"] = OPS ["eq"]
    OPS ["iexact"] = OPS ["ieq"]
    OPS ["nexact"] = OPS ["neq"]
    OPS ["inexact"] = OPS ["ineq"]

    # lower version compat
    OPS ["notcontain"] = OPS ["ncontains"]
    OPS ["notendwith"] = OPS ["nendswith"]
    OPS ["notstartwith"] = OPS ["nstartswith"]

    def __init__ (self):
        self._parameter_caches = {}
        self._current_validators = []

    def _get_parameter_requirements (self, func_id, merge = True):
        parameter_requirements = self._parameter_caches.get (func_id, {})
        r = {}
        for scope, ps in parameter_requirements.items ():
            d = {}
            for k, v in ps.items ():
                if k == 'computed':
                    if not isinstance (v, (list, tuple)):
                        v = [v]
                    d [k] = [v.__name__ for it in v]
                elif hasattr (v, 'pattern'):
                    try: fd, op = k.split ('__', 1)
                    except ValueError: fd, op = k, 'search'
                    k = f"{fd}__{'i' if v.flags == 34 else ''}{'n' if op [0] == 'n' else ''}regex"
                    d [k] = v.pattern
                elif type (v) is types_.FunctionType:
                    if not k.endswith ("__computed"):
                        k = f"{k}__computed"
                    d [k] = v.__name__
                else:
                    d [k] = v

            if not merge:
                r [scope] = d
                continue

            fields = {}
            for k, v in d.items ():
                if k in self.PARAM_TYPES:
                    for it in v:
                        if it not in fields:
                            fields [it] = {}
                        typ = k [:-1]
                        fields [it]['type'] = typ

                elif k in self.PARAM_CUSTOM_TYPES:
                    for it in v:
                        if it not in fields:
                            fields [it] = {}
                        if k in ("editables", "optional"):
                            continue
                        elif k in ("protected", "required"):
                            fields [it][k] = True
                        else:
                            fields [it][k] = v

                else:
                    try:
                        it, rest = k.split ('__', 1)
                    except ValueError:
                        it, rest = k, 'eq'

                    if it not in fields:
                        fields [it] = {}
                    fields [it][rest] = v

            if 'editables' in d:
                editables = d ['editables']
                for k, v in fields.items ():
                    if k not in editables:
                        v ['protected'] = True

            if 'optional' in d:
                for k in d ['optional']:
                    if k not in fields:
                        fields [k] = {}

            r [scope] = fields
        return r

    def _validate_param (self, params, __options = {}, **validators):
        params = params or {}
        non_types = []
        computed = []

        editables = validators.get ('editables', [])
        optional = validators.get ('optional', [])
        protected = validators.get ('protected', [])

        for k in validators:
            if k in self.PARAM_CUSTOM_TYPES:
                fields = validators [k]
                if not fields:
                    continue

                if k == 'computed':
                    if not isinstance (fields, (list, tuple)):
                        fields = [fields]
                    for each in fields:
                        computed.append ((None, 'inject', each))

                elif k == 'required':
                    if __options.get ('ignore_required', False): # IMP: need only functional required args
                        fields = [j for j in fields if j in __options.get ('func_args', [])]

                    for each in fields:
                        if editables and each not in editables:
                            continue
                        if protected and each in protected:
                            continue
                        try:
                            a, b = each.split (".")
                        except ValueError:
                            if params.get (each) in ('', None, [], {}):
                                return 'parameter {} is required'.format (each)
                        else:
                            if not params [a] or a not in params or not params [a].get (b):
                                return 'parameter {} is required'.format (each)

                elif k == 'editables':
                    for it in params:
                        if it in editables:
                            continue
                        return 'parameter {} is not editable'.format (it)

                elif k == 'protected':
                    for each in fields:
                        try:
                            a, b = each.split (".")
                        except ValueError:
                            if each in params:
                                return 'parameter {} is unknown'.format (each)
                        else:
                            if a not in params:
                                continue
                            if params [a] and b in params [a]:
                                return 'parameter {} is unknown'.format (each)

                elif k in ('oneof', 'manyof'):
                    vals = []
                    for fd in fields:
                        vals.append (params.get (fd) is not None and 1 or 0)
                    if sum (vals) == 0:
                        if k == 'manyof':
                            return 'one or more parameters of {} are required'.format (', '.join (fields))
                        else:
                            return 'one parameter of {} are required'.format (', '.join (fields))
                    if k == 'one' and sum (vals) != 1:
                        return 'exactly one parameter of {} are required'.format (', '.join (fields))

            elif k in self.PARAM_TYPES:
                types = validators [k]
                for each in types:
                    try:
                        val = params [each]
                    except KeyError:
                        continue
                    if val is None:
                        continue

                    if k == 'querystrings':
                        continue

                    if k in self.RX_TYPEMAP_NEG:
                        if not isinstance (val, str):
                            return 'parameter {} should be string'.format (each)
                        non_types.append ((f'{each}__nsearch', self.RX_TYPEMAP_NEG [k]))
                        continue

                    if k in self.RX_TYPEMAP:
                        if not isinstance (val, str):
                            return 'parameter {} should be string'.format (each)
                        non_types.append ((f'{each}__search', self.RX_TYPEMAP [k]))
                        continue

                    try:
                        if k == 'ints':
                            val = int (val)

                        elif k in ('booleans', 'bools'):
                            if val in ('True', 'yes', 'true', 'y', 't'): val = True
                            elif val in ('False', 'no', 'false', 'n', 'f'): val = False
                            if val not in (True, False):
                                return 'parameter {} should be a boolean (one of yes, no, y, n, t, f, true or false)'.format (each)

                        elif k == 'files':
                            if not isinstance (val, FileWrapper):
                                return 'parameter {} should be a file'.format (each)

                        elif k == 'ranges':
                            try:
                                a, b = map (int, val.split ('~'))
                                val = (a, b)
                            except (AttributeError, ValueError):
                                return 'parameter {} should be `1~100` format'.format (each)

                        elif k == 'notags':
                            val = val.replace ('<', '&lt;').replace ('>', '&gt;')

                        elif k == 'floats':
                            val = float (val)

                        elif k.startswith ('lists'):
                            if not isinstance (val, (str, list, tuple)):
                                return 'parameter {} should be a list or comma/bar delimetered string'.format (each)
                            if isinstance (val, str):
                                if val == '':
                                    val = []
                                elif "|" in val:
                                    val = val.split ("|")
                                elif "," in val:
                                    val = val.split (",")
                                else:
                                    val = [val]

                        elif k in ('strings', 'strs'):
                            if not isinstance (val, str):
                                raise ValueError

                        elif k == 'dicts':
                            if isinstance (val, (dict, list)):
                                val = dict (val)
                            if not isinstance (val, dict):
                                raise ValueError

                        elif k == 'jsons':
                            val = json.loads (val) if val else {}

                        # finally altered val
                        params [each] = val

                    except (TypeError, ValueError):
                        return 'parameter {} should be {} type'.format (each, k [:-1])

            else:
                non_types.append ((k, validators [k]))

        for fd_, cond in non_types:
            es = fd_.split ('___')
            if len (es) > 1: # inspect JSON
                tail = ''
                val = params.get (es [0])
                fds = [es [0]]
                for e in es [1:]:
                    e, *index = e.split ('__')
                    try:
                        val = val [e]
                    except KeyError:
                        return 'parameter {} has key related error'.format (fd_)
                    if not index:
                        index = None
                    else:
                        if index [0].isdigit ():
                            tail = index [1:] or ''
                            try:
                                val = val [int (index [0])]
                            except:
                                return 'parameter {} has index related error'.format (fd_)
                            fds.append (index [0])
                        else:
                            index, tail = None, index
                        if tail:
                            tail = '__{}'.format ('__'.join (tail))
                    fds.append (e)
                fd = '.'.join (fds)
                ops = '{}{}'.format (fd, tail).split ('__')

            else:
                ops = fd_.split ("__")
                fd = ops [0]
                val = params.get (fd)

            if not (len (ops) <= 3 and fd):
                raise SyntaxError ("invalid require expression on {}".format (fd))

            if len (ops) == 1:
                if isinstance (cond, types_.FunctionType):
                    ops.append ('computed')
                elif hasattr (cond, 'search'):
                    ops.append ('search')
                else:
                    ops.append ('eq')

            if ops [-1] in ("computed", "inject"):
                computed.insert (0, (fd, ops [-1], cond))
                continue # later

            if val is None:
                continue

            if len (ops) == 2 and ops [1] == "len":
                ops.append ("eq")

            if len (ops) == 3:
                if ops [1] == "len":
                    val = len (val)
                    fd = "length of {}".format (fd)
                else:
                    raise ValueError ("Unknown function: {}".format (ops [1]))

            op = ops [-1]
            if op not in ('codein', 'codenotin'):
                try:
                    val = (isinstance (cond, (list, tuple)) and type (cond [0]) or type (cond)) (val)
                except ValueError:
                    return 'parameter {} is invalid'.format (fd)
                except TypeError:
                    pass # re.compile

            try:
                err = self.OPS [op] (val, fd, cond)
                if err:
                    return err
            except TypeError:
                return 'parameter {} is invalid'.format (fd) # not str for re.compile
            except KeyError:
                raise ValueError ("Unknown operator: {}".format (op))

        for fd, op, func in computed:
            val = params.get (fd)
            newval = func (skitai.was, val) if op == 'computed' else func (skitai.was)
            if fd and newval != val:
                params [fd] = newval

        # IMP: prefer null than blank
        for k in params:
            if hasattr (params [k], 'dtype'):
                continue
            if params [k] == '':
                params [k] = None

    def _validate_container (self, request, validators):
        if not request.split_uri () [2]: # querystring
            return

        if request.method in {"POST", "PUT", "PATCH"}:
            if "querystrings" not in validators:
                return f"URL parameter not allowed"

        if "querystrings" in validators:
            query_fields = validators ["querystrings"]
            for k in query_fields:
                if k in request.DATA:
                    return f"parameter `{k}` should be URL parameter"
            body_fields = [k for k in (list (request.DATA.keys ()) + list (request.URL.keys ())) if k not in query_fields]
            for k in body_fields:
                if k in request.URL:
                    return f"parameter `{k}` should be in body"

    def argspec (self, spec_class = None, scope = 'ARGS', required = None, datamodel = None, **validators):
        # spec_class, computed, required, protected, oneof, manyof, **validators
        class DummySpec:
            pass

        def decorator (f):
            self.save_function_spec (f)
            func_id = self.get_func_id (f)
            if not self._reloading:
                assert func_id not in self._websocket_configs, "use @argspec under @websocket decorator"

            if func_id not in self._parameter_caches:
                self._parameter_caches [func_id] = {}

            if required:
                validators ['required'] = required

            for k, v in list (validators.items ()):
                if (k in self.PARAM_CUSTOM_TYPES or k in self.PARAM_TYPES) and isinstance (v, str):
                    validators [k] = v.split ()
                else:
                    if type (v) is types_.FunctionType and k != 'computed' and '__' not in k:
                        validators [f'{k}__computed'] = validators.pop (k)
                    elif hasattr (v, 'search') and '__' not in k:
                        validators [f'{k}__search'] = validators.pop (k)
                    else:
                        validators [k] = v

            argspec = None
            if spec_class:
                argspec = ArgSpec (copy_class (spec_class))
                validators.update (argspec.specs)
            merge_types (validators)

            self._parameter_caches [func_id][scope] = validators
            self._current_validators.append ((scope, argspec))

            def processed (was, args, kwargs):
                nonlocal validators

                if func_id in self._websocket_configs:
                    return

                if args: # pipe call or XML/JSONRPC
                    return

                scope_ = scope
                if scope in ("FORM", "JSON", "DATA"):
                    if was.request.method not in {"POST", "PUT", "PATCH"}:
                        return
                    if scope == "JSON" and not was.request.get_header ("content-type", '').startswith ("application/json"):
                        return

                elif scope not in ("URL", "ARGS"):
                    if was.request.method != scope:
                        return
                    if scope in {"GET", "DELETE"}:
                        scope_ = "URL"
                    elif scope in {"POST", "PUT", "PATCH"}:
                        if was.request.get_header ("content-type", '').startswith ("application/json"):
                            scope_ = "JSON"
                        else:
                            scope_ = "FORM"
                    else:
                        return

                validatable_args = getattr (was.request, scope_)
                __options = {}
                if argspec:
                    set_default = True
                    # if hasattr (spec_class, '__related_models__') and was.request.method == 'PATCH':
                    if was.request.method == 'PATCH':
                        __options ['ignore_required'] = True
                        __options ['func_args'] = was.request.routable.get ('args', [])
                        set_default = False
                    set_default and argspec.set_default (validators, validatable_args, kwargs)

                more_info = self._validate_container (was.request, validators) or (validators and self._validate_param (validatable_args, __options, **validators))
                if more_info:
                    raise was.HttpError ("400 Bad Request", 'missing or bad parameter in {}: {}'.format (scope_, more_info), 40050)

                # syncing args --------------------------------------
                kwargs.update (validatable_args)
                if scope_ != "ARGS":
                    was.request.args.update (validatable_args)

            @wraps (f)
            def wrapper (was, *args, **kwargs):
                processed (was, args, kwargs)
                return f (was, *args, **kwargs)

            @wraps (f)
            async def awrapper (was, *args, **kwargs):
                processed (was, args, kwargs)
                return await f (was, *args, **kwargs)

            @wraps (f)
            async def agenwrapper (was, *args, **kwargs):
                processed (was, args, kwargs)
                async for it in f (was, *args, **kwargs):
                    yield it

            if inspect.iscoroutinefunction (f):
                return awrapper
            if inspect.isasyncgenfunction (f):
                return agenwrapper
            return wrapper

        if datamodel:
            assert spec_class is None, "cannot use spec_class and datamodel together"
            if not isinstance (datamodel, (list, tuple)):
                datamodel = (datamodel,)
            spec_class = _datamodel (*datamodel) (DummySpec)

        if type (spec_class) is types_.FunctionType:
            _f, spec_class = spec_class, None
            return decorator (_f)

        return decorator

    def inspect (self, scope = 'ARGS', required = None, **validators):
        # deprecasted
        if type (scope) is types_.FunctionType:
            return self.argspec (scope)
        return self.argspec (scope = scope, required = required, **validators)
    require = parameters_required = params_required = test_params = spec = inspect

    def validate (self, request, **kargs):
        if not kargs:
            return
        more_info = self._validate_param (request.ARGS, **kargs)
        if more_info:
            raise skitai.was.HttpError ("400 Bad Request", "missing or bad parameter: {}".format (more_info), 40050)
