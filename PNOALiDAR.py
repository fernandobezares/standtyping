import os, sys
import subprocess
import glob
import laspy

from osgeo import gdal, gdal_array, gdalconst
from math import ceil
import re
import shutil
import time
import os, subprocess
#import streamlit
from datetime import datetime


sys.path.append('C:\\LAStools\\bin')
sys.path.append('C:\\LAStools\\LASzip')

#gm = os.path.join('C:\\ProgramData\\Anaconda3\\Scripts','gdal_merge.py')
gm = os.path.join('C:\\','Users','fernando.bezares','Documents','TIC','dmm','lidar','scripts','gdal_merge.py')
command_merge = ["python", gm]

# -----------------------------------------------------------------
#                            ROOTS
# -----------------------------------------------------------------

# define the working directory

# fusion path
fusion_path = os.path.join('C:\\', 'FUSION')

# input .laz folder
input_folder = os.path.join('C:\\LiDAR\\s')
#'C:\\LiDAR\\para_procesar'
# -----------------------------------------------------------------
#                    INPUT FUSION VARIABLES
# -----------------------------------------------------------------

## GridSurfaceCreate
# -----------------------------------------------------------------

# MDE size
gsc_cellsize = '10'

# class to use in the generation of the MDE. In PNOA LiDAR 2 = ground/soil
gsc_class = '2'

## GridMetrics
# -----------------------------------------------------------------

# minimun processing height, 2 meters shrub height
gm_min_height = '2'

# classes to be processed, vegetation and soil classes [2,3,4,5]
gm_class = '2,3,4,5'

# fcc
gm_fcc = '2'

# pixel processing surface (m)
gm_pixel = '25'

# CSV2Grid
# -----------------------------------------------------------------
intensity_metrics = {
#1:"Int_Row",
#2:"Int_Column",
#3:"Int_Center_X",
#4:"Int_Center_Y",
5:"Int_Total_return_count_above_htmin",
6:"Int_minimum",
7:"Int_maximum",
8:"Int_mean",
9:"Int_mode",
10:"Int_stddev",
11:"Int_variance",
12:"Int_CV",
13:"Int_IQ",
14:"Int_skewness",
15:"Int_kurtosis",
16:"Int_AAD",
17:"Int_L1",
18:"Int_L2",
19:"Int_L3",
20:"Int_L4",
21:"Int_L_CV",
22:"Int_L_skewness",
23:"Int_L_kurtosis",
24:"Int_P01",
25:"Int_P05",
26:"Int_P10",
27:"Int_P20",
28:"Int_P25",
29:"Int_P30",
30:"Int_P40",
31:"Int_P50",
32:"Int_P60",
33:"Int_P70",
34:"Int_P75",
35:"Int_P80",
36:"Int_P90",
37:"Int_P95",
38:"Int_P99"
}
elevation_metrics = {
#   1:"Row",
#   2:"Col",
#   3:"Center X",
#   4:"Center Y",
    5:"Elev_Total_return_count_above_htmin",
    6:"Elev_minimum",
    7:"Elev_maximum",
    8:"Elev_mean",
    9:"Elev_mode",
    10:"Elev_stddev",
    11:"Elev_variance",
    12:"Elev_CV",
    13:"Elev_IQ_Int_IQ",
    14:"Elev_skewness",
    15:"Elev_kurtosis",
    16:"Elev_AAD",
    17:"Elev_L1",
    18:"Elev_L2",
    19:"Elev_L3",
    20:"Elev_L4",
    21:"Elev_L_CV",
    22:"Elev_L_skewness",
    23:"Elev_L_kurtosis",
    24:"Elev_P01",
    25:"Elev_P05",
    26:"Elev_P10",
    27:"Elev_P20",
    28:"Elev_P25",
    29:"Elev_P30",
    30:"Elev_P40",
    31:"Elev_P50",
    32:"Elev_P60",
    33:"Elev_P70",
    34:"Elev_P75",
    35:"Elev_P80",
    36:"Elev_P90",
    37:"Elev_P95",
    38:"Elev_P99",
    39:"Return_1_count_above_htmin",
    40:"Return_2_count_above_htmin",
    41:"Return_3_count_above_htmin",
    42:"Return_4_count_above_htmin",
    43:"Return_5_count_above_htmin",
    44:"Return_6_count_above_htmin",
    45:"Return_7_count_above_htmin",
    46:"Return_8_count_above_htmin",
    47:"Return_9_count_above_htmin",
    48:"Other_return_count_above_htmin",
    49:"Percentage_first_returns_above_heightbreak",
    50:"Percentage_all_returns_above_heightbreak",
    51:"(All_returns_above_heightbreak)div(Total_first_returns)100",
    52:"First_returns_above_heightbreak",
    53:"All_returns_above_heightbreak",
    54:"Percentage_first_returns_above_mean",
    55:"Percentage_first_returns_above_mode",
    56:"Percentage_all_returns_above_mean",
    57:"Percentage_all_returns_above_mode",
    58:"(All_returns_above_mean)div(Total_first_returns)100",
    59:"(All_returns_above_mode)div(Total_first_returns)100",
    60:"First_returns_above_mean",
    61:"First_returns_above_mode",
    62:"All_returns_above_mean",
    63:"All_returns_above_mode",
    64:"Total_first_returns",
    65:"Total_all_returns",
    66:"Elev_MAD_median",
    67:"Elev_MAD_mode",
    68:"Canopy_relief_ratio",#\n((mean_-_min)/(max_–_min))",
    69:"Elev_quadratic_mean",
    70:"Elev_cubic_mean",
    71:"Profile_area",
    72:"KDE_elev_modes",
    73:"KDE_elev_min_mode",
    74:"KDE_elev_max_mode",
    75:"KDE_elev_mode_range"
}

