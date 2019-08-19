import functools
import json
import logging
import subprocess

import overpass

from . import constants
from . import nominatim

logger = logging.getLogger(__name__)


def get_overpass_area_id(place):
    """
    Geocode a place with Nominatim and get the matching ID to use in Overpass
    queries.

    :param place: Place name.
    :returns: The ID to use as an Overpass place id.
    """
    osm_type, osm_id = nominatim.geocode_place(place)
    # See https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#By_area_.28area.29
    overpass_area_id = None
    if osm_type == 'relation':
        overpass_area_id = 3600000000 + osm_id
    elif osm_type == 'way':
        overpass_area_id = 2400000000 + osm_id
    logger.info('Overpass area id for %s is %d.', place, overpass_area_id)
    return overpass_area_id


@functools.lru_cache()
def query(query_str):
    """
    Query Overpass API.

    :param query_str: The query to run on Overpass API.
    :returns: The parsed (Geo)JSON response.
    """
    api = overpass.API(endpoint=constants.OVERPASS_ENDPOINT,
                       headers={
                           "Accept-Charset": "utf-8;q=0.7,*;q=0.7",
                           "User-Agent": constants.USER_AGENT
                       },
                       timeout=constants.OVERPASS_TIMEOUT
                      )
    logger.debug('Running Overpass query: %s', query_str)
    # Query Overpass API
    xml_data = api.get(query_str, responseformat='xml', verbosity='geom')
    # Convert XML to GeoJSON using OSMToGeoJSON, which gives support for
    # relations.
    geojson_data = json.loads(
        subprocess.check_output(
            constants.OSMTOGEOJSON_BIN,
            input=xml_data.encode('utf-8')
        )
    )
    return geojson_data
