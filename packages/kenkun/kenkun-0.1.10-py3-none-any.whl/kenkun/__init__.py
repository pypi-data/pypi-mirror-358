from datetime import datetime as dt

from kenkun.util.fields import get_list_from_metadata

import argparse
import dataclasses
import errno
import importlib.util
import jinja2 as jj2
import os
import shutil
import stat
import subprocess
import sys

# open user directory
user_dir = os.path.expanduser("~")

# check if kenkun directory exists
kenkun_dir = os.path.join(user_dir, '.kenkun')

config_path = os.path.join(kenkun_dir, 'kenkun.cfg')

# if not, create it
if not os.path.exists(kenkun_dir):
    os.makedirs(kenkun_dir)

    # create kenkun.cfg file
    with open(config_path, 'w') as f:
        f.write("[kenkun]\n")
        f.write("GITHUB_URL = 'https://github.com/sylvioazevedo'")

# read GITHUB_URL from kenkun.cfg
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        for line in f:
            if line.startswith('GITHUB_URL'):
                GITHUB_URL = line.split('=')[1].strip().strip("'\"")        


# set python path as current directory
sys.path.insert(0, os.path.abspath(os.getcwd()))

ACTION_CHOICES = [
    'create', 'generate', 'run', 'test', 'delete',
    'all', 'views', 'controller', 'domain', 'incorporate'
]

# constants
template_path = "./kenkun/templates"