# -----------------------------------------------------------------
#                          FUNCTIONS
# -----------------------------------------------------------------
def remove_duplicates (list_of_files):
    """ get a list of .laz files and removes the lighter tile among the ones that fall in the same tile
    :param reference: is there tile code to search duplicates in
    :param list_of_files: list of .laz files"""

    # no_duplicates
    no_dup_files = []

    # no duplicate

    # tile codes
    tile_codes = []
    # loop through the list and get the tile codes
    for laz_file in list_of_files:
        # look for the tile code in the file name
        tile_code = re.findall(r'\d+\-\d+',laz_file)[0]
        # append it to the list
        tile_codes.append(tile_code)

    # remove duplicates by turning the list to set
    tile_codes_no_duplicates = list(set(tile_codes))

    for tile in tile_codes_no_duplicates:

        dupli_files = []
        sizes = []
        # dictionary to store the size of each file and teh file
        files_sizes = {}
        # loop through the laz files
        for i, laz_file in enumerate(list_of_files):
            if tile in laz_file:
                size = os.stat(laz_file).st_size
                # append the file in duplicate files
                sizes.append(size)
                dupli_files.append(laz_file)

            else:
                pass
        files_sizes.update({i: list(zip(dupli_files, sizes))})

        # iterate over the dictionary values ( laz_file, size)
        for sizes in files_sizes.values():

            # get only the sizes from the pair of sizes
            only_size = list(zip(*sizes))[1] # only_size = [sizes[1] for el in sizes]
            # get only the files
            only_files = list(zip(*sizes))[0]  # only_files = [sizes[0] for el in sizes]

            # get the maximun size value
            max_size = max(only_size)
            # get the index of the max size in the list
            max_ind = only_size.index(max_size)
            # get file with max size
            max_file = only_files[max_ind]

            # add to the exporting list
            no_dup_files.append(max_file)
    #print('longitud de lista',len (no_dup_files))

    if len(list(no_dup_files)) == 0:
        no_dup_file = list(list_of_files)
    else:
        pass
    return list(no_dup_files)


def create_folder(path):
    ''' creates in the output folder the directories passed in as argument. If the folder already exisits does nothing'''
    # create a folder list
    if os.path.exists(path):
        print("The directory", path, "exists!")
    else:
        os.mkdir(path)


