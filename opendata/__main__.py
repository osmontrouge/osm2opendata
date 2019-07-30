import argparse
import json
import logging

from . import mapping

logging.basicConfig()


def main(mappings, searchArea):
    for filename in mappings:
        parsed = mapping.read_mapping(filename)
        data = mapping.execute_overpass(parsed, searchArea)
        data = mapping.apply_mapping(data, parsed)
        print(json.dumps(
            {
                'type': 'FeatureCollection',
                'features': sorted(
                    data,
                    key=lambda x: x['properties']['osm_id']
                )
            },
            sort_keys=True, indent=4, separators=(',', ': ')
        ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate OpenData from OSM.'
    )
    parser.add_argument(
        'mappings', nargs='+', help='Mappings files to load.'
    )
    parser.add_argument(
        '--searchArea', help='Search area to geocode.'
    )
    parser.add_argument(
        '-v', '--verbose', help='Verbose logging', action='store_true'
    )
    parser.add_argument(
        '-vvv', '--debug', help='Debug logging', action='store_true'
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    main(args.mappings, args.searchArea)
