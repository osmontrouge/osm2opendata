import logging

import overpass

logger = logging.getLogger(__name__)


def query(queries_str):
    """
    Query Overpass API.

    :param query_str: The query to run on Overpass API.
    :returns: The parsed JSON response.
    """
    api = overpass.API()
    data = {
        'type': 'FeatureCollection',
        'features': []
    }
    for query in queries_str:
        logger.debug('Running Overpass query: %s', query)
        data['features'].extend(
            api.get(query, responseformat='geojson', verbosity='geom').features
        )
    return data
