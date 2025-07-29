from parkitect_blueprint_reader.__version__ import __version__
from parkitect_blueprint_reader.blueprint import load
from argparse import ArgumentParser
from sys import stdout
import json


def cli() -> None:
    arg_parser = ArgumentParser(
        description='CLI tool to read Parkitect\'s blueprints metadata.'
    )

    arg_parser.add_argument(
        'filename',
        help='The blueprint file to read metadata from'
    )

    arg_parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'parkitect-blueprint-reader {__version__}'
    )

    arg_parser.add_argument(
        '-p', '--pretty',
        help='Pretty-print output',
        action='store_true'
    )

    args = arg_parser.parse_args()

    with open(args.filename, 'rb') as fp:
        json.dump(
            load(fp),
            stdout,
            indent=2 if args.pretty else None,
            separators=None if args.pretty else (',', ':')
        )


__all__ = ['load']