# Processing of the LiDAR info
def processing(file, folder):
    # for i, file in enumerate(laz_files):

    # ------------------------------------------------------
    #               FILE DIMENSION
    # ------------------------------------------------------

    # read laz file using laspy library
    # I have pasted the Lazzip.dll and Lazzip64.dll from LASTools in order to read this
    inFile = laspy.file.File(file, mode='r')

    print(inFile.header.max, inFile.header.min)
    # maximun and minimun coordinates of the file
    maxX = inFile.header.max[0]
    maxY = inFile.header.max[1]
    minX = inFile.header.min[0]
    minY = inFile.header.min[1]

    # get the dimension of the file
    file_dim = (ceil(maxX - minX), ceil(maxY - minY))

    # ------------------------------------------------------
    #               GRID SURFACE CREATE
    # ------------------------------------------------------

    # extract the file name
    nombre = os.path.basename(file)
    # reverse the string as the standard name is more stable at the end
    file = file[::-1]
    # get x and y
    y = file[16:20]
    x = file[21:24]
    # reverse the strings back to normal
    x = int(x[::-1])
    y = int(y[::-1])
    file = file[::-1]

    # Create a list of files with the data to pass to GRID SURFACE CREATE
    filename = os.path.join(folder, str(x) + '-' + str(y) + "_lista_de_archivos.txt")
    # create the text files where the 9 .laz files will be stored and passed on to FUSION
    Txtfile = open(filename, 'w')

    if file_dim[0] >= 1999:
        extra = 2000
        fs = 2
    elif file_dim[0] <= 1999:
        extra = 1000
        fs = 1

    # calculate inital coordinate where the iteration begins
    c_ini = [x * 1000, y * 1000 - extra]
    c_fin = [x * 1000 + extra, y * 1000]

    # calculate buffer's inital  coordinate
    c_ini_buf = [c_ini[0] - 200, c_ini[1] - 200]

    # amount of cells (height and width) in the buffer 2400 m - 2 m of pixel size
    # pixel size 2.5
    t_pix = int(gsc_cellsize)
    W = extra + 400 - t_pix
    H = extra + 400 - t_pix

    # write command for FUSSION
    comando_switchgrid = '/grid:' + str(c_ini_buf[0]) + ',' + str(c_ini_buf[1]) + ',' + str(W) + ',' + str(H)
    comando_buffer = '/grid:' + str(c_ini_buf[0]) + ',' + str(c_ini_buf[1]) + ',' + str(W) + ',' + str(H)
    # obtain the files names that surrounds the file "file" in the iteration. Next the MDE will be created.
    files_list = [str(x - fs) + '-' + str(y + fs), str(x) + '-' + str(y + fs), str(x + fs) + '-' + str(y - fs),
                  str(x - fs) + '-' + str(y), str(x) + '-' + str(y), str(x + fs) + '-' + str(y),
                  str(x - fs) + '-' + str(y - fs), str(x) + '-' + str(y - fs), str(x + fs) + '-' + str(y - fs)]


    #root = file.split('.laz')[0]
    #no_ext_fn = root.split('_')
    #tail = '_' + no_ext_fn[-1]

    # get common part of the file name
    #common_name_part = "_".join(no_ext_fn[:-2]) + "_"

    for item in files_list:
        arch = re.sub(r'\d+\-\d+',item,file)
        #arch = common_name_part + item + tail + '.laz'
        Txtfile.write('{}\n'.format(arch))  # Escribir en el fichero de comandos
    Txtfile.close()

    # define the folders where the files and .exes are

    dtm_filename = o_MDT + '\\MDT_' + str(x) + '-' + str(y) + '.dtm'
    ascii_filename = o_MDT + '\\MDT_' + str(x) + '-' + str(y) + '.asc'

    dtm_filename2 = o_MDS + '\\MDS_' + str(x) + '-' + str(y) + '.dtm'
    ascii_filename2 = o_MDS + '\\MDS_' + str(x) + '-' + str(y) + '.asc'

    # ------------------------------------------------------
    #                       DEM
    # ------------------------------------------------------
    # compute the DTM, Digital Terrain Model, with only the soil class and the minimun
    string = fusion_path + '\\GridSurfaceCreate.exe' + ' ' + comando_buffer + ' /class:2' + ' ' + dtm_filename + ' ' + gsc_cellsize + ' m m 0 0 0 0 ' + filename
    # compute the DEM, Digital Elevation model, with the soil and the vegetation classes
    string2 = fusion_path + '\\GridSurfaceCreate.exe' + ' ' + comando_buffer + ' /class:2,3,4,5' + ' ' + dtm_filename2 + ' ' + gsc_cellsize + ' m m 0 0 0 0 ' + filename

    print(string)

    # pass to fusion
    proc = subprocess.run(string, shell=True)
    proc = subprocess.run(string2, shell=True)

    # ------------------------------------------------------
    #                       CLIP DTM
    # ------------------------------------------------------
    # ClipDTM [switches] InputDTM OutputDTM MinX MinY MaxX MaxY

    # filenames for the clipped image
    clip_filename = o_MDT + '\\MDT_' + str(x) + '-' + str(y) + '_clip' + '.dtm'
    asclip_filename = o_MDT + '\\MDT_' + str(x) + '-' + str(y) + '_clip' + '.asc'

    # nombres dem
    clip_filename2 = o_MDS + '\\MDS_' + str(x) + '-' + str(y) + '_clip' + '.dtm'
    asclip_filename2 = o_MDS + '\\MDS_' + str(x) + '-' + str(y) + '_clip' + '.asc'
    # define extent
    minx = str(c_ini[0])
    miny = str(c_ini[1])
    maxx = str(c_fin[0])
    maxy = str(c_fin[1])

    # string to pass to FUSION
    string = fusion_path + '\\ClipDTM.exe' + ' ' + dtm_filename + ' ' + clip_filename + ' ' + minx + ' ' + miny + ' ' + maxx + ' ' + maxy
    # DMS
    string2 = fusion_path + '\\ClipDTM.exe' + ' ' + dtm_filename2 + ' ' + clip_filename2 + ' ' + minx + ' ' + miny + ' ' + maxx + ' ' + maxy
    #print('comando ClipDTM: {}'.format(string))

    proc = subprocess.run(string, shell=True)
    proc = subprocess.run(string2, shell=True)

    os.remove(dtm_filename)
    os.remove(dtm_filename2)
    # ------------------------------------------------------
    #                     DTM2ASCII
    # ------------------------------------------------------

    # turn dtm into asc
    # Crear .asc

    string = fusion_path + '\\DTM2ASCII.exe' + ' ' + clip_filename + ' ' + asclip_filename
    string2 = fusion_path + '\\DTM2ASCII.exe' + ' ' + clip_filename2 + ' ' + asclip_filename2
    #print('\ncomando DTM2ASCII: {}'.format(string))

    proc = subprocess.run(string, shell=True)
    proc = subprocess.run(string2, shell=True)

    # --------------------------
    #           MDAV
    # --------------------------
    create_CHM((asclip_filename2,asclip_filename))

    #os.remove(asclip_filename2)
    # --------------------------
    #           ASPECT
    # --------------------------
    op1 = gdal.DEMProcessingOptions(computeEdges = True,slopeFormat = "percent")
    aspect_filename = o_Asp + '\\Aspect_' + str(x) + '-' + str(y) + '.tif'
    slope_filename = o_Slo + '\\Slope_' + str(x) + '-' + str(y) + '.tif'

    aspect = gdal.DEMProcessing(aspect_filename, asclip_filename, 'aspect', computeEdges=True)
    slope = gdal.DEMProcessing(slope_filename,asclip_filename,'slope', options = op1)
    # -------------------------
    #       GRIDMETRICS
    # -------------------------

    archivos = glob.glob(os.path.join(o_MDT, '*clip.dtm'))  # dtm fold out de la primera

    # define the folders where the files and .exes are

    csv_filename = o_metric + '\\metric_' + str(x) + '-' + str(y) + '.csv'

    string = fusion_path + '\\gridmetrics.exe'

    # Switches
    # grid switch
    # string = string + ' /verbose' + ' ' + comando_switchgrid

    string = string + ' ' + comando_switchgrid

    string = string + ' /minht:' + str(gm_min_height)

    string = string + ' /class:' + str(gm_class)

    string = string + ' /outlier:-0.5,50'

    string = string + ' ' + clip_filename + ' ' + gm_fcc + ' ' + gm_pixel + ' ' + csv_filename + ' ' + file

    # imprimir el comando
    #print('\ncomando Gridmetrics: {}'.format(string))
    proc = subprocess.run(string, shell=True)

    csv_filename_elevation_stats = o_metric + '\\metric_' + str(x) + '-' + str(y) + '_all_returns_elevation_stats.csv'
    csv_filename_intensity_stats = o_metric + '\\metric_' + str(x) + '-' + str(y) + '_all_returns_intensity_stats.csv'
    # checks the type of metrics

    # iterates over the files in the folder

    for key in intensity_metrics.keys():
        # extract the file name

        asc_filename = o_raster + '\\raster_' + os.path.basename(csv_filename).split('.csv')[0]+'_' + intensity_metrics[key] + '.asc'

        string = fusion_path + '\\CSV2Grid.exe'

        string = string + ' ' + csv_filename_intensity_stats + ' ' + str(key) + ' ' + asc_filename

        # print('\ncomando CSV2Grid: {}'.format(string))

        proc = subprocess.run(string, shell=True)
        # Crear .dtm

    for key in elevation_metrics.keys():
        # extract the file name

        asc_filename = o_raster + '\\raster_' + os.path.basename(csv_filename).split('.csv')[0] +'_'+ elevation_metrics[key] + '.asc'

        string = fusion_path + '\\CSV2Grid.exe'

        string = string + ' ' + csv_filename_elevation_stats + ' ' + str(key) + ' ' + asc_filename

        # print('\ncomando CSV2Grid: {}'.format(string))

        proc = subprocess.run(string, shell=True)
        # Crear .dtm


