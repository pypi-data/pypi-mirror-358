import argparse
import sys
from ._utils import find_models

def execute (project_dir):
    import pandas
    import numpy as np
    import rs4
    from rs4.misc import django_standalone; django_standalone.activate ()

    parser = argparse.ArgumentParser ()
    parser.add_argument ('-i', '--include-apps', nargs='+', default = [])
    parser.add_argument ('-e', '--exclude-apps', nargs='+', default = [])
    parser.add_argument ('-m', '--models', nargs='+', default = [])

    args = parser.parse_args (sys.argv [2:])

    for app, model in find_models (project_dir, args.include_apps, args.exclude_apps):
        if args.models and model.__name__ not in args.models:
            continue
        output = f'{app}.{model.__name__}.csv'
        rows = []
        df = pandas.DataFrame ({fd.name: [] for fd in model._meta.fields})
        print (f'writing {output}')
        for item in rs4.tqdm (model.objects.all ()):
            row = {}
            for fd in model._meta.fields:
                val = getattr (item, fd.name)
                if fd.get_internal_type () == 'ForeignKey' and val:
                    val = val.id
                row [fd.name] = np.nan if val is None else val
            df.loc [len (df)] = row
        df.to_csv (output, index = False)
