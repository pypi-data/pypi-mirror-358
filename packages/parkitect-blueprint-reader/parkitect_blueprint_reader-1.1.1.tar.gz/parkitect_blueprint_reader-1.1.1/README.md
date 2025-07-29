# Parkitect Blueprint Reader

Python API and CLI tool to read [Parkitect](https://www.themeparkitect.com/)'s blueprints metadata.

![Python versions](https://img.shields.io/pypi/pyversions/parkitect-blueprint-reader.svg) ![Version](https://img.shields.io/pypi/v/parkitect-blueprint-reader.svg) ![License](https://img.shields.io/pypi/l/parkitect-blueprint-reader.svg)

[PyPI](https://pypi.org/project/parkitect-blueprint-reader/) - [Documentation](https://github.com/EpocDotFr/parkitect-blueprint-reader?tab=readme-ov-file#usage) - [Source code](https://github.com/EpocDotFr/parkitect-blueprint-reader) - [Issue tracker](https://github.com/EpocDotFr/parkitect-blueprint-reader/issues) - [Changelog](https://github.com/EpocDotFr/parkitect-blueprint-reader/releases)

## Prerequisites

  - Python >= 3.10

## Installation

### From PyPi

```shell
pip install parkitect-blueprint-reader
```

### Locally

After cloning/downloading the repo:

```shell
pip install .
```

## Usage

### API

The API consists of one `load()` method, which reads blueprint metadata from the given binary file-like object and returns
the parsed data as a dictionary.

```python
import parkitect_blueprint_reader
from pprint import pprint

try:
    with open('coaster.png', 'rb') as fp: # Note it's opened in binary mode
        pprint(
            parkitect_blueprint_reader.load(fp)
        )
except Exception as e:
    print(e)
```

### CLI

The CLI reads metadata from the given blueprint filename, then writes the parsed data as a JSON to `stdout`.

```shell
parkitect-blueprint-reader coaster.png
```

The `--pretty` option may be used to pretty-print the outputted JSON.

## Data format

Data is stored in blueprints as follows, using the [least significant bits](https://en.wikipedia.org/wiki/Steganography#Digital_messages)
steganography technique (described in the reference documents below):

  - A three-bytes [magic number](https://en.wikipedia.org/wiki/Magic_number_(programming)): `SM\x01` (Parkitect's main
    developer initials)
  - Size (little-endian unsigned int), in bytes, of the gzippped content to be read
  - A 16-bytes [MD5 checksum](https://en.wikipedia.org/wiki/MD5)
  - The actual gzippped data, which is `Size` bytes long

## References

  - [Parkitect devlog - Update 58](https://www.texelraptor.com/blog/update-58)
  - [Reddit - How are blueprints stored?](https://www.reddit.com/r/ThemeParkitect/comments/qpa35q/how_are_blueprints_stored/)
  - [GitHub - Parkitect Blueprint Investigation](https://github.com/slothsoft/parkitect-blueprint-investigator/)

## Development

### Getting source code and installing the package with dev dependencies

  1. Clone the repository
  2. From the root directory, run: `pip install -e ".[dev]"`

### Releasing the package

From the root directory, run `python setup.py upload`. This will build the package, create a git tag and publish on PyPI.

`__version__` in `parkitect_blueprint_reader/__version__.py` must be updated beforehand. It should adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

An associated GitHub release must be created following the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.