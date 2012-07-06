import argparse
from os import path
import json
import os
import shutil
from fnmatch import fnmatch
import util
from jinja2 import Environment
from datetime import datetime

SKEL_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'skels')
PLUGIN_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'plugins')
CONFIG_FILE = path.abspath(path.expanduser('~/.packstrap'))

default_options = {
    '--author' : dict(flag='-a', dest='author', help='Name of the author of this project (default: %(default)s)'),
    '--author-email' : dict(flag='-e', dest='author_email', help='Email of the author of this project (default: %(default)s)'),
    '--version' : dict(flag='-v', dest='version', help='Version of this project (default: %(default)s)', default='0.7.0'),
    '--skeleton' : dict(flag='-s', dest='skeleton', help='The skeleton to base the project on (default: %(default)s)', default='default'),
    '--plugin' : dict(flag='-p', dest='plugins', help='Plugins to include in this project (default: %(default)s)', action='append'),
}

def get_defaults():
    if path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}

def set_defaults(args):
    defaults = get_defaults()
    changes = False
    for opt in default_options.values():
        key = opt['dest']
        v = getattr(args, key)
        if v:      
            if key == 'plugins':
                plugins = os.listdir(PLUGIN_DIR)
                for plugin in v:
                    if plugin not in plugins:
                        raise Exception('Invalid plugin %s' % plugin)

            changes = True      
            defaults[key] = v
        
    if changes:
        with open(CONFIG_FILE, 'w') as file:
            json.dump(defaults, file, indent=2)

    print(json.dumps(get_defaults(), indent=2))

def list_plugins(args):
    print('\n'.join(os.listdir(PLUGIN_DIR)))

class SyncListener(util.SyncListener):
    def __init__(self, template_env, context):
        self.context = context
        self.template_env = template_env

    def copied(self, srcroot, srcname, dstroot, dstname):
        """
        Called for each file that is copied
        """
        if srcname.endswith('.tmpl'):
            print('  Evaluating template %s' % srcname)
            # Source was a template, lets open the file and parse it as a template
            with open(path.join(dstroot, dstname), 'r') as file:
                template = self.template_env.from_string(file.read())

            with open(path.join(dstroot, dstname), 'w') as file:
                file.write(template.render(**self.context))

    def exists(self, srcroot, srcname, dstroot, dstname):
        """
        Called when destination path already exists.

        Retun True to overwrite, False to skip.
        """
        if self.context['force']:
            print('  %s/%s already exists but forcing overwrite' % (dstroot, dstname))
            return True
        else:
            print('  %s/%s already exists, skipping' % (dstroot, dstname))
            return False

    def copy(self, srcroot, srcname, dstroot, dstname):
        """
        Called when destination path does not already exists.

        Retun True to write, False to skip.
        """        
        print('  %s/%s is new, syncing' % (dstroot, dstname))
        return True

    def destpath(self, srcroot, srcname, dstroot, dstname):
        """
        Called for each file before each sync operation. Here you can rewrite
        the destination name if need be.        

        Retuns a tuple of dstroot, dstname
        """
        if dstname.endswith('.tmpl'):
            # File is a template, remove template extension
            dstname = dstname[:-5]

        return dstroot, dstname.format(**self.context)
            
def _empty_string(val):
    if val is None:
        return ''
    return val

def create(args):
    args.modname = args.modname if args.modname else args.name
    args.dir = path.abspath(path.expanduser(args.dir))

    print('Creating %s project %s at %s...' % (args.skeleton, args.name, args.dir))

    template_env = Environment(finalize=_empty_string)
    sync_listener = SyncListener(template_env, vars(args))

    util.synctree(path.join(SKEL_DIR, args.skeleton), args.dir, listener=sync_listener)

    if args.plugins:
        for plugin in args.plugins:
            print('Including plugin %s...' % plugin)
            util.synctree(path.join(PLUGIN_DIR, plugin), args.dir, listener=sync_listener)        

def add_package_config_args(parser):
    defaults = get_defaults()
    for k, opt in default_options.iteritems():
        if opt['dest'] in defaults:
            default = defaults[opt['dest']]
            opt['default'] = default
        
        args = [k]
        if 'flag' in opt:
            args.append(opt['flag'])
            opt = opt.copy()
            del opt['flag']

        parser.add_argument(*args, **opt)

    return parser

def main():
    parser = argparse.ArgumentParser(description='Create a Python package project')
    


    subparsers = parser.add_subparsers()  
    parser_default = subparsers.add_parser('defaults', help='Set project defaults for new projects')
    parser_default.set_defaults(func=set_defaults)

    add_package_config_args(parser_default.add_argument_group('config'))


    parser_create = subparsers.add_parser('create', help='Create a new project')
    parser_create.add_argument('name', help='Name of the project', metavar='NAME')
    parser_create.add_argument('dir', help='Directory to create project in (default: %(default)s)', default='.', metavar='DIRECTORY', nargs='?')
    parser_create.add_argument('-y', '--copyright-year', help='Copyright year (default: %(default)s)', type=int, dest='copyright_year', default=datetime.now().year, metavar='YEAR')
    parser_create.add_argument('--force', help='Force overwriting existing files', action='store_true')
    parser_create.set_defaults(func=create)

    cfg_parser = add_package_config_args(parser_create.add_argument_group('config'))
    cfg_parser.add_argument('--modname', help='Name of the Python module if different from project name.')
    cfg_parser.add_argument('--description', help='Project description.') 

    parser_plugins = subparsers.add_parser('plugins', help='List availible plugins')
    parser_plugins.set_defaults(func=list_plugins)

    args = parser.parse_args()
    
    if getattr(args, 'plugins', None):
        args.plugins = list(set(args.plugins))

    args.func(args)

if __name__ == '__main__':
    main()
