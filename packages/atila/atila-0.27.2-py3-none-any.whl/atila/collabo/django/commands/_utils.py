import os
import sys
from django.db import models
import re

def find_models (project_dir, include_apps, exclude_apps):
    _models = set ()
    orm_dir = os.path.join (project_dir, 'orm')
    for app in os.listdir (orm_dir):
        app_dir = os.path.join (orm_dir, app)
        if app.startswith ('_'):
            continue
        if not os.path.isdir (app_dir):
            continue
        model_file = os.path.join (app_dir, 'models.py')
        if not os.path.isfile (model_file):
            continue
        with open (model_file) as f:
            file_content = f.read ()
        try:
            mod = sys.modules [f'{project_dir}.orm.{app}.models']
        except KeyError:
            continue # not installed app
        for model_name in dir (mod):
            model = getattr (mod, model_name)
            try:
                if not issubclass (model, models.Model):
                    continue
            except TypeError:
                continue

            rx_class = re.compile (rf'^class\s+{model_name}', re.M|re.S)
            if not rx_class.search (file_content):
                continue

            if (app, model) in _models:
                continue

            skip = False
            for e in exclude_apps:
                if e in app:
                    skip = True
                    break
            if skip: continue

            for e in include_apps:
                if e not in app:
                    skip = True
                    break
            if skip: continue
            _models.add ((app, model))

    return sorted (list (_models), key = lambda x: (x [0], x [1].__name__))