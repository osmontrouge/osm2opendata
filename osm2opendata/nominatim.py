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
    :returns: The ID to use as an Overpass place id.
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
    # See https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#By_area_.28area.29
    overpass_area_id = None
    if nominatim_place['osm_type'] == 'relation':
        overpass_area_id = 3600000000 + nominatim_place['osm_id']
    elif nominatim_place['osm_type'] == 'way':
        overpass_area_id = 2400000000 + nominatim_place['osm_id']
    logger.info('Overpass area id for %s is %d.', place, overpass_area_id)
    return overpass_area_id
