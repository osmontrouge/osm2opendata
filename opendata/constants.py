import os

USER_AGENT = os.environ.get('USER_AGENT', 'OSMontrouge/opendata')
OSMTOGEOJSON_BIN = os.environ.get(
    'OSMTOGEOJSON_BIN',
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../node_modules/.bin/osmtogeojson'
    )
)
OVERPASS_ENDPOINT = os.environ.get('OVERPASS_ENDPOINT', 'https://overpass-api.de/api/interpreter')