# Create the Canopy Height Model
def create_CHM(pair):
    """ Creates a Canopy Height Model by substractic a DEM to a DSM. The input is a pair of files where on the first
     position lies the DSM and in the second one the DEM"""

    # select raster from the tuple
    dsm = pair[0]
    dtm = pair[1]

    # Open raster
    dsm_raster = gdal.Open(dsm)
    dtm_raster = gdal.Open(dtm)
    # select band 1
    dem_b1 = dtm_raster.GetRasterBand(1)##.SetNoDataValue(0)
    dsm_b1 = dsm_raster.GetRasterBand(1)##.SetNoDataValue(0)

    # read as Array
    dem_arr = dem_b1.ReadAsArray()
    dsm_array = dsm_b1.ReadAsArray()

    # apply equation
    data = dsm_array - dem_arr

    # define output directory
    o_MDAV = os.path.join(o_temp,'MDAV_LiDAR')

    # create the output directory
    if os.path.exists(o_MDAV):
        print("The directory", o_MDAV, "exists!")
    else:
        os.makedirs(o_MDAV)

    # define output file name
    # get tile code
    tile_code = os.path.basename(dsm).split('_')[1]

    # output filename
    output = os.path.join(o_MDAV,'MDAV_'+ tile_code + '.tif')

    # save array, using dsm_raster as a prototype
    gdal_array.SaveArray(data.astype("float32"), output, "GTIFF", dtm_raster)

    # print the file output


