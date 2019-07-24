OSM2OpenData
============

When your city hall does not provide opendata, just do it yourself…


## Installation

At the root of the Git repository,

```
pip install -r requirements.txt
npm install osmtogeojson
```


## Usage

At the root of the Git repository,

```
python -m opendata -v --searchArea Montrouge <MAPPING_FILE>
```

To generate everything,

```
mkdir -p out
for i in mappings/*.yml; do python -m opendata -v --searchArea Montrouge ${i} > out/${$(basename $i)%.yml}.geojson; sleep 5; done
```


## License

This software is licensed under an MIT license, unless explicitly mentionned otherwise.
