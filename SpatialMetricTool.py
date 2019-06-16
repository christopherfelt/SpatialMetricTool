import arcpy
import os
import sys

arcpy.env.overwriteOutput = True

# Make this the first input display - Set Environment
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# Make this the second display - Raster List
rasterList = arcpy.GetParameterAsText(1).split(';')

# Make this the third display - Shapefile List
shapefileList = arcpy.GetParameterAsText(2).split(';')

# Make this the fourth display - Choose output folder
outputFolderUser = arcpy.GetParameterAsText(3)

# Make this the fifth display - Choose Fragstat model file
fca = arcpy.GetParameterAsText(4)

# Generates folders for tifs, batch files, tables
outputFolder = outputFolderUser + '\\' + 'output'
tifFolder = outputFolder + '\\' + 'tifFolder'
batchFolder = outputFolder + '\\' + 'batchFolder'
fstablesFolder = outputFolder + '\\' + 'fstablesFolder'

folderList = [outputFolder, tifFolder, batchFolder, fstablesFolder]

for folder in folderList:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Rasters and shapefiles are given numbers based on their place in the list
# Tif folders
i = 1
shpFileFolders = []
for raster in rasterList:
    rasterNameTif = tifFolder + '\\' + 'raster' + str(i)
    os.makedirs(rasterNameTif)
    j = 1
    for shapefile in shapefileList:
        shpName = rasterNameTif + '\\' + 'shp' + str(j)
        os.makedirs(shpName)
        shpFileFolders.append(shpName)

        j += 1
    i += 1

# Batch folder
i = 1
shpBatchList = []
for raster in rasterList:
    rasterNameBatch = batchFolder + '\\' + 'raster' + str(i)
    os.makedirs(rasterNameBatch)
    shpBatchList.append(rasterNameBatch)
    i += 1

# Fragstats tables folder
i = 1
classFileList = []
for raster in rasterList:
    rasterNamefstable = fstablesFolder + '\\' + 'raster' + str(i)
    os.makedirs(rasterNamefstable)
    classFileList.append(rasterNamefstable)
    i += 1

j = 1
b = 0
k = 0

fbtList = []
tifList = []
fbtMasterList = []
for raster in rasterList:

    n = 1
    tifList = []
    fbtList = []
    for shapefile in shapefileList:

        cursor = arcpy.SearchCursor(shapefile)
        arcpy.AddMessage(shapefile)

        ii = 1
        tifList = []

        text_file = open(shpBatchList[b] + '\\' + 'shp' + str(n) + '.fbt', "w")
        fbtFile = shpBatchList[b] + '\\' + 'shp' + str(n) + '.fbt'
        fbtList.append(fbtFile)

        for row in cursor:
            clippedFile = shpFileFolders[k] + '\\' + 'poly' + str(ii) + '.tif'

            feat = row.Shape

            arcpy.Clip_management(in_raster=raster, rectangle="#",
                                  out_raster=clippedFile, in_template_dataset=feat,
                                  nodata_value="255", clipping_geometry="ClippingGeometry",
                                  maintain_clipping_extent="NO_MAINTAIN_EXTENT")

            tifList.append(clippedFile)

            ii += 1
        for tif in tifList:
            text_file.write(tif + ', x, 999, x, x, 1, x, IDF_GeoTIFF' + '\n')

        text_file.close()
        n += 1
        k += 1

    fbtMasterList.append(fbtList)
    b += 1


g = 0
for fbtListIndex in fbtMasterList:
    f = 1

    cFL = classFileList[g]
    for fbt in fbtListIndex:

        classFileDir = cFL + '\\' + 'shp' + str(f)

        arcpy.AddMessage("\nRUNNING THE FRAGSTATS BATCH ...\n")
        frg_path = r'"C:\Program Files (x86)\Fragstats 4\frg.exe"'
        try:
            os.system(frg_path + " /m " + fca + " /b " + fbt + " /o " + classFileDir)
        except:
            arcpy.AddMessage("\n\nWas not able to run FRAGSTATS. Quitting.\n\n")
            sys.exit()
        f += 1
    g += 1