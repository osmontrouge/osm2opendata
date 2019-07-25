import logging
import re

import yaml

from . import nominatim
from . import overpass


logger = logging.getLogger(__name__)


def read_mapping(filename):
    """
    Parse a YAML mapping file.

    :param filename: The YAML mapping to load.
    :return: Parsed mapping.
    """
    logger.info('Loading mapping description from %s.', filename)
    with open(filename, 'r') as fh:
        mapping = yaml.load(fh, Loader=yaml.Loader)
    return mapping


def execute_overpass(parsed, searchArea=None):
    """
    Execute the Overpass query for a given parsed mapping.

    :param parsed: A parsed YAML mapping.
    :returns: The fetched objects.
    """
    logger.info('Querying Overpass for mapping "%s".', parsed['name'])
    if searchArea:
        area = nominatim.geocode_place(searchArea)
        geocoded_overpass_query = parsed['overpass'].replace(
            'area.searchArea', 'area:%d' % area
        )
    else:
        geocoded_overpass_query = parsed['overpass']
    return overpass.query(geocoded_overpass_query)


def apply_mapping(data, parsed):
    """
    TODO
    """
    new_items = []
    logger.debug('Got response: %s.', data)

    for item in data.get('features', []):
        new_item = {
            'geometry': item['geometry'],
            'properties': {
                'osm_id': item['id']
            }
        }
        for new_field, osm_field in parsed.get('mapping', {}).items():
            if osm_field == '<ADDRESS>':
                new_item['properties'][new_field] = '%s, %s' % (
                    item.get('properties', {}).get('contact:housenumber'),
                    item.get('properties', {}).get('contact:street')
                )
            else:
                cast = None
                if '|' in osm_field:
                    osm_field, cast = osm_field.split('|')[:2]
                new_value = item.get('properties', {}).get(osm_field)

                if cast == 'int':
                    new_item['properties'][new_field] = (
                        int(new_value) if new_value else None
                    )
                elif cast == 'bool':
                    if new_value in ['yes', '1']:
                        new_item['properties'][new_field] = True
                    elif new_value in ['no', '0', None]:
                        new_item['properties'][new_field] = False
                    else:
                        new_item['properties'][new_field] = None
                else:
                    new_item['properties'][new_field] = new_value

        new_items.append(new_item)
    return new_items
