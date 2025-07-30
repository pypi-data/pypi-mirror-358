import sys, os
from rs4 import pathtool
from .commands import describe_models, export_models
try:
    from dotenv import load_dotenv; load_dotenv (os.path.join (os.getcwd (), '.env'))
except ImportError:
    pass

BACKEND_DIR = 'backend'

APP_INIT = """import os
import sys

def load_models ():
    from rs4.misc import django_standalone; django_standalone.activate ()

if 'skitai' not in sys.modules:
    load_models ()

BASE_DIR = os.path.dirname (__file__)

def __config__ (pref):
    import skitai
    from rs4 import pathtool
    from .orm import settings

    skitai.mount ("/", os.path.join (BASE_DIR, 'orm/wsgi:application'), pref, name = 'orm')
    for its in ('STATIC', 'MEDIA'):
        url, root = getattr (settings, f"{its}_URL"), getattr (settings, f"{its}_ROOT")
        pathtool.mkdir (root)
        skitai.mount (url, root)
        skitai.log_off (url)

def __app__ ():
    import atila
    return atila.Atila (__name__)

def __setup__ (context, app):
    import skitai
    from django.conf import settings

    settings.DEBUG = skitai.is_devel ()
    app.config.SETTINGS = settings
    app.secret_key = settings.SECRET_KEY


def __mount__ (context, app):
    @app.route ("/ping")
    def ping (context):
        return 'pong'
"""

ATILA_INIT = """
def __app__ ():
    import atila
    return atila.Atila (__name__)

def __mount__ (context, app):
    @app.route ("/ping")
    def ping (context):
        return 'pong'
"""

SKITAID = f"""#! /usr/bin/env python3

import skitai
import %s # make sure behind skitai

with skitai.preference () as pref:
    pref.config.MAX_UPLOAD_SIZE = 1 * 1024 * 1024 * 1024
    skitai.mount ('/', %s, pref)

skitai.run (ip = '0.0.0.0', port = 5000, name = 'atila-app', workers = 1)
""" % (BACKEND_DIR, BACKEND_DIR)

def customized_management (project_dir):
    def decorator(manage_main):
        def fixed ():
            APP_ROOT = os.path.abspath (f'./{BACKEND_DIR}/orm')
            try:
                cmd = sys.argv [1]
            except IndexError:
                return manage_main ()

            if cmd == 'runserver':
                os.system ("./skitaid.py --devel")
                return

            if cmd == 'describe_models':
                return describe_models.execute (project_dir)
            if cmd == 'export_models':
                return export_models.execute (project_dir)

            if cmd in ('startproject', 'startatila'):
                assert not os.path.isfile ("./skitaid.py"), "skitaid.py already exists"
                with open (os.path.join ("./skitaid.py"), "w") as f:
                    f.write (SKITAID)
                pathtool.mkdir (f"./{BACKEND_DIR}")
                PROJECT_ROOT = os.path.abspath (f'./{BACKEND_DIR}')

                if cmd == 'startatila':
                    with open (os.path.join (PROJECT_ROOT, "__init__.py"), "w") as f:
                        f.write (ATILA_INIT)
                    return

                with open (os.path.join (PROJECT_ROOT, "__init__.py"), "w") as f:
                    f.write (APP_INIT)

                assert len (sys.argv) == 2, "do not give [project name]"
                sys.argv.append ("orm")
                sys.argv.append (PROJECT_ROOT)
                manage_main ()
                os.remove (os.path.join (PROJECT_ROOT, "manage.py"))
                os.mkdir (os.path.join (PROJECT_ROOT, "orm", "static"))
                os.mkdir (os.path.join (PROJECT_ROOT, "orm", "media"))

                with open (os.path.join (PROJECT_ROOT, "orm", "settings.py"), "r") as f:
                    d = f.read ()
                with open (os.path.join (PROJECT_ROOT, "orm", "settings.py"), "w") as f:
                    d = d.replace ("orm.urls", "backend.orm.urls")
                    d = d.replace ("orm.wsgi.application", "backend.orm.wsgi.application")
                    d = d.replace ("parent.parent", "parent")
                    d += "\nimport os\nSTATIC_ROOT = os.getenv ('STATIC_ROOT') or os.path.join (BASE_DIR, 'static/')\n\n"
                    d += "MEDIA_URL = '/media/'\nMEDIA_ROOT = os.path.join(BASE_DIR, 'media/')\n"
                    f.write (d)

                with open (os.path.join (PROJECT_ROOT, "orm", "wsgi.py"), "r") as f:
                    d = f.read ()
                with open (os.path.join (PROJECT_ROOT, "orm", "wsgi.py"), "w") as f:
                    f.write (d.replace ("orm.settings", "backend.orm.settings"))
                with open (os.path.join (PROJECT_ROOT, "orm", "urls.py"), "r") as f:
                    d = f.read ()

                return

            APP_ROOT = os.path.abspath (f'./{BACKEND_DIR}/orm')
            os.chdir (APP_ROOT)

            if cmd == 'startapp':
                path = os.path.join (APP_ROOT, sys.argv [2])
                pathtool.mkdir (path)
                sys.argv.insert (3, path)

            manage_main ()

            if cmd == 'startapp':
                path = os.path.join (APP_ROOT, sys.argv [2])
                with open (os.path.join (path, 'apps.py')) as f:
                    d = f.read ()
                    d = d.replace ("name = '", f"name = '{project_dir}.orm.")
                with open (os.path.join (path, 'apps.py'), 'w') as f:
                    f.write (d)
                os.remove (os.path.join (path, 'tests.py'))
                os.remove (os.path.join (path, 'views.py'))
        return fixed

    if not isinstance (project_dir, str):
        return decorator (project_dir)

    global BACKEND_DIR
    BACKEND_DIR = project_dir

    return decorator