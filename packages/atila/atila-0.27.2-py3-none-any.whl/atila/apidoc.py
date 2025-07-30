import os
import pickle
from urllib.parse import urlparse
import sys
import json
import re
from rs4 import pathtool
from rs4.attrdict import CaseInsensitiveDict
from pprint import pprint

class API:
  def __init__ (self, resource_id):
    self.resource_id = resource_id
    self.endpoints = set ()
    self.routeopt = {}
    self.parameter_requirements = {}
    self.auth_requirements = []
    self.urlspec = {}
    self.doc = None
    self.desc = ""
    self.METHODS = {}
    self.out = None

  VALID_METHODS = ('GET', 'POST', 'PATCH', 'PUT', 'DELETE')
  def add_call (self, method, url, status_code, reason, reqh, reqd, resh, resd, spec):
    from rs4.protocols.sock.impl.http import http_util

    if not self.endpoints:
      self.routeopt = spec ["routeopt"]
      self.parameter_requirements = spec.get ("parameter_requirements")
      self.urlspec = spec ["urlspec"]
      self.auth_requirements = spec ["auth_requirements"]
      self.doc = spec ["doc"]
      self.desc = spec ["id"].split (":")[-1].replace ("_", " ").title ()
      for each in self.routeopt ['methods']:
        if each in self.VALID_METHODS:
          self.METHODS [each] = {}
    endpoint = self.get_endpoint (spec ['current_request']['uri'], spec ['routeopt']['route'])
    self.endpoints.add (endpoint)

    endpoint = self.get_endpoint (spec ['current_request']['uri'], spec ['routeopt']['route'])
    self.endpoints.add (endpoint)

    if method in self.METHODS:
      reqh = CaseInsensitiveDict (reqh)
      if status_code not in self.METHODS [method]:
        self.METHODS [method][status_code] = []
      if isinstance (reqd, str):
        if reqh.get ('content-type', '').startswith ('application/json'):
          reqd = json.loads (reqd)
        else:
          try:
            reqd = http_util.crack_query (reqd)
          except IndexError:
            pass

      reqd = self.squeeze (reqd)
      resd = self.squeeze (resd)
      for d in self.METHODS [method][status_code]:
        if d [3] == reqd:
          return
        if isinstance (d [3], dict) and set (d [3].keys ()) == set (reqd.keys ()):
          if d [5] == resd:
            return
        if method in ("GET", "DELETE") and d [0] == url:
          return
      self.METHODS [method][status_code].append ((url, reason, reqh, reqd, resh, resd, spec))

  def get_endpoint (self, endpoint, route):
    parts = urlparse (endpoint)
    a = parts.path.split ("/")
    if not route:
      return parts.path
    b = route.split ("/")
    if b [-1].startswith ("<path:"):
      s = parts.path.rfind ("/".join (b [:-1]))
      return parts.path [:-s] + route
    else:
      return "/".join (a [:-(len (b) - 1)] + b [1:])

  def squeeze (self, d):
    if isinstance (d, dict):
      d_ = {}
      for k, v in list (d.items ()):
        if isinstance (v, (dict, list, str)):
          d_ [k] = self.squeeze (v)
        else:
          d_ [k] = v
      return d_
    elif isinstance (d, list):
      d_ = []
      for each in d:
        d_.append (self.squeeze (each))
      return d_
    elif isinstance (d, str) and len (d) > 80:
      return d [:77] + '...'
    return d

  def to_dict (self, d):
    from rs4.protocols.sock.impl.http import http_util
    return http_util.crack_query (d)

  def write (self, d):
    self.out and self.out.write (d)

  def writeln (self, line = ''):
    self.write (line + '  \n')

  def writebl (self, data, code = 'json'):
    self.write ("\n```{}\n{}\n```\n\n".format (code, data))

  def writep (self, line = ''):
    self.write (line + '\n\n')

  RX_INDENT = re.compile (r'^\s+')
  def writemd (self, md):
    lines = []
    indent = 0
    for line in md.split ("\n"):
      if not lines:
        if not line:
          continue
        m = self.RX_INDENT.match (line)
        indent = indent = 0 if not m else len (m.group ())
      lines.append (line [indent:])
    self.writep ('\n'.join (lines))

  def chiplist (self, l):
    return "`{}`".format ("`, `".join (sorted (l)))

  def argslist (self, part, ups, qps):
    if 'argspecs' not in self.urlspec:
      return
    if not self.urlspec ['argspecs'].get (part):
      return
    if not ups and not qps:
      return

    self.writeln ("### Parameters")
    self.writeln ("")
    argspecs = self.urlspec ['argspecs'][part]

    for name, spec in argspecs.items ():
      if 'required' not in spec:
        spec ['required'] = False

    if ups:
      self.writeln ("#### Path Parameters")
      self.write_params (argspecs, ups)
    if qps:
      self.writeln ("#### URL / Data Parameters")
      self.write_params (argspecs, exclude = ups)

  def write_params (self, argspecs, include = [], exclude = []):
    for name, spec in sorted (argspecs.items (), key = lambda x: (-int (x [1]['required']), x [0])):
      if include and name not in include:
        continue
      if exclude and name in exclude:
        continue
      if spec.get ('protected'):
        continue
      required = spec.get ('required')
      if required:
        self.writeln (f"- **{name}**")
      else:
        self.writeln (f"- **{name}** *(optional)*")

      for k, v in spec.items ():
        if k == 'required':
          continue
        if v is None:
          v = 'null'
        elif isinstance (v, (list, tuple)):
          v = ' | '.join (list (map (str, v)))
          v = f'[ {v} ]'
        self.writeln (f"  - {k}: *{v}*")
    self.writeln ("")

  def argslist_v1 (self, part):
    if not self.parameter_requirements.get (part):
      return

    # TODO: REPLACE with routeopt ['aegspec']
    requirements = self.parameter_requirements [part]
    alls = {}
    for param, cond in requirements.items ():
      if isinstance (cond, list) and param.find ('__') == -1:
        for each in cond:
          if param not in alls:
            alls [each] = []
          alls [each].append (param [:-1])

      else:
        parts = param.split ('__')
        param = parts [0]
        if param not in alls:
          alls [param] = []

        if isinstance (cond, str) and cond.startswith ('<class'):
          cond = 'type `{}`'.format (cond [8:len (cond) - 2])
        elif isinstance (cond, (list, tuple)):
          cond = "|".join (map (str, cond))

        if len (parts) == 1:
          if hasattr (cond, 'pattern'):
            alls [param].append ('pattern `{}`'.format (cond.pattern))
          else:
            alls [param].append (cond)
          continue

        if len (parts) == 3:
          alls [param].append ('{} `{}`'.format (parts [1], cond))
          continue

        op = parts [1]
        alls [param].append ('{} `{}`'.format (op, cond))

    self.writeln ("**{}Parameters Requirements**:".format (part != 'ARGS' and part + ' ' or ''))
    for name, reqs in alls.items ():
      self.writeln ("  - {}: {}".format (name, ", ".join (reqs)))

  def render (self, out):
    self.out = out
    #{'methods': ['OPTIONS', 'GET', 'DELETE'], 'route': '/<name>', 'args': ['name', 'where'], 'defaults': {'where': 'latest'}, 'urlargs': 1}
    for method in self.VALID_METHODS:
      if method not in self.METHODS:
        continue
      if not self.METHODS [method]:
        continue

      self.writep ('<div style="page-break-after: always"></div>\n')
      self.writep ("## `{}` {}".format (method, self.chiplist ([each.replace ('<', ':').replace ('>', '') for each in self.endpoints])))
      self.writemd (self.doc) if self.doc else self.writep (self.desc)
      self.writep ('### Resource ID\n{}'.format (self.resource_id))
      # self.writep ("**Methods Allowed**: {}".format (self.chiplist (self.routeopt ['methods'])))

      ups, qps = [], []
      if self.routeopt.get ('urlargs'):
        for k in self.routeopt ['args'][:self.routeopt ['urlargs']]:
          ups.append (k)

      qss = self.parameter_requirements.get ("ARGS", {}).get ('required', [])
      if not qss:
        qss = self.routeopt ['args'][self.routeopt.get ('urlargs', 0):]

      if qss:
        defaults = self.routeopt.get ('defaults', {})
        for arg in qss:
          qps.append (arg)

      self.argslist ('ARGS', ups, qps)
      self.writeln ()

      auth = 'No'
      perms = []
      testpass = None
      login = False
      for t, d in self.auth_requirements:
        if t == "permission":
          if auth == 'No':
            auth = "Yes"
          perms = d or []
        elif t == "login":
          login = True
        elif t == "testpass":
          testpass = d
        elif t == "auth":
          auth = d

      auth and self.writeln ("### Authorization Required\n{}".format (auth))
      perms and self.writeln ("### Permission Required\n{}".format (self.chiplist (perms)))
      testpass and self.writeln ("### Test Pass Required\n`{}`".format (testpass))
      login and self.writeln ("### Login Required\nYes")
      self.writeln ()

      if method in ("POST", "PUT", "PATCH"):
        self.argslist ('JSON', ups, qps)
        self.argslist ('FORM', ups, qps)
      else:
        self.argslist ('URL', ups, qps)
      self.writeln ()

      self.writep ("### Request / Response Examples")
      idx = [0, 0]
      for status_code in sorted (self.METHODS [method].keys ()):
        for url, reason, reqh, reqd, resh, resd, spec in self.METHODS [method][status_code]:
          if 200 <= status_code < 300:
            idx [0] += 1
            if idx [0] >= 3:
              continue
            self.writep (f"#### Success Case #{idx [0]}")
          else:
            idx [1] += 1
            self.writep (f"#### Error Case #{idx [1]}")

          self.writep (f"##### Request")
          self.writeln ("**_URL_**: `{}`".format (spec ["current_request"]['uri']))
          self.writeln ("**_Header_**:")
          self.writebl ('\n'.join ([f"{k}: {v}" for k, v in reqh.items ()]), 'http')

          if reqd:
            self.writeln ("**_Request Data_** ({})".format (reqh.get ('content-type')))
            self.writebl (json.dumps (reqd, ensure_ascii = False, indent = 2))
          self.writeln ()

          self.writep (f"##### Response")
          self.writeln ("**_Status_**: `{} {}`".format (status_code, reason))
          # self.writeln ("**_Header_**:")
          # self.writebl ('\n'.join ([f"{k}: {v}" for k, v in resh.items ()]), 'http')

          if resd:
            self.writeln ("**_Response Data_** ({})".format (resh.get ('content-type')))
            self.writebl (json.dumps (resd, ensure_ascii = False, indent = 2))

          self.writeln ()

