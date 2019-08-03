import functools
import logging

import requests

from . import constants

logger = logging.getLogger(__name__)


@functools.lru_cache()
def geocode_place(place):
    """
    Geocode a place with Nominatim.

    :param place: Place name.
    :returns: A tuple of the type of OSM feature and the associated ID.
    """
    logger.info('Geocoding %s through Nominatim.', place)
    r = requests.get(
        'https://nominatim.openstreetmap.org/search',
        headers={
            'User-Agent': constants.USER_AGENT
        },
        params={
            'format': 'json',
            'q': place,
        }
    )
    nominatim_place = r.json()[0]
    return nominatim_place['osm_type'], nominatim_place['osm_id']
