import argparse
import logging

from . import mapping

logging.basicConfig()


def main(mappings):
    for filename in mappings:
        parsed = mapping.read_mapping(filename)
        print(mapping.execute_overpass(parsed))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate OpenData from OSM.'
    )
    parser.add_argument(
        'mappings', nargs='+', help='Mappings files to load.'
    )
    parser.add_argument(
        '-v', '--verbose', help='Verbose logging', action='store_true'
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    main(args.mappings)
