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
    :returns: The parsed JSON response.
    """
    api = overpass.API()
    logger.debug('Running Overpass query: %s', query_str)
    xml_data = api.get(query_str, responseformat='xml', verbosity='geom')
    geojson_data = json.loads(
        subprocess.check_output(
            constants.OSMTOGEOJSON_BIN,
            input=xml_data.encode('utf-8')
        )
    )
    return geojson_data
