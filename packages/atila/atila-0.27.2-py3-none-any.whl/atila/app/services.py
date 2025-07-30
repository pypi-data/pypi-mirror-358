from rs4.termcolor import tc
import os, sys
from importlib import reload
import time
from types import ModuleType, FunctionType
import copy
import inspect
from warnings import warn
import skitai

class Services:
    def __init__ (self):
        self.mount_p = "/"
        self.path_suffix_len = 0
        self.service_roots = []
        self.mount_params = {}
        self.reloadables = {}
        self.reloadable_objects = {}
        self.last_reloaded = time.time ()
        self._mount_order = []
        self._mount_funcs = []
        self._package_dirs = set ()
        self._mount_option = {}
        self._current_mount_options = []
        self._mounted_funcs = []
        self._module_tree = {}

    PACKAGE_DIRS = ["services", "exports"]
    def set_mount_point (self, mount):
        if not mount or mount == '/':
            self.mount_p = "/"
        elif mount [-1] != "/":
            self.mount_p = mount + "/"
        else:
            self.mount_p = mount
        self.path_suffix_len = len (self.mount_p) - 1

    def add_package (self, *names):
        for name in names:
            self.PACKAGE_DIRS.append (name)

    MOUNT_HOOKS = ["__mount__", "mount"]
    UMOUNT_HOOKS = ["__umount__", "umount", "dettach"]
    def _mount (self, module):
        def find_hooks (module):
            hooks = []
            for hook_name in ('request', 'wrapup', 'error', 'teardown'):
                try:
                    hooks.append (getattr (module, f'__{hook_name}__'))
                except AttributeError:
                    hooks.append (None)
            return hooks

        parts = module.__name__.split (".")

        if parts [0] not in self._module_tree: # service root
            self._module_tree [parts [0]] = {}
            try:
                root = sys.modules [parts [0]]
            except KeyError:
                pass
            else:
                self._module_tree [parts [0]]['#'] = find_hooks (root)

        last_idx = len (parts) - 1
        parent = self._module_tree
        for idx, p in enumerate (parts):
            if p not in parent:
                parent [p] = {}
            if idx == last_idx:
                parent [p]["#"] = find_hooks (module)
            parent = parent [p]

        mount_func = None
        for hook in self.MOUNT_HOOKS:
            if hasattr (module, hook):
                mount_func = getattr (module, hook)
                break

        if mount_func:
            if not self.auto_mount and module not in self.mount_params:
                return
            params = copy.deepcopy (self.mount_params.get (module, {}))
            if params.get ("debug_only") and not self.debug:
                return
            params ["module_name"] = module.__name__
            if self.enable_namespace and "ns" not in params:
                if module.__name__ not in self.PACKAGE_DIRS:
                    try:
                        _, ns = module.__name__.split (".", 1)
                        if _ not in self.PACKAGE_DIRS:
                            ns = module.__name__
                    except ValueError:
                        ns = module.__name__
                    params ["ns"] = ns

            setattr (module, "__options__", params)
            # for app initialzing and reloading
            self._mount_option = params

            try:
                self.run_hook (mount_func, params)
                if 'point' in params:
                    self.log ("- {} mounted to {}".format (tc.cyan (module.__name__), tc.grey (self.mount_p [:-1] + params ['point'])), "info")
                else:
                    self.log ("- {} mounted".format (tc.cyan (module.__name__)), "info")

                if hasattr (module, "__mounted__"):
                    self._mounted_funcs.append ((getattr (module, "__mounted__"), params))

            finally:
                self._mount_option = {}

        try:
            self.reloadables [module] = self.get_file_info (module)
        except FileNotFoundError:
            del self.reloadables [module]
            return

        # find recursively
        self.find_mountables (module)

    def _reload_objects (self, origin):
        if origin not in self.reloadable_objects:
            return

        deletables = []
        for objname, includers in self.reloadable_objects [origin].items ():
            for each in includers:
                try:
                    attr = getattr (origin, objname)
                except AttributeError:
                    deletables.append (objname)
                    continue
                setattr (each, objname, attr)

        for objname in deletables:
            try:
                del self.reloadable_objects [origin][objname]
            except KeyError:
                pass

    def _set_reloadable_object (self, objname, origin, includer):
        if origin not in self.reloadable_objects:
            self.reloadable_objects [origin] = {}
        if objname not in self.reloadable_objects [origin]:
            self.reloadable_objects [origin][objname] = set ()
        self.reloadable_objects [origin][objname].add (includer)

    def get_modpath (self, module):
        try:
            modpath = module.__spec__.origin
        except AttributeError:
            try:
                modpath = module.__file__
            except AttributeError:
                return
        return modpath

    def find_mountables (self, module):
        for attr in dir (module):
            if attr.startswith ("__"):
                continue
            v = getattr (module, attr)
            maybe_object = None
            mountable = False

            if hasattr (v, "__module__"):
                maybe_object = attr
                try:
                    v = sys.modules [v.__module__]
                    if v == module:
                        continue
                except KeyError:
                    continue

            if type (v) is not ModuleType:
                continue

            modpath = self.get_modpath (v)
            if not modpath:
                continue

            maybe_object and self._set_reloadable_object (maybe_object, v, module)
            if v in self.reloadables:
                continue

            if v in self.reloadables:
                continue

            for package_dir in self._package_dirs:
                if modpath.startswith (package_dir):
                    mountable = True
                    break

            if mountable:
                self._mount (v)

    def add_package_dir (self, path):
        # DEPRECATED. for mounting external package or module, use app.extends ()
        for exist in self._package_dirs:
            if exist.startswith (path) and len (path) > len (exist):
                return
        self._package_dirs.add (path)

    def mount_explicit (self):
        try:
            for module in self._mount_order:
                if module in self.reloadables:
                    continue
                self._mount (module)
        except RuntimeError:
            raise RuntimeError ('cannot call app.mount () in __mount__ () hook. move to __setup__ () hook')

    def have_mounted (self):
        # _mount () collects mounted_funcs
        for mounted, params in self._mounted_funcs:
            self.run_hook (mounted, params)
        self._mounted_funcs = []

    def mount_funcs (self):
        for mount_func, params in self._mount_funcs:
            fspec = inspect.getfullargspec (mount_func)
            if len (fspec.args) == 1:
                mount_func (self)
            else:
                mount_func (self, params)

            if 'point' in params:
                self.log ("- {} mounted to {}".format (tc.cyan (mount_func.__name__), tc.grey (self.mount_p [:-1] + params ['point'])), "info")
            else:
                self.log ("- {} mounted".format (tc.cyan (mount_func.__name__)), "info")

    def mount_nested (self):
        # within __mount__
        for module in list (sys.modules.values ()):
            if module in self.reloadables:
                continue
            modpath = self.get_modpath (module)
            if not modpath:
                continue
            for package_dir in self._package_dirs:
                if modpath.startswith (package_dir):
                    self._mount (module)
                    break

    def remount (self, module):
        self.setup (module)
        self._mount (module)
        self.have_mounted ()

    def setup (self, module):
        options = copy.deepcopy (self.mount_params.get (module, {}))
        try:
            setup_func = getattr (module, '__setup__')
        except AttributeError:
            return
        self.run_hook (setup_func, options)
        return setup_func

    def mount (self, maybe_point = None, *modules, **kargs):
        self.auto_mount = False # set to explicit mount mode
        if maybe_point or maybe_point == '':
            if isinstance (maybe_point, str):
                assert maybe_point == "" or maybe_point.startswith ("/"), "mount point should be balnk or startswith `/`"
                kargs ["point"] = maybe_point
            else:
                modules = (maybe_point,) + modules

        if self._current_mount_options:
            inherited_options = copy.deepcopy (self._current_mount_options [-1])
            # called in __setup__ hook, make sure sub path mount
            kargs ['point'] = inherited_options ['point'] + kargs ['point']
            if kargs ['point'].endswith ('//'):
                kargs ['point'] = kargs ['point'][:-1]
            if kargs ['point'].startswith ('//'):
                kargs ['point'] = kargs ['point'][1:]
            inherited_options.update (kargs)

        else:
            inherited_options = kargs

        self._current_mount_options.append (inherited_options)
        try:
            for module in modules:
                if isinstance (module, FunctionType):
                    self._mount_funcs.append ((module, inherited_options))
                    continue
                self.mount_params [module] = (inherited_options)
                setup_func = self.setup (module)
                mount_func = None
                for hook in self.MOUNT_HOOKS:
                    if hasattr (module, hook):
                        mount_func = getattr (module, hook)
                        break

                if not setup_func:
                    assert mount_func, "__mount__ hook doesn't exist"

                if mount_func:
                    self.add_package_dir (os.path.dirname (self.get_modpath (module)))
                    if module not in self.mount_params:
                        self._mount_order.append (module)

        finally:
            self._current_mount_options.pop (-1)

    mount_with = decorate_with = mount

    def umount (self, *modules):
        _umounted_funcs = []
        for module in reversed (modules):
            umount_func = None
            for hook in self.UMOUNT_HOOKS:
                if hasattr (module, hook):
                    umount_func = getattr (module, hook)
                    break

            if umount_func:
                try:
                    self.run_hook (umount_func)
                except:
                    self.traceback ()

            if hasattr (module, "__umounted__"):
                _umounted_funcs.append (getattr (module, "__umounted__"))
            # self.log ("- unmounted %s" % tc.cyan (module.__name__), "info")

        for umounted in _umounted_funcs:
            try:
                self.run_hook (umounted)
            except:
                self.traceback ()

    def umount_all (self):
        self.umount (*tuple (self.mount_params.keys ()))
    dettach_all = umount_all

    def _reload (self):
        reloaded = 0
        for module in list (self.reloadables.keys ()):
            try:
                fi = self.get_file_info (module)
            except FileNotFoundError:
                del self.reloadables [module]
                continue
            if self.reloadables [module] == fi:
                continue

            self.log ("- reloading service, %s" % module.__name__, "info")
            for each in self.service_roots:
                # reinstead package root for path finder
                sys.modules [each.__name__] = each

            if hasattr (module, "__reload__"):
                self.run_hook (getattr (module, "__reload__"))

            try:
                newmodule = reload (module)
            except:
                self.log ("- reloading failed. see exception log, %s" % module.__name__, "fatal")
                raise

            reloaded += 1
            self._current_function_specs = {}
            self.umount (module)
            del self.reloadables [module]
            self.remount (newmodule)

            self._reload_objects (newmodule)
            if hasattr (newmodule, "__reloaded__"):
                self.run_hook (getattr (module, "__reloaded__"))

        return reloaded

    def maybe_reload (self):
        with self.lock:
            if self._reloading or time.time () - self.last_reloaded < 1.0:
                return
            self._reloading = True

        try:
            self._reload () and self.load_jinja_filters ()
        finally:
            with self.lock:
                self.last_reloaded = time.time ()
                self._reloading = False

    def run_hook (self, fn, opts = {}):
        class Context:
            def __init__ (self, app):
                self.app = app
                self.mount_options = {}

        def display_warning ():
            warn (f'use {fn.__name__} (context)', DeprecationWarning)

        if not opts:
            module = sys.modules [fn.__module__]
            if hasattr (module, "__options__"):
                opts = module.__options__

        nargs = len (inspect.getfullargspec (fn).args)
        as_proto = fn.__name__ in ('__setup__', '__umounted__')

        options = self.build_opts (as_proto)
        opts and options.update (opts)

        if self._wasc:
            context = options ["Context" if as_proto else "context"]
        else:
            context = Context (self)
        context.app = self
        context.mount_options = options

        if nargs == 1:
            if skitai.version_info >= (0, 53):
                args = (context,)
            else:
                display_warning ()
                args = (self,)
        elif nargs == 2:
            if skitai.version_info >= (0, 53):
                args = (context, self)
            else:
                display_warning ()
                args = (self, options)
        elif nargs == 3:
            args = (context, self, options)

        self._allied_type = self._mro.get (fn.__module__)
        if self._wasc:
            self._wasc.execute_function (fn, args)
        else:
            fn (*args)
        self._allied_type = None

        try:
            del args [0].mount_options
        except AttributeError:
            pass

    def build_opts (self, as_proto):
        d = dict (
            use_reloader = self.use_reloader,
            debug = self.debug
        )
        if as_proto:
            d ["Context"] = self._wasc
        else:
            d ["context"] = self._was_in_main_thread
        return d
