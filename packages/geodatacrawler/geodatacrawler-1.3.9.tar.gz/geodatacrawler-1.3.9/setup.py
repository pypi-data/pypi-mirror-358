# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['geodatacrawler',
 'geodatacrawler.schemas.iso19139',
 'geodatacrawler.templates',
 'templates']

package_data = \
{'': ['*']}

install_requires = \
['GDAL>=3.6.2,<4.0.0',
 'Jinja2>=3.1.2,<4.0.0',
 'OWSLib==0.31.0',
 'PyYAML>=6.0,<7.0',
 'Unidecode>=1.3.8,<2.0.0',
 'beautifulsoup4>=4.12.3,<5.0.0',
 'bibtexparser>=2.0.0b2,<3.0.0',
 'jinja2-time>=0.2.0,<0.3.0',
 'mappyfile>=1.0.0,<2.0.0',
 'openpyxl>=3.1.2,<4.0.0',
 'pygeometa==0.16.0',
 'pyproj>=3.4.0,<4.0.0',
 'pytest>=7.4.0,<8.0.0',
 'xmltodict>=0.13.0,<0.14.0']

entry_points = \
{'console_scripts': ['crawl-etl = geodatacrawler.etl:etl',
                     'crawl-maps = geodatacrawler.mapfile:mapForDir',
                     'crawl-metadata = geodatacrawler.metadata:indexDir']}