def create_CHM(pair):
    """ Creates a Canopy Height Model by substractic a DEM to a DSM. The input is a pair of files where on the first
     position lies the DSM and in the second one the DEM"""
    import numpy as np
    # select raster from the tuple
    dsm = pair[0]
    dtm = pair[1]

    # Open raster
    dsm_raster = gdal.Open(dsm)
    dtm_raster = gdal.Open(dtm)
    # select band 1
    dem_b1 = dtm_raster.GetRasterBand(1)
    dsm_b1 = dsm_raster.GetRasterBand(1)

    # nodata array
    nodata = -9999

    # read as Array
    dem_arr = dem_b1.ReadAsArray()
    dsm_array = dsm_b1.ReadAsArray()


    # define output directory
    o_MDAV = os.path.join(o_temp, 'MDAV_LiDAR')

    # create the output directory
    if os.path.exists(o_MDAV):
        print("The directory", o_MDAV, "exists!")
    else:
        os.makedirs(o_MDAV)

    # define output file name
    # get tile code
    tile_code = os.path.basename(dsm).split('_')[1]

    # output filename
    output = os.path.join(o_MDAV, 'MDAV_' + tile_code + '.tif')

    # save array, using dsm_raster as a prototype
    gdal_array.SaveArray(data.astype("float32"), output, "GTIFF", dtm_raster)

    # print the file output
