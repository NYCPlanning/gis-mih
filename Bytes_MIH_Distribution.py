import os, arcpy, datetime, sys, zipfile, shutil, xml.etree.ElementTree as ET, ConfigParser, traceback, sys, csv

# Define function for removing geoprocessing and local storage information.

try:
    def remove_geoprocess_lcl_storage(src, date):
        arcdir = arcpy.GetInstallInfo("desktop")["InstallDir"]
        xslt_remove_geoprocessing = arcdir + "Metadata/Stylesheets/gpTools/remove geoprocessing history.xslt"
        xslt_remove_local_storage = arcdir + "Metadata/Stylesheets/gpTools/remove local storage info.xslt"
        arcpy.XSLTransform_conversion(src, xslt_remove_geoprocessing, r"C:\temp\{}.xml".format(src.split("\\")[-1]))
        tree = ET.parse(r"C:\temp\{}.xml".format(src.split("\\")[-1]))
        root = tree.getroot()
        for pubdate in root.iter('pubDate'):
            print("Previous publication date - {}".format(pubdate.text))
            print("Setting publication date to - {}".format(date))
            pubdate.text = date
        for pubdate in root.iter('pubdate'):
            print("Previous publication date - {}".format(pubdate.text))
            print("Setting publication date to - {}".format(date))
            pubdate.text = date
        for summary_date in root.iter('idPurp'):
            if 'Last Update:' in summary_date.text:
                summary_date.text = summary_date.text.replace(prev_city_council_date, city_council_date)
            else:
                summary_date.text = summary_date.text.replace(prev_city_council_date, city_council_date)
        for title in root.iter('title'):
            print("Updating FGDC metadata title to - {}".format(date))
            title.text = "MIH_{}".format(date)
        for metd in root.iter('metd'):
            print("Updating FGDC metadata date to - {}".format(date))
            metd.text = date
        tree.write(r"C:\temp\{}.xml".format(src.split("\\")[-1]))
        arcpy.MetadataImporter_conversion(r"C:\temp\{}.xml".format(src.split("\\")[-1]), src)
        arcpy.XSLTransform_conversion(src, xslt_remove_local_storage, r"C:\temp\{}.xml".format(src.split("\\")[-1]))
        arcpy.MetadataImporter_conversion(r"C:\temp\{}.xml".format(src.split("\\")[-1]), src)

    # Define function for updating publication date within XML.

    def update_xml_meta(src, date):
        old_export_dir = r"M:\GIS\BytesProduction\MIH\2019\20190329"
        print("Copying old metadata xml to new directory and updating publication date")
        old_metadata_dir = os.path.join(old_export_dir, 'meta')
        print("Copying {}".format(src))
        shutil.copyfile(os.path.join(old_metadata_dir, src), os.path.join(export_directory_meta, src))
        print("Copy complete")
        print("Editing xml publication date")
        tree = ET.parse(os.path.join(export_directory_meta, src))
        root = tree.getroot()
        for pubdate in root.iter('pubDate'):
            print("Previous publication date - {}".format(pubdate.text))
            print("Setting publication date to - {}".format(date))
            pubdate.text = date
        for summary_date in root.iter('idPurp'):
            if '2/28/19' in summary_date.text:
                print("Previous summary - {}".format(summary_date.text))
                summary_preview = summary_date.text.replace('2/13/2019', city_council_date)
                summary_preview = summary_preview.replace('2/28/19', str(datetime.datetime.strftime(publication_datetime, '%#m/%#d/%Y')))
                summary_date.text = summary_preview
                print("Setting summary to - {}".format(summary_date.text))
            else:
                print("Previous summary - {}".format(summary_date.text))
                summary_preview = summary_date.text.replace('2/13/2019', city_council_date)
                summary_date.text = summary_preview
                print("Setting summary to - {}".format(summary_date.text))
        tree.write(os.path.join(export_directory_meta, "{}_new.xml".format(src.split('.')[0])))
        os.remove(os.path.join(export_directory_meta, src))
        os.rename(os.path.join(export_directory_meta, "{}_new.xml".format(src.split('.')[0])),
                  os.path.join(export_directory_meta, src))

    # Setting config path

    config = ConfigParser.ConfigParser()
    config.read(r'G:\SCRIPTS\MIH_Distribution\ini\MIH_config.ini')

    # Setting log path

    log_path = config.get('PATHS', 'log_path')
    log = open(log_path, "a")

    # Set start time

    StartTime = datetime.datetime.now().replace(microsecond=0)

    # Setting metadata translator path

    dir = arcpy.GetInstallInfo("desktop")["InstallDir"]
    translator = dir + "Metadata/Translator/ARCGIS2FGDC.xml"

    # Setting path variables for mxd location directory and MIH Bytes output directory

    city_council_date = config.get('VARS', 'city_council_date')
    prev_city_council_date = config.get('VARS', 'prev_city_council_date')
    publication_date = config.get('VARS', 'publication_date')
    publication_datetime = datetime.datetime.strptime(publication_date, '%Y%m%d')
    mxd_path = arcpy.mapping.MapDocument(config.get('PATHS', 'mxd_path'))
    mih_output_path = config.get('PATHS', 'mih_output_path')
    sde_path = config.get('PATHS', 'sde_path')
    zoning_path = config.get('PATHS', 'zoning_path')
    bytes_zoning_path = config.get('PATHS', 'bytes_zoning_path')

    # Compiling list of export directory years

    mih_years = []

    mih_dates = []

    print("Compiling list of export directory years")
    for directory in os.listdir(mih_output_path):
        if len(str(directory)) == 4 and directory[0].isdigit():
            directory = datetime.datetime.strptime(directory, '%Y')
            mih_years.append(directory.date().year)

    # Setting current year directory value

    current_year = max(mih_years)
    print("Most recent export year directory is {}".format(current_year))

    # Checking for latest MIH layer in MXD document

    for lyr in arcpy.mapping.ListLayers(mxd_path):
        try:
            if lyr.supports("DATASOURCE") and 'nycmih' in lyr.name:
                print("Available layer srcs within MIH MXD doc - {}".format(lyr.dataSource))
                mih_date = datetime.datetime.strptime(lyr.name.split('_')[1], '%Y%m%d').date()
                print("Dates associated with available layer srcs - {}".format(mih_date))
                mih_dates.append(mih_date)
                latest_mih_date = max(mih_dates)
                latest_mih_name = 'nycmih_{}'.format(str(latest_mih_date.strftime('%Y%m%d')))
                print("Most recent MIH layer - {}".format(latest_mih_name))
        except Exception as e:
            raise(e)

    # Beginning export of requisite files from MXD to Bytes directories

    for lyr in arcpy.mapping.ListLayers(mxd_path):
        try:
            if latest_mih_name in lyr.name:
                # Checking for existence of requisite export sub-directories
                export_directory = os.path.join(mih_output_path, str(current_year), publication_date)
                print("Setting export directory path - {}".format(export_directory))
                export_directory_shp = os.path.join(export_directory, 'shp')
                print("Setting shapefile export directory path - {}".format(export_directory_shp))
                export_directory_meta = os.path.join(export_directory, 'meta')
                print("Setting metadata export directory path - {}".format(export_directory_meta))
                if os.path.exists(export_directory):
                    print("A sub-directory with this date already exists. Deleting now.")
                    shutil.rmtree(export_directory)
                    print("Creating export directory - {}".format(export_directory))
                    os.mkdir(export_directory)
                    print("Creating shapefile export directory - {}".format(export_directory))
                    os.mkdir(export_directory_shp)
                    print("Creating export directory - {}".format(export_directory))
                    os.mkdir(export_directory_meta)
                else:
                    print("Creating export directory - {}".format(export_directory))
                    os.mkdir(export_directory)
                    print("Creating shapefile export directory - {}".format(export_directory))
                    os.mkdir(export_directory_shp)
                    print("Creating export directory - {}".format(export_directory))
                    os.mkdir(export_directory_meta)

                # Retrieving latest MIH layer source in preparation for export to Bytes directory
                print("Setting path for layer source in prep for export")
                latest_mih_src = lyr.dataSource
                print("MXD layer source - {}".format(latest_mih_src))
                # Exporting latest MIH shapefile to Bytes shapefile sub-directory
                print("Exporting MIH layer src to {}".format(export_directory_shp))
                arcpy.FeatureClassToShapefile_conversion(latest_mih_src, export_directory_shp)
                remove_geoprocess_lcl_storage(os.path.join(export_directory_shp, "{}.shp".format(latest_mih_src.split('\\')[-1])), publication_date)
            elif latest_mih_name is None:
                # Handling case where no matching layer sources were found in the MXD Document
                print("No MIH layer found within the MXD document. Please double-check the MIH MXD document")
        except Exception as e:
            raise(e)

    # Beginning export of MIH shapefile to SDE PROD
    print("Exporting MIH from layer source location to SDE PROD with today's date appended")
    print("Make sure you archive/delete the old MIH version on PROD and replace when ready")
    arcpy.FeatureClassToFeatureClass_conversion(latest_mih_src, sde_path, 'DCP_MIH_{}'.format(publication_date))
    remove_geoprocess_lcl_storage(os.path.join(sde_path, 'DCP_MIH_{}'.format(publication_date)), publication_date)

    # Zipping shapefile in parent MIH directory
    print("Starting zip process")
    zip = zipfile.ZipFile(os.path.join(export_directory, 'nycmih_{}.zip'.format(publication_date)),
                          'w',
                          compression=zipfile.ZIP_DEFLATED)
    print("Zipping shapefile components. Zip file located in {}".format(export_directory))

    for file in os.listdir(export_directory_shp):
        os.chdir(export_directory_shp)
        zip.write(file)
    zip.close()
    print("Zip file successfully generated")

    # Copying MIH WebServices.txt file to Bytes root directory
    old_export_dir = config.get('PATHS', 'old_export_dir')

    print("Copying MIH WebServices.txt")
    shutil.copyfile(os.path.join(old_export_dir, 'MIH_WebServices.txt'),
                    os.path.join(export_directory, 'MIH_WebServices.txt'))
    print("MIH WebService.txt copy successful")

    # Exporting updated metadata files to Bytes meta directory

    update_xml_meta('MIHmetaBytes.xml', publication_date)
    update_xml_meta('MIHmetaGuide.xml', publication_date)

    print("xml publication date modified")

    # Exporting metadata xmls to M:\GIS\DATA\Zoning

    shutil.copy(os.path.join(export_directory_meta, 'MIHmetaBytes.xml'), zoning_path)
    os.remove(os.path.join(zoning_path, 'Mandatory Inclusionary Housing (MIH).lyr.xml'))
    os.rename(os.path.join(zoning_path, 'MIHmetaBytes.xml'),
              os.path.join(zoning_path, 'Mandatory Inclusionary Housing (MIH).lyr.xml'))

    # Exporting metadata xmls to M:\GIS\DATA\BYTES of the BIG APPLE\Zoning Related

    arcpy.ExportMetadata_conversion(os.path.join(sde_path, 'DCP_MIH_{}'.format(publication_date)),
                                    translator,
                                    os.path.join(zoning_path, 'Mandatory Inclusionary Housing (MIH).lyr.xml'))
    arcpy.ExportMetadata_conversion(os.path.join(sde_path, 'DCP_MIH_{}'.format(publication_date)),
                                    translator,
                                    os.path.join(bytes_zoning_path, 'Mandatory Inclusionary Housing (MIH).lyr.xml'))

    # Exporting MIHBlocklist csv file

    # Setting path variables for mxd location directory and MIH Bytes output directory

    dtm_path = config.get('PATHS', 'dtm_path')
    blocklist_dir_path = config.get('PATHS', 'blocklist_dir_path')
    blocklist_path = os.path.join(blocklist_dir_path, "BlockList_Test.gdb")
    output_blocklist_path = config.get('PATHS', 'output_blocklist_path')

    # Check for any previous versions of the Blocklist temporary files

    if arcpy.Exists(blocklist_dir_path):
        print("Previous temporary files identified. Deleting now")
        arcpy.Delete_management(blocklist_dir_path)
        print("Creating temporary blocklist directory")
        os.mkdir(blocklist_dir_path)
    else:
        print("Blocklist directory does not currently exist. Creating now")
        os.mkdir(blocklist_dir_path)

    if arcpy.Exists(blocklist_path):
        print("Previous temporary files identified. Deleting now")
        arcpy.Delete_management(blocklist_path)
        print("Temporary files deleted")
        print("Creating new file geodatabase for temporary files")
        arcpy.CreateFileGDB_management(blocklist_dir_path, 'BlockList_Test.gdb')
    else:
        print("Creating new file geodatabase for temporary files")
        arcpy.CreateFileGDB_management(blocklist_dir_path, 'BlockList_Test.gdb')

    # Compiling list of export directory years

    mih_years = []

    mih_dates = []

    print("Compiling list of export directory years")
    for directory in os.listdir(mih_output_path):
        if len(str(directory)) == 4 and directory[0].isdigit():
            directory = datetime.datetime.strptime(directory, '%Y')
            mih_years.append(directory.date().year)

    # Setting current year directory value

    current_year = max(mih_years)
    print("Most recent export year directory is {}".format(current_year))

    # Checking for latest MIH layer in MXD document

    for lyr in arcpy.mapping.ListLayers(mxd_path):
        try:
            if lyr.supports("DATASOURCE") and 'nycmih' in lyr.name:
                print("Available layer srcs within MIH MXD doc - {}".format(lyr.dataSource))
                mih_date = datetime.datetime.strptime(lyr.name.split('_')[1], '%Y%m%d').date()
                print("Dates associated with available layer srcs - {}".format(mih_date))
                mih_dates.append(mih_date)
                latest_mih_date = max(mih_dates)
                latest_mih_name = 'nycmih_{}'.format(str(latest_mih_date.strftime('%Y%m%d')))
                if latest_mih_name in lyr.name:
                    latest_layer_source = lyr.dataSource
                    print("Most recent MIH layer - {}".format(latest_mih_name))
                    print("Most recent MIH layer source - {}".format(latest_layer_source))
                    if arcpy.Exists(blocklist_path):
                        print("Exporting MIH layer data-source to temporary FGDB")
                        arcpy.FeatureClassToFeatureClass_conversion(lyr.dataSource, blocklist_path, "latest_mih_export")
                        print("MIH data-source imported into temporary FGDB")
                    else:
                        arcpy.CreateFileGDB_management(blocklist_dir_path, 'BlockList_Test.gdb')
                        print("Exporting MIH layer data-source to temporary FGDB")
                        arcpy.FeatureClassToFeatureClass_conversion(lyr.dataSource, blocklist_path, "latest_mih_export")
                        print("MIH data-source imported into temporary FGDB")
        except Exception as e:
            raise (e)

    # Import Tax Lot Polygon into test GDB

    print("Exporting DTM Tax Lot Polygon to temporary FGDB")
    arcpy.FeatureClassToFeatureClass_conversion(dtm_path, blocklist_path, "dtm_tax_lot_polygon")
    print("DTM Tax Lot Polygon imported into temporary FGDB")

    print("Setting paths for temporary exports")
    mih_temp_path = os.path.join(blocklist_path, "latest_mih_export")
    dtm_temp_path = os.path.join(blocklist_path, "dtm_tax_lot_polygon")
    join_output_path = os.path.join(blocklist_path, "join_intersect_output")
    csv_output_path = os.path.join(output_blocklist_path, publication_date)
    print("Export paths set")

    print(dtm_temp_path)
    print(mih_temp_path)
    print(join_output_path)

    print("Setting in-memory environment path")
    arcpy.env.workspace = "in_memory"
    print("In-memory environment path set")

    # Join temporary mih layer to temporary dtm layer for spatial join and eventual export

    print("Creating feature layers from mih feature class")
    arcpy.MakeFeatureLayer_management(mih_temp_path, "mih_temp_layer")
    print("Creating feature layers from tax lot polygon feature class")
    arcpy.MakeFeatureLayer_management(dtm_temp_path, "tax_lot_poly_temp_layer")

    print("Getting MIH in-memory layer properties")
    mih_desc = arcpy.Describe("mih_temp_layer")
    print("Getting Tax Lot in-memory layer properties")
    tax_lot_poly = arcpy.Describe("tax_lot_poly_temp_layer")
    print(mih_desc.dataType, mih_desc.shapeType)
    print(tax_lot_poly.dataType, tax_lot_poly.shapeType)

    if not arcpy.Exists(join_output_path):
        print("Initiating spatial join analysis")
        arcpy.SpatialJoin_analysis(target_features=r"tax_lot_poly_temp_layer",
                                   join_features=r"mih_temp_layer",
                                   out_feature_class=join_output_path,
                                   join_operation="JOIN_ONE_TO_ONE",
                                   join_type="KEEP_COMMON",
                                   match_option="INTERSECT")
        print("Spatial join complete")
    else:
        print("Join feature already exists. Skipping spatial join analysis")

    cursor = arcpy.SearchCursor(join_output_path, ['BORO', 'BLOCK'])

    dup_block_list = []

    # Write resulting join attribute information to csv table

    with open(os.path.join(output_blocklist_path, "MIH_BlockList_{}.csv".format(publication_date)),
              'w') as mihFile:
        writer = csv.writer(mihFile, lineterminator='\n')
        writer.writerow(['BORO', 'BLOCK'])
        try:
            for row in cursor:
                boro = str(row.getValue('BORO'))
                block = str(row.getValue('BLOCK'))
                if block in dup_block_list:
                    print("Skipping dup block val - {}".format(block))
                else:
                    writer.writerow([boro, block])
                    dup_block_list.append(block)
        except Exception as e:
            raise (e)

    EndTime = datetime.datetime.now().replace(microsecond=0)
    print("Script runtime: {}".format(EndTime - StartTime))

    # Log run-time or any associated errors

    log.write(str(StartTime) + "\t" + str(EndTime) + "\t" + str(EndTime - StartTime) + "\n")
    log.close()

except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    print pymsg
    print msgs

    log.write("" + pymsg + "\n")
    log.write("" + msgs + "")
    log.write("\n")
    log.close()
