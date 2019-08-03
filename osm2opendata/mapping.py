import functools
import logging

import pyproj
import yaml

from shapely.geometry import mapping, shape
from shapely.ops import transform

from . import constants
from . import nominatim
from . import overpass


logger = logging.getLogger(__name__)

LOCAL_COORDINATES = pyproj.Proj(init=constants.LOCAL_COORDINATES_SYSTEM)
WGS84_COORDINATES = pyproj.Proj(init='EPSG:4326')
TO_LOCAL = functools.partial(
    pyproj.transform,
    WGS84_COORDINATES, LOCAL_COORDINATES
)
TO_WGS84 = functools.partial(
    pyproj.transform,
    LOCAL_COORDINATES, WGS84_COORDINATES
)


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
    :param searchArea: The area to execute Overpass queries in.
    :returns: The fetched objects.
    """
    logger.info('Querying Overpass for mapping "%s".', parsed['name'])
    if searchArea:
        area = overpass.get_overpass_area_id(searchArea)
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


def _clip_geometry(geometry, searchArea):
    """
    Clip the geometry of the object to the bounds of the search area.

    :param geometry: A GeoJSON geometry.
    :param searchArea: The area to clip geometry to.
    """
    osm_type, osm_id = nominatim.geocode_place(searchArea)
    clipping_geometry = next(
        x
        for x in overpass.query(
            '%s(%d)' % (osm_type, osm_id)
        ).get('features', [])
        # This is a hack to ignore relation members and keep the only one
        # geometry.
        if x['id'].startswith(osm_type)
    )['geometry']

    # Convert to shapely objects in local coordinates system
    clipping_geometry = transform(TO_LOCAL, shape(clipping_geometry))
    geometry = transform(TO_LOCAL, shape(geometry))

    # Clip the geometry
    geometry = geometry.intersection(clipping_geometry)

    # Return the geometry projected back in WGS84
    return mapping(transform(TO_WGS84, geometry))


def apply_mapping(data, parsed, searchArea=None):
    """
    Apply the mapping rules on an API response.

    :param data: The API response.
    :param parsed: A parsed YAML mapping.
    :param searchArea: The area to execute Overpass queries in.
    :return: The new items with the mapping rules applied.
    """
    new_items = []
    logger.debug('Got response: %s.', data)

    for item in data.get('features', []):
        # Initialize a new matching item
        new_item = {
            'properties': {
                'osm_id': item['id']
            }
        }
        if searchArea:
            new_item['geometry'] = _clip_geometry(item['geometry'], searchArea)
        else:
            new_item['geometry'] = item['geometry']

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
