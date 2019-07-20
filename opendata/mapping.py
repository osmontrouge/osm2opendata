import logging
import re

import yaml

from . import nominatim
from . import overpass


logger = logging.getLogger(__name__)
GEOCODE_AREA_RE = re.compile(r'{{geocodeArea:(\w+?)}}')


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


def execute_overpass(parsed):
    """
    Execute the Overpass query for a given parsed mapping.

    :param parsed: A parsed YAML mapping.
    :returns: The fetched objects.
    """
    logger.info('Querying Overpass for mapping "%s".', parsed['name'])
    geocoded_overpass_query  = GEOCODE_AREA_RE.sub(
        lambda match: 'area(%d)' % nominatim.geocode_place(match.group(1)),
        parsed['overpass']
    )
    return overpass.query(geocoded_overpass_query)
