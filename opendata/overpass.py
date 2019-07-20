import requests

from . import constants


def query(query_str):
    """
    Query Overpass API.

    :param query_str: The query to run on Overpass API.
    :returns: The parsed JSON response.
    """
    r = requests.post(
        'https://overpass-api.de/api/interpreter',
        headers={
            'User-Agent': constants.USER_AGENT
        },
        data=query_str
    )
    return r.json()
