import argparse
import sys
from ._utils import find_models

def execute (project_dir):
    from rs4.misc import django_standalone; django_standalone.activate ()
    from rs4.webkit import markdown

    parser = argparse.ArgumentParser ()
    parser.add_argument ('-o', '--output', default = None)
    parser.add_argument ('-q', '--quiet', action = 'store_true')
    parser.add_argument ('-i', '--include-apps', nargs='+', default = [])
    parser.add_argument ('-e', '--exclude-apps', nargs='+', default = [])
    args = parser.parse_args (sys.argv [2:])

    md = markdown.Markdown ()
    md.writeln ('# Table Specification')
    for app, model in find_models (project_dir, args.include_apps, args.exclude_apps):
        md.writeln (f'## {model.__name__}')
    md.writeln ('\n\n\n\n\n')

    for app, model in find_models (project_dir, args.include_apps, args.exclude_apps):
        md.writeln ('<div style="page-break-after: always"></div>\n')
        md.writeln (f'## {model.__name__}')
        md.writeln (f'**{app.replace ("_", " ").title ()} / {model._meta.verbose_name_plural.title ()}**')
        if model.__doc__:
            indent = -1
            doc = []
            for idx, line in enumerate (model.__doc__.split ('\n')):
                if indent == -1:
                    if not line.strip ():
                        doc.append ('')
                        continue
                    else:
                        indent = len (line) - len (line.lstrip ())
                        doc.append (line [indent:])
                else:
                    doc.append (line [indent:])

            doc = '\n'.join (doc)
            md.writeln (f'\n{doc}')

        rows = []
        for fd in model._meta.fields:
            row = {
                "name": fd.name,
                "type": fd.get_internal_type (),
                "max length": fd.max_length or ' ',
                "primary": 'Yes' if fd.primary_key else ' ',
                "null": 'Yes' if fd.null else 'No',
                "default": fd.get_default () or ' ',
                "related": fd.related_model.__name__ + '.id' if fd.related_model else ' ',
                "comment": fd.help_text.replace ("|", " ")
            }
            rows.append (row)

        md.write_table (rows)

    if args.output is None:
        not args.quiet and print (md.close ())
    else:
        with open (args.output, 'w') as f:
            f.write (md.close ())