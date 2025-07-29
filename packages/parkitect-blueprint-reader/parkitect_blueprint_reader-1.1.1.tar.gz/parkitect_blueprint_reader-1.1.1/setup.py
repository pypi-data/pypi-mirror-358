# Original setup.py template: https://github.com/kennethreitz/setup.py

from setuptools import find_packages, setup, Command
from importlib import util as importlib_util
from subprocess import call
from shutil import rmtree
from os import path
import sys

NAME = 'parkitect-blueprint-reader'
DESCRIPTION = 'Python API and CLI tool to read Parkitect\'s blueprints metadata.'
URL = 'https://github.com/EpocDotFr/parkitect-blueprint-reader'
EMAIL = 'contact.nospam@epoc.nospam.fr'
AUTHOR = 'Maxime "Epoc" Gross'
REQUIRES_PYTHON = '>=3.10'
VERSION = None  # Pulled from parkitect_blueprint_reader/__version__.py

REQUIRED = [
    'pillow~=11.1',
    'bitstring~=4.3',
]

EXTRAS = {
    'dev': {
        'build~=1.2',
        'twine~=6.0',
        'setuptools>=69',
    },
}

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Operating System :: OS Independent',
    'Environment :: Console',
    'Topic :: Games/Entertainment',
    'Topic :: File Formats',
    'Topic :: Multimedia :: Graphics',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Intended Audience :: Developers',
]

PROJECT_URLS = {
    'Documentation': 'https://github.com/EpocDotFr/parkitect-blueprint-reader?tab=readme-ov-file#usage',
    'Source code': 'https://github.com/EpocDotFr/parkitect-blueprint-reader',
    'Issue tracker': 'https://github.com/EpocDotFr/parkitect-blueprint-reader/issues',
    'Changelog': 'https://github.com/EpocDotFr/parkitect-blueprint-reader/releases',
}

KEYWORDS = ['parkitect', 'blueprint', 'reader', 'steganography']

here = path.abspath(path.dirname(__file__))

try:
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}

if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")

    spec = importlib_util.spec_from_file_location('__version__', path.join(here, project_slug, '__version__.py'))
    module = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)

    about['__version__'] = module.__version__
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')

            rmtree(path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel distribution…')

        call('"{0}" -m build --sdist --wheel'.format(sys.executable), shell=True)

        self.status('Uploading the package to PyPI via Twine…')

        call('twine upload dist/*', shell=True)

        self.status('Pushing git tags…')

        call('git tag v{0}'.format(about['__version__']), shell=True)
        call('git push --tags', shell=True)

        exit()


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='DBAD',
    entry_points={
        'console_scripts': [
            'parkitect-blueprint-reader = parkitect_blueprint_reader:cli',
        ]
    },
    classifiers=CLASSIFIERS,
    cmdclass={
        'upload': UploadCommand,
    },
    project_urls=PROJECT_URLS,
    keywords=KEYWORDS
)