setup_kwargs = {
    'name': 'geodatacrawler',
    'version': '1.3.9',
    'description': 'a crawler script to extract and author metadata of spatial datasets',
    'long_description': '# pyGeoDataCrawler\n\nThe tool crawls a data folder or tree. For each spatial file identified, it will process the file. Extract as many information as possible and store it on a sidecar metadata file. \n\nThe tool can also look for existing metadata using common conventions. For metadata imports the tool wil use [owslib](https://github.com/geopython/owslib), which supports some metadata formats. \n\nSeveral options exist for using the results of the generated index:\n\n- The resulting indexed content can be converted to iso19139 or OGCAPI-records and inserted on an instance of pycsw, geonetwork or pygeoapi, to make it searchable.\n- Automated creation of a mapserver mapfile to provide OGC services on top of the spatial files identified.\n\n## Installation\n\nThe tool requires GDAL 3.2.2 and pysqlite 0.4.6 to be installed. I recommend to use [conda](https://conda.io/) to install them.\n\n```\nconda create --name pgdc python=3.9 \nconda activate pgdc\nconda install -c conda-forge gdal==3.3.2\nconda install -c conda-forge pysqlite3==0.4.6\n```\n\nThen run:\n\n```\npip install geodatacrawler\n```\n\n## Usage \n\nThe tools are typically called from commandline or a bash script.\n\n### Index metadata\n\n```\ncrawl-metadata --mode=init --dir=/myproject/data [--out-dir=/mnt/myoutput]\n```\n\nMode explained:\n\n- `init`; creates new metadata for files which do not have it yet (not overwriting)\n- `update`; updates the metadata, merging new content on existing (not creating new)\n- `export`; exports the mcf metadata to xml and stored it in a folder (to be loaded on pycsw) or on a database (todo)\n- `import-csv`; imports a csv of metadata fiels into a series of mcf files, typically combined with a [.j2 file](geodatacrawler/templates/csv.j2) with same name, which `maps` the csv-fields to mcf-fields \n\nThe export utility will merge any yaml file to a index.yml from a parent folder. This will allow you to create minimal metadata at the detailed level, while providing more generic metadata down the tree. The index.yml is also used as a configuration for any mapfile creation (service metadata).\n\nMost parameters are configured from the commandline, check --help to get explanation.\n2 parameters can be set as an environment variable\n\n- pgdc_host is the url on which the data will be hosted in mapserver or a webdav folder.\n- pgdc_schema_path is a physical path to an override of the default iso19139 schema of pygeometa, containing jinja templates to format the exported xml\n\nSome parameters can be set in index.yml, in a robot section. Note that config is inherited from parent folders.\n\n```yaml\nmcf:\n    version 1.0\nrobot: \n  skip-subfolders: True # do not move into subfolders, typically if subfolder is a set of tiles, default: False \n  skip-files: "temp.*" # do not process files matching a regexp, default: None \n```\n\n### OGR/GDAL formats\n\nSome GDAL (raster) or OGR (vector) formats, such as [FileGDB](https://gdal.org/drivers/vector/openfilegdb.html), [GeoPackage](https://gdal.org/drivers/vector/gpkg.html) and [parquet](https://gdal.org/drivers/vector/parquet.html) require an additional plugin. Verify for each of the commom formats in your organisation, if the relevant GDAL plugins are installed.\n\nFor grid files, the metadata will be extracted from the .aux.xml file. You can use the Dublin Core terms; title, description, license, ... in the grid metadata.\n\n## Create mapfile\n\nThe metadata identified can be used to create OGC services exposing the files. Currently the tool creates [mapserver mapfiles](https://www.mapserver.org/mapfile/), which are placed on a output-folder. A `index.yml` configuraton file is expected at the root of the folder to be indexed, if not, it will be created.\n\n```\ncrawl-mapfile --dir=/mnt/data [--out-dir=/mnt/mapserver/mapfiles]\n```\n\nSome parameters in the mapfile can be set using environment variables:\n\n| Param | Description | Example |\n| --- | --- | --- |\n| **pgdc_out_dir** | a folder where files are placed (can override with --dir-out) | | \n| **pgdc_md_url** | a pattern on how to link to metadata, use {0} to be substituted by record uuid, or empty to not include metadata link | https://example.com/{0} |\n| **pgdc_ms_url** | the base url of mapserver | http://example.com/maps |\n| **pgdc_webdav_url** | the base url on which data files are published or empty if not published | http://example.com/data |\n| **pgdc_md_link_types** | which service links to add | OGC:WMS,OGC:WFS,OGC:WCS,OGCAPI:Features |\n\n```bash\nexport pgdc_webdav_url="https://example.com/data"\n```\n\nA [mapserver docker](https://github.com/camptocamp/docker-mapserver) image is provided by Camp to Camp which is able to expose a number of mapfiles as mapservices, eg http://example.com/{mapfile}?request=getcapabilities&service=wms. Each mapfile needs to be configured as alias in [mapserver config file](https://mapserver.org/mapfile/config.html).\n\n### Layer styling\n\nYou can now set dedicated layer styling for grids and vectors. Note that you can define multiple styles per layer, the last is used as default:\n\n### SLD\n\nStarting from [Mapserver 8.2](https://github.com/MapServer/MapServer/tree/rel-8-2-0) SLD can directly be referenced from mapfiles for layer styling.\nIf the crawler notices a file with the same name as the dataset, but with extension `.sld`, it will reference that file for layer styling. Notice that you can export sld from any QGIS layer. \n\n### Mapfile syntax\n\nAdd mapserver mapfile syntax to the mcf robot section\n\n```yaml\nrobot:\n  map:\n    styles: |\n      CLASS\n        NAME "style"\n        STYLE\n          COLOR 100 100 100\n          SIZE 8\n          WIDTH 1\n        END\n      END\n```\n\n### YAML syntax\n\nFor various layer types, various options exits. \n\n- A range of colors (grid only), the min-max range of the first band is devided by the number of colors.\n\n```yaml\nrobot:\n  map:\n    styles:\n      - name: rainbow\n        classes: "#ff000,#ffff00,#00ff00,#00ffff,#0000ff"\n      - name: grays\n        classes: "#00000,#333333,#666666,#999999,#cccccc,#ffffff"\n```\n\n- A range of distinct values, you can also use rgb colors\n\n```yaml\nrobot:\n  map:\n    styles:\n      - name: rainbow\n        property: length # name of the column, vector only\n        classes: \n          - label: True\n            val: 1\n            color: "0 255 0"\n          - label: False\n            val: 0\n            color: "255 0 0" \n```\n\n- A range of classes\n\n```yaml\nrobot:\n  map:\n    styles:\n      - name: Scale\n        property: length # name of the column, vector only\n        classes: \n          - label: Low\n            min: 0\n            max: 100\n            color: "#0000ff"\n          - label: Medium\n            min: 100\n            max: 200\n            color: "#00ff00"\n          - label: High\n            min: 200\n            max: 300\n            color: "#ff0000" \n```\n\n## Development\n\n### Python Poetry\n\nThe project is based on common coding conventions from the python poetry community.\n\nOn the sources, either run scripts directly:\n\n```\npoetry run crawl-mapfile --dir=/mnt/data\n```\n\nor run a shell in the poetry environment:\n\n```\npoetry shell \n```\n\nThe GDAL dependency has some installation issue on poetry, see [here](https://stackoverflow.com/a/70986804) for a workaround\n\n```\n> poetry shell\n>> sudo apt-get install gdal\n>> gdalinfo --version\nGDAL 3.3.2, released 2021/09/01\n>> pip install gdal==3.3.2\n>> exit\n```\n\n### Release\n\n- poetry run pytest tests\n- update [__init__.py](__init__.py) and [pyproject.toml](pyproject.toml)\n- push changes\n- trigger semantic release\n- poetry build\n- poetry publish\n\n## Docker hub\n\n```\ndocker build -t pvgenuchten/geodatacrawler:1.3.8 .\ndocker login\ndocker push pvgenuchten/geodatacrawler:1.3.8\ndocker tag pvgenuchten/geodatacrawler:1.3.8 pvgenuchten/geodatacrawler:latest\ndocker push pvgenuchten/geodatacrawler:latest\n```',
    'author': 'Paul van Genuchten',
    'author_email': 'genuchten@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pvgenuchten/pyGeoDataCrawler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
