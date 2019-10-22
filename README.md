OSM2OpenData
============

When your city hall does not provide opendata, just do it yourself!


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
python -m osm2opendata -v --searchArea Montrouge <MAPPING_FILE>
```

to generate the GeoJSON OpenData file for the specified mapping (output is on
`stdout`). The `--searchArea` parameter is passed to Nominatim to geocode the
area.


To generate all GeoJSON OpenData files, run

```
mkdir -p out
for i in mappings/*.yml; do python -m osm2opendata -v --searchArea Montrouge ${i} > out/${$(basename $i)%.yml}.geojson; sleep 5; done
```

Run

```
python -m osm2opendata -h
```

for documentation.

## Usage with Docker

```
docker run --rm osmontrouge/osm2opendata python -m osm2opendata -v --searchArea Montrouge <MAPPING_FILE>
```


### Environment variables

You can use (see the `osm2opendata/constants.py` file):

* `OSMTOGEOJSON_BIN` environment variable to change the location of the
    `osmtogeojson` binary (default to `node_modules/.bin/osmtogeojson` in the
    root of the Git repository).
* `USER_AGENT` environment variable to change the user agent used for API
    calls.
- `OVERPASS_ENDPOINT` to specify the overpass endpoint, by default `https://overpass-api.de/api/interpreter`.


## Mapping file syntax

The mapping rules are described in a YAML mapping file. The following items
are required:

* `name`: The name of the dataset.
* `overpass`: The Overpass query to run to fetch the items from OSM.
* `mapping`: The mapping used to define the new fields. This is a dictionary,
    the keys being the new field names and the values being the mapping rules.
    These rules can be:

  * A single string of the form `key` to use the value of the OSM field
      `key`.
  * A check against a value, `key==value` which will return `true` if
      the value of the OSM field `key` is `value` and `false` otherwise.
  * A cast operation, `key|int` or `key|bool` to convert the value of
      the OSM field `key` to `int` or `bool` (converting `yes`, `no`,
      `0` and `1` values to boolean values).
  * A list of such operations, resulting in a coalesce operation (first
      rule returning something else than `None` defines the value).


## License

This software is licensed under an MIT license, unless explicitly mentionned otherwise.
