import os

USER_AGENT = os.environ.get('USER_AGENT', 'OSMontrouge/OSM2OpenData')
OSMTOGEOJSON_BIN = os.environ.get(
    'OSMTOGEOJSON_BIN',
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../node_modules/.bin/osmtogeojson'
    )
)
OVERPASS_ENDPOINT = os.environ.get(
    'OVERPASS_ENDPOINT',
    'https://overpass-api.de/api/interpreter'
)
OVERPASS_TIMEOUT = os.environ.get(
    'OVERPASS_TIMEOUT',
    300
)
LOCAL_COORDINATES_SYSTEM = os.environ.get(
    'LOCAL_COORDINATES_SYSTEM',
    'EPSG:2154'  # Lambert93, France
)