def load_module_from_file(file_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def render_template(domain, fields, template, type: str='view'):

    tl = jj2.FileSystemLoader(searchpath=f'{template_path}/{type}')
    te = jj2.Environment(loader=tl)

    te.globals.update({
        'get_list_from_metadata': get_list_from_metadata,
        'dt': dt
    })

    tpl = te.get_template(f'{template}.tpl')

    outputText = tpl.render(domain=domain, fields=fields)    
    
    if type == 'view':
        target_path = f"./{type}/{domain}"
        
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        target_file = f"{target_path}/{template}.py"

    elif type == 'controller':
        target_path = f"./{type}"
        
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        target_file = f"{target_path}/{domain}_{type}.py"

    else:
        target_path = f"./{type}"
        
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        target_file = f"{target_path}/{domain}.py"


    with open(target_file, "w") as f:
        f.write(outputText) 
        f.flush()

    print(f"Generated {type} for domain {domain}: {target_file}")

def load_fields(domain: str):

    domain_file_path = f"./domain/{domain}.py"
    module_name = os.path.splitext(os.path.basename(domain_file_path))[0]
    
    # Load the module
    domain_module = load_module_from_file(domain_file_path, module_name)
    
    # Access an object from the module (e.g., a class or function
    _c = getattr(domain_module, domain.title(), None)

    if not _c:
        raise Exception(f"Object 'ObjectName' not found in {domain_file_path}")
    
    fields = dataclasses.fields(_c)

    return fields
    
def generate_views(domain: str):

    fields = load_fields(domain)

    # generate crud views
    print(f'Creating views for domain: {domain}')
    render_template(domain, fields, '__init__')
    render_template(domain, fields, 'create')
    render_template(domain, fields, 'show')
    render_template(domain, fields, 'edit')

    print(f"Generated {domain} views")

def generate_controller(domain: str):

    fields = load_fields(domain)

    # generate crud views
    print(f'Creating controller for domain: {domain}')
    render_template(domain, fields, 'controller', 'controller')
    print(f"Generated {domain} controller")

def generate_domain(domain: str):    

    # generate crud views
    print(f'Creating : {domain}')
    render_template(domain, None, 'domain', 'domain')
    print(f"Generated {domain} domain")

def generate_all(domain: str):
    
    generate_views(domain)
    generate_controller(domain)

def incorporate(domain: str):

    # open app.py and insert a new route
    with open('./app.py', 'r') as f:
        lines = f.readlines()

    with open('./app.py', 'w') as f:
        for line in lines:
            if line.strip().startswith('# kenkun|controllers'):
                f.write(line)
                f.write(f"from controller.{domain}_controller import {domain}_app as {domain}_routes\n")                
                continue

            f.write(line)

        f.flush()

    # open app.py and isert a new route
    with open('./app.py', 'r') as f:
        lines = f.readlines()

    with open('./app.py', 'w') as f:
        for line in lines:            
            if line.strip().startswith('# kenkun|routes'):
                f.write(line)    
                f.write(f"    Mount('/{domain}', {domain}_routes, name='{domain}'),\n")
                continue

            f.write(line)  

        f.flush()  

    # incorporate the new route in left menu
    with open('./view/templates/left_menu.py', 'r') as f:
        lines = f.readlines()
    
    with open('./view/templates/left_menu.py', 'w') as f:
        for line in lines:
            if line.strip().startswith('# kenkun|left_menu'):
                f.write(line)
                f.write(f"            VerticalMenuItem('{domain.title()}s', icon='ti ti-point', href='/{domain}', active=session['active'] == '{domain.title()}s'),\n")
                continue

            f.write(line)

        f.flush()
    
    print(f"Added route for {domain} in app.py")

def main():

    # Argument parsing
    parser = argparse.ArgumentParser(description='Kenkun webapp generator')

    parser.add_argument('action', metavar='<action>', nargs="?", type=str, help=", ".join(ACTION_CHOICES), choices=ACTION_CHOICES)
    parser.add_argument('-a', '--appname', type=str, help='The application name')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')    
    parser.add_argument('-s', '--skeleton', type=str, help='The skeleton to generate', default='fh-vuexy-sa')

    parser.add_argument('-d', '--domain', type=str, help='The domain reference to generate the artifacts')

    args = parser.parse_args()

    # Variables
    action = args.action
    appname = args.appname
    skeleton = args.skeleton
    domain = args.domain

    print(f"Action: {action}")
    print(f"Appname: {appname}")
    print(f"Skeleton: {skeleton}")
    print(f"Domain: {domain}")

    # set python path as current directory
    os.environ['PYTHONPATH'] = os.getcwd()

    # show python path
    print(f"Python path: {os.path.dirname(os.path.realpath(__file__))}")

    # show current directory
    print(f"Current directory: {os.getcwd()}")   

    if action == 'create':

        # mark start time
        start = dt.now()

        if not appname:
            print("Appname is required")
            exit(1)

        # check if appname already exists
        if os.path.exists(appname):
            print(f"App {appname} already exists")
        else:
            print(f"Creating app {appname} with skeleton {skeleton}")

            # remove internal project files [.gitignore, .python-version, README.md, pyproject.toml, uv.lock]
            for file in ['.gitignore', '.python-version', 'README.md', 'pyproject.toml', 'uv.lock']:
                try:
                    os.remove(file)
                except FileNotFoundError:
                    pass            

            # assemble github url from selected sekleton
            url = f'{GITHUB_URL}/{skeleton}.git'

            print('Cloning skeleton from github...')
            print(f'URL: {url}')

            # init git repository
            proc = subprocess.Popen(['git', 'init'], stdout=subprocess.PIPE)            
            out, err = proc.communicate()

            # fork locally the skeleton from a git repository
            proc = subprocess.Popen(['git', 'remote', 'add', 'upstream', f"{url}"], stdout=subprocess.PIPE)            
            out, err = proc.communicate()

            print(out)
            print(err)
            
            proc = subprocess.Popen(['git', 'fetch', 'upstream'], stdout=subprocess.PIPE)            
            out, err = proc.communicate()

            print(out)
            print(err)

            # clone locally the skeleton from a git repository
            proc = subprocess.Popen(['git', 'checkout', 'master'], stdout=subprocess.PIPE)
            out, err = proc.communicate()

            print(out)
            print(err)

            # clone locally the skeleton from a git repository
            proc = subprocess.Popen(['git', 'merge', 'upstream/master'], stdout=subprocess.PIPE)
            out, err = proc.communicate()

            print(out)
            print(err)

        # Find replace |APPNAME| with appname in all files in view folder
        print("Find replace |APPNAME| with appname in all files in view folder")
        for root, dirs, files in os.walk(f'{appname}/view'):
            for file in files:                
                filepath = os.path.join(root, file)
                print(filepath)

                try:
                    with open(filepath) as f:
                        s = f.read()
                    s = s.replace('|-APPNAME-|', appname)
                    with open(filepath, "w") as f:
                        f.write(s)
                except Exception as e:
                    print(e)
                    continue    

        # mark end time and show elapsed time        
        print(f"Elapsed time: {dt.now() - start}")

    elif action == 'run':

        # excute the command
        os.system('uv run app.py')
        exit(0)

    elif action == 'test':

        print("Testing app...")

    elif action == 'delete':

        # mark start time
        start = dt.now()

        def handle_remove_readonly(func, path, exc):
            excvalue = exc[1]
            if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
                os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
                func(path)
            else:
                raise

        print("Cleaning up app...")

        # delete appname folder
        shutil.rmtree(appname, ignore_errors=False, onexc=handle_remove_readonly)

        # mark end time and show elapsed time
        print(f"Elapsed time: {dt.now() - start}")

    elif action == 'all':
        print("Generating all artifacts...")

        # mark start time
        start = dt.now()

        if not domain:
            print("Domain is required")
            exit(1)

        generate_all(domain)

        # mark end time and show elapsed time
        print(f"Elapsed time: {dt.now() - start}")

    elif action == 'views':
        print("Generating views...")

        # mark start time
        start = dt.now()

        if not domain:
            print("Domain is required")
            exit(1)

        generate_views(domain)

        # mark end time and show elapsed time
        print(f"Elapsed time: {dt.now() - start}")

    elif action == 'controller':

        print("Generating controller...")

        # mark start time
        start = dt.now()

        if not domain:
            print("Domain is required")
            exit(1)

        generate_controller(domain)

        # mark end time and show elapsed time
        print(f"Elapsed time: {dt.now() - start}")

    elif action == 'domain':
        
        print("Generating domain...")

        # mark start time
        start = dt.now()

        if not domain:
            print("Domain is required")
            exit(1)

        generate_domain(domain)

        # mark end time and show elapsed time
        print(f"Elapsed time: {dt.now() - start}")

    elif action == 'incorporate':

        print("Incorporating domain...")

        # mark start time
        start = dt.now()

        if not domain:
            print("Domain is required")
            exit(1)

        incorporate(domain)

        # mark end time and show elapsed time
        print(f"Elapsed time: {dt.now() - start}")

    else:
        print("Invalid action")
        
        # show help message
        parser.print_help()

if __name__ == "__main__":    
    '''
    Kenkun - Main entry point for the script
    '''
    main()