import json
import logging
import subprocess

import overpass

from . import constants

logger = logging.getLogger(__name__)


def query(query_str):
    """
    Query Overpass API.

    :param query_str: The query to run on Overpass API.
    :returns: The parsed (Geo)JSON response.
    """
    api = overpass.API(headers={
        "Accept-Charset": "utf-8;q=0.7,*;q=0.7",
        "User-Agent": constants.USER_AGENT
    })
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
