from setuptools import setup, find_packages
import sys

# Read the contents of your requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Standard setup for a Python package
setup_args = {
    'name': 'MopMan_PacketMaker',
    'version': '0.1.0',
    'packages': find_packages(),
    'install_requires': requirements,
    # Add other standard setup parameters as needed
}

# Conditional setup for py2app
if 'py2app' in sys.argv:
    setup_args.update({
        'app': ['your_script.py'],
        'data_files': [],
        'options': {
            'py2app': {
                'argv_emulation': True,
                'packages': ['required', 'packages'],
            }
        },
        'setup_requires': ['py2app'],
    })

setup(**setup_args)
