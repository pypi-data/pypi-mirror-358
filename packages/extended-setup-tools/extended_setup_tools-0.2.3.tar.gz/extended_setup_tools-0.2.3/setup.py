import sys
from pathlib import Path

current_dir = str(Path(__file__).parent)
if (current_dir not in sys.path):
    sys.path.insert(0, current_dir)

from extended_setup import *

SingleScriptModuleSetup('extended_setup').setup \
(
    short_description = "Python tool for helping making shorter and smarter setup.py scripts",
    category = 'tools',
    min_python_version = '3.6',
    classifiers =
    [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        "Topic :: Software Development :: Build Tools",
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