RX_ALNUM = re.compile ('[^-_a-zA-Z0-9]')
apis = {}
def build_doc (output = None):
  if not os.path.isdir (".webtest_log/v"):
    sys.stdout.writep ("apidoc.build_doc: no log directory, skipped.")
    return

  for fn in os.listdir (".webtest_log/v"):
    try:
      with open (os.path.join (".webtest_log/v", fn), 'rb') as f:
        method, url, status_code, reason, reqh, reqd, resh, resd, spec = pickle.load (f)
    except EOFError:
      continue

    if not spec:
      continue
    resource_id = spec ['id']
    if resource_id not in apis:
      apis [resource_id] = API (resource_id)
    apis [resource_id].add_call (method.upper (), url, status_code, reason, reqh, reqd, resh, resd, spec)

  if output:
    pathtool.mkdir (os.path.dirname (output))
    out = open (output, 'w')
  else:
    out = sys.stdout

#get-apiforecastsapiforecastsdate
#get-apiforecasts-apiforecastsdate


  out.write ("## Table of Content\n\n")
  sorted_apis = sorted (apis.items (), key = lambda x: sorted (list (x [1].endpoints))[0])
  for idx, (resource_id, api) in enumerate (sorted_apis):
    for method in API.VALID_METHODS:
      if not api.METHODS.get (method):
        continue
      out.write ("1. [**`{}`**".format (method))
      end_points = " | ".join (list (api.endpoints)).replace ("<", ":").replace (">", "")
      out.write (" {}](#{}-{})".format (end_points, method.lower (), RX_ALNUM.sub ('', api.chiplist (list (api.endpoints)).replace (' ', '-')).lower ()))
      out.write (" *{}*".format (api.desc))
      out.write ("\n")

  for resource_id, api in sorted_apis:
    api.render (out)
    out.write ("\n\n")

  if output:
    out.close ()

# logging spec -----------------------------------------------

def truncate_log_dir (remove_only = False):
  from rs4 import pathtool
  import shutil

  if os.path.isdir (".webtest_log/v"):
      shutil.rmtree (".webtest_log/v")
  if remove_only:
      return
  pathtool.mkdir (".webtest_log/v")

SPECS = 0
if os.path.isdir (".webtest_log/v"):
  for fn in os.listdir (".webtest_log/v"):
    SPECS = max (SPECS, int (fn [:-5]))

def log_spec (method, url, status_code, reason, reqh, reqd, resh, resd):
    global SPECS

    try:
        spec = resd.pop ("__spec__")
    except (AttributeError, KeyError):
        return
    # pprint (spec)
    if not os.path.isdir (".webtest_log/v"):
      return
    if SPECS > 1000:
      truncate_log_dir ()
      SPECS = 0
    SPECS += 1

    resd_ = {}; resd_.update (resd) # convert to native dict
    with open (os.path.join (".webtest_log/v", '{:04d}.spec'.format (SPECS)), 'wb') as f:
        pickle.dump ((method, url, status_code, reason, reqh, reqd, resh, resd_, spec), f)
