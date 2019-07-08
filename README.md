# Mandatory Inclusionary Housing (MIH)

*******************************

 MIH sets mandatory affordable housing requirements for neighborhood rezonings and private applications that significantly increase residential capacity. This script is used to build and distribute the Mandatory Inclusionary Housing data set, internally.

### Prerequisites

A version of Python with the default ArcPy installation that comes with ArcGIS Desktop is required in order to utilize Metadata functionality that is currently not available in the default ArcPy installation that comes with ArcGIS Pro (Python 3).

##### Bytes\_MIH\_Distribution.py

```
os, arcpy, datetime, sys, zipfile, shutil, xml.etree.ElementTree as ET, ConfigParser, traceback, sys, csv
```

### Instructions for running

##### Bytes\_MIH\_Distribution.py

Modify the configuration file variable lines to reflect the desired publication date **(YYYYMMDD)**, the previous city council meeting date **(M/DD/YYYY)** and the date of the last city council meeting **(M/DD/YYYY)**.  The script will execute the following steps:

1. Create a new directory in the BytesProduction MIH folder. The title of this new directory will be equal to the desired publication date entered in the initialization file.

2. Create necessary sub-directories (shp and meta) within newly created folder.

3. Copy the MIH_WebServices.txt file from previous Bytes export directory to the current. This text file holds the urls required for the GeoJSON and REST Feature Data links on the Bytes website.

4. Parse the MIH mxd document and export the source for the most recent mih layer available within the MXD. Exported to both PROD SDE (with pub date appended to title as well as shapefiles in BytesProduction folder )

5. Updates shapefile metadata to include updated publication date and city council date.

6. Copy the metadata xmls from the previous iteration of the MIH export and replace the old city council and publication dates within these xml files.

7. Zip the exported shapefiles within publication date root directory.

8. Export metadata xmls to requisite zoning directories

9. Generate BlockList csv file in following directory with publication date used as unique ID for output file.
