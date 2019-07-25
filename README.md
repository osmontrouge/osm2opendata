OSM2OpenData
============

When your city hall does not provide opendata, just do it yourself…


## Requirements

At the root of the Git repository,

```
pip install -r requirements.txt
npm install osmtogeojson
```

You should run `pip` in a
[virtualenv](https://docs.python-guide.org/dev/virtualenvs/).


## Usage

At the root of the Git repository, run

```
python -m opendata -v --searchArea Montrouge <MAPPING_FILE>
```

to generate the GeoJSON OpenData file for the specified mapping (output is on
`stdout`). The `--searchArea` parameter is passed to Nominatim to geocode the
area.


To generate all GeoJSON OpenData files, run

```
mkdir -p out
for i in mappings/*.yml; do python -m opendata -v --searchArea Montrouge ${i} > out/${$(basename $i)%.yml}.geojson; sleep 5; done
```

Run

```
python -m opendata -h
```

for documentation.


### Environment variables

You can use (see the `opendata/constants.py` file):

* `OSMTOGEOJSON_BIN` environment variable to change the location of the
    `osmtogeojson` binary (default to `node_modules/.bin/osmtogeojson` in the
    root of the Git repository).
* `USER_AGENT` environment variable to change the user agent used for API
    calls.


## License

This software is licensed under an MIT license, unless explicitly mentionned otherwise.
