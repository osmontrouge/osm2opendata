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


def _process_field(item, osm_field):
    """
    TODO
    """
    if osm_field == '<ADDRESS>':
        return '%s, %s' % (
            item.get('properties', {}).get('contact:housenumber'),
            item.get('properties', {}).get('contact:street')
        )
    cast = None
    check = None
    if '|' in osm_field:
        osm_field, cast = osm_field.split('|')[:2]
    if '==' in osm_field:
        osm_field, check = osm_field.split('==')[:2]

    new_value = item.get('properties', {}).get(osm_field)

    if check:
        return new_value == check

    if cast == 'int':
        return int(new_value) if new_value else None

    if cast == 'bool':
        if new_value in ['yes', '1']:
            return True
        elif new_value in ['no', '0', None]:
            return False
        return None
    return new_value


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
            if type(osm_field) == list:
                for osm_field_item in osm_field:
                    new_value = _process_field(
                        item, osm_field_item
                    )
                    if new_value is not None:
                        new_item['properties'][new_field] = new_value
                        break
            else:
                new_item['properties'][new_field] = _process_field(
                    item, osm_field
                )

        new_items.append(new_item)
    return new_items