# -------------------------------------------------
# merge the images
# ------------------------------------------------
def merge_tiles ():
    # create a dictionary where every value is a list with all the files for each variable
    d = {}
    # elevation metrics
    for j in elevation_metrics.values():
        d[j] = glob.glob(os.path.join(o_raster,'*'+j+'.asc'))
    # intensity metrics
    for j in intensity_metrics.values():
        d[j] = glob.glob(os.path.join(o_raster, '*' + j + '.asc'))

    # list the files for each varaibles
    slo = glob.glob(os.path.join(o_Slo,'*.tif'))
    mdt = glob.glob(os.path.join(o_MDT,'*.asc'))
    mdav = glob.glob(os.path.join(o_temp,'MDAV_LiDAR','*.tif'))
    aspectf = glob.glob(os.path.join(o_Asp,'*.tif'))

    # update the dictionary with all the variables
    d.update({'slope':slo,'mdt':mdt,'mdav':mdav,'aspect':aspectf})

    # define the transalte options
    op = gdal.TranslateOptions(outputType = gdalconst.GDT_Float32,outputSRS ='epsg:25830', noData=None)

    # create a directory to add the results
    int_results = o_final # key + 'Productos_intermedios'
    if os.path.exists(int_results):
        pass
    else:
        os.mkdir(int_results)

    name_file = os.path.basename(key);
    # print(d,name_file)

    # loop through the variables and transalte and
    for i in d.keys():
        print(i,'number of files: ',len(d[i]))
        try:
            gdal.BuildVRT(os.path.join(int_results,name_file + "_" + i +".vrt"), d[i])
            gdal.Translate(os.path.join(int_results,name_file + "_" + i +".tif"),
                           os.path.join(int_results,name_file + "_" + i +".vrt"),
                           options=op)
            os.remove(os.path.join(int_results,name_file + "_" + i +".vrt"))
        except:
            error = open(os.path.join(o_final,'error.txt'),'a+')
            error.write('\nfailed to transalte:'+i)
            error.close()



def merge_files(list, name, path):
    """
    :param list: list of files to merge
    :param name: name of the variable to represent
    :param path: path to hold the merged files
    :return: NONE, merges a list of files that holds a variable and paste it in the specified path
    uses gdal_merge.py
    """
    results = os.path.join(path, 'Resultados')

    if os.path.exists(results):
        pass
    else:
        os.mkdir(results)

    # merged asc files in one GRIDSURFACE CREATE
    out = os.path.join(results, os.path.basename(path)+'_'+ name + '.tif')
    #list.append('-a_nodata')
    #list.append('none')#(str(-9999))
    list.append('-o')
    list.append(out)
    list.insert(0, '')
    # añadir lista con los comandos
    list = command_merge + list
    subprocess.run(list,shell = True)

# remove folders
def remove_folders(folders):
    for folder in folders:
        shutil.rmtree(folder)



def merge_admin_units(path):
    """ the path points to a directory form which the function will walk down recursively looking for files to merge
     holding the same variable names.Therefore, if you select a directory that holds CCAA,
     it will create the merge for the CCAA and if you select a directory for a country it will merge
     using the CCAA level files """
    d = {}

    # walk down the path
    for root, dirs, files in os.walk(os.path.join(path)):
        # if the path has the folder "Productos_intermedios" then it means it is a province with the files merged
        if 'Productos_intermedios' in root:
            # print(root)

            # elevation metrics
            for j in list(elevation_metrics.values()) + list(intensity_metrics.values()) + ['aspect','MDAV','MDT','slope']:
                if d.get(j) is None:
                    print('IS NONE: ',d.get(j), j)
                    d.update({j:glob.glob(os.path.join(root, '*' + j + '.tif'))})
                else:
                    newVar = glob.glob(os.path.join(root, '*' + j + '.tif'))
                    lista = d.get(j)
                    newlist = lista + newVar
                    #print(newlist)
                    d.update({j: newlist})



    for element in d.keys():
        #print(d.get(element),element,path)
        merge_files(d.get(element),element,path)

# --------------------------------------------------------------------------------------
#                                   FIND DUPLICATES
#---------------------------------------------------------------------------------------

def find_processed(txt):
    """
    Finds the .laz files already processed reading the tiempos_procesados.txt
    :param: txt the txt with the files already processed
    :return:
    """
    with open(txt) as f:
        content = f.readlines()

    procesados = [procesado.split('PROCESSING')[0] for procesado in content]

    return procesados

def remove_processed_from_list(procesados,no_procesados):
    """
    Removes the processed files from the list to be processed
    :param procesados: list of files from which laz files will be removed
    :param no_procesados
    :return: list of unprocessed laz_files
    """
    unprocessed = sorted(list(set(no_procesados)- set(procesados)))

    return unprocessed



