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


def _process_field(item, field_mapping):
    """
    Process the mapping rules for a given field.

    :param item: The item from the Overpass response.
    :param field_mapping: The field mapping to apply (not pre-processed).
    :return: The new value of the field.
    """
    # Handle the special address filter
    properties = item.get('properties', {})
    if field_mapping == '<ADDRESS>':
        housenumber = properties.get('contact:housenumber')
        if housenumber:
            return '%s, %s' % (
                housenumber,
                properties.get(
                    'contact:street',
                    properties.get('contact:place')
                )
            )
        else:
            return '%s' % properties.get(
                'contact:street',
                properties.get('contact:place')
            )

    # Parse the mapping for cast and checks
    cast, check = None, None
    if '|' in field_mapping:
        field_mapping, cast = field_mapping.split('|')[:2]
    if '==' in field_mapping:
        field_mapping, check = field_mapping.split('==')[:2]

    # Get the current value of the field
    new_value = properties.get(field_mapping)

    # Eventually apply check
    if check:
        return new_value == check

    # Eventually apply cast operation
    if cast == 'int':
        return int(new_value) if new_value else None
    if cast == 'bool':
        if new_value in ['yes', '1']:
            return True
        elif new_value in ['no', '0']:
            return False
        return None
    return new_value


def apply_mapping(data, parsed):
    """
    Apply the mapping rules on an API response.

    :param data: The API response.
    :param parsed: A parsed YAML mapping.
    :return: The new items with the mapping rules applied.
    """
    new_items = []
    logger.debug('Got response: %s.', data)

    for item in data.get('features', []):
        # Initialize a new matching item
        new_item = {
            'geometry': item['geometry'],
            'properties': {
                'osm_id': item['id']
            }
        }
        # Apply mapping rules
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