def create_processing_dictionary(input_folder):
    """
    Indicate an input folder and generates a dictionary holding in the keys the folders paths and in the values a list of
    the laz files contained in each folder
    :param input_folder:
    :return:
    """
    # where the las files are
    folders = []
    # this dictionary will hold
    dict = {}

    # get all the dirs and files inside the data folder
    for root, dirs, files in os.walk(input_folder, topdown=False):
        for name in dirs:
            fold = (os.path.join(root, name))
            folders.append(fold)

    # create a dictionary where every folder and subfolder has a list with the laz files
    for fold in folders:
        #print(fold)
        file = glob.glob(os.path.join(fold,'*.laz'))
        dict.update({fold: file})

    return dict

print ('------------------------------------------------------------------------------------')
mainstart = time.time()
print ( '              START PROCESSING TIME', mainstart)

# create the dictionary with the files to process
to_process = create_processing_dictionary(input_folder)

print(to_process)
# iterate for every element of the dictionary (folder,laz files)
for key in to_process.keys():
    print('-------------------------------\nKEY USED:',key,'\n-------------------------------')

    if 'Productos_intermedios' in key or 'temp_LiDAR' in key:
        pass
        # province folder
    else:
        # if the folder doesn't have laz files then it means it is a CCAA folder
        if len(glob.glob(os.path.join(key, '*.laz'))) != 0:

            # Create folders
            # create final product folder
            o_final = os.path.join(key, 'Productos_intermedios')

            # create temporal folders
            o_temp = os.path.join(key, 'temp_LiDAR')
            o_raster = os.path.join(o_temp, 'Rasters_LiDAR')
            o_metric = os.path.join(o_temp, 'Metrics_LiDAR')
            o_MDT = os.path.join(o_temp, 'MDT_LiDAR')
            o_MDS = os.path.join(o_temp, 'MDS_LiDAR')
            o_Asp = os.path.join(o_temp, 'Aspect_LiDAR')
            o_MDAV = os.path.join(o_temp, 'MDAV_LiDAR')
            o_Slo = os.path.join(o_temp, 'Slope_LiDAR')

            # apply the list to the create folder function
            for element in [o_temp, o_raster, o_MDT, o_MDS, o_metric, o_Asp, o_final, o_Slo]:
                create_folder(element)

            # process the laz file lists:
            # if there is a 'tiempos procesados.txt' it means there are processed files.
            if os.path.exists(os.path.join(o_final, 'tiempos procesados.txt')):

                # find the processed files in the log " tiempos procesados.txt'
                processed = find_processed(os.path.join(o_final, 'tiempos procesados.txt'))

                # remove the processed files from the list
                unprocessed = remove_processed_from_list(processed,to_process[key])

            else:
                unprocessed = to_process[key]

            print('unprocessed',unprocessed)
            # remove duplicated files in the list
            #clean_files = remove_duplicates(list(unprocessed))

            # sort the files
            clean_files = sorted(unprocessed)

            print('KEY:{}\n CLEAN FILES:{}\n'.format(key, clean_files))
            print('KEY:{}\n OLD FILES:{}\n'.format(key, unprocessed))
            #print('ELEMENTS REMOVED: {}'.format(set(dict[key]).difference(set(clean_files))))

            for i, file in enumerate(clean_files):
                print('Processing progress {}/{}:'.format(i, len(clean_files)))
                start = time.time()
                print(file)
                try:
                    start = time.time()
                    processing(file=file, folder=key)
                    end = time.time()

                    #  write if the file is processed and processing time
                    hora = str(datetime.utcnow())
                    log = open(os.path.join(o_final, 'tiempos procesados.txt'), 'a+')
                    log.write(file + 'PROCESSING TIME: ' + str((end - start) / 60) + ' mins ' + 'hora: ' + hora + '\n')
                    log.close()

                    print('---------------------------------------')
                    print('PROCESSING TIME:', (end - start) / 60, 'mins')
                    print('---------------------------------------')
                except:
                    hora = str(datetime.utcnow())
                    log = open(os.path.join(o_final, 'archivosNoProcesados.txt'), 'a+')
                    log.write(file + 'hora: ' + hora + '\n')
                    log.close()

                #streamlit.legacy_caching.clear_cache()
            merge_tiles()
            #remove_folders([o_MDT, o_MDS, o_Asp, o_Slo])

        else:
            print('no length:',key)
            merge_admin_units(key)


## MERGE SPAIN
merge_admin_units(input_folder)

mainEnd = time.time()
print ( '              END PROCESSING TIME', mainEnd)
print ( '              TOTAL PROCESSING TIME', (mainEnd - mainstart)/60,'mins')











