__author__ = 'Kevin_Mattmueller'


import myFunctions as mf
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import os

directoryName = raw_input("Enter name of Directory: ")
# basedir = "C:/users/kevin/desktop/"+directoryName+"/"
basedir = "C:/users/bl4ck0ut88/desktop/"+directoryName+"/"
outputDirUnfiltered = 'results_unfiltered/'
outputDirFiltered = 'results_filtered/'
valedoFolderAngles = 'Valedo_angles/'
valedoFolderAv = 'Valedo_av/'
swayFolderAngles = 'SwayStar_angles/'
swayFolderAv = 'SwayStar_av/'
files = os.listdir(basedir)

# Check if results folders already exists
if not os.path.exists(basedir+outputDirFiltered):
    os.makedirs(basedir+outputDirFiltered)

if not os.path.exists(basedir+outputDirUnfiltered):
    os.makedirs(basedir+outputDirUnfiltered)

# create output data file
# open(basedir+outputDirUnfiltered+'output_data.txt', 'w')

listValedo = []
listSway = []
listExtractedValedoData = []

# Seperate files by file type
for i in range(len(files)):
    if files[i].endswith('.txt'):
        listValedo.append(files[i])
    elif files[i].endswith('.xlsx'):
        listSway.append(files[i])

# create a list with the data from all 3 valedo sensors
for i in range(len(listValedo)):
    extractedData = mf.extractDataValedo(basedir+'/'+listValedo[i])
    listExtractedValedoData.append(extractedData)

# create a time stamp table with AV values for each axis of the 3 valedo sensors
for i in range(1, 4):
    mf.buildTimestampTable(listExtractedValedoData, i, basedir+outputDirUnfiltered+valedoFolderAv, 'av')

# create a time stamp table with angle values for each axis of the 3 valedo sensors
for i in range(4, 7):
    mf.buildTimestampTable(listExtractedValedoData, i, basedir+outputDirUnfiltered+valedoFolderAngles, 'angles')

# Compute raw data (angular velocity) and generate figures
mf.computeRawData(basedir+outputDirUnfiltered+valedoFolderAv, basedir+outputDirUnfiltered+valedoFolderAv)

# Compute raw data (angles) and generate figures
mf.computeRawData(basedir+outputDirUnfiltered+valedoFolderAngles, basedir+outputDirUnfiltered+valedoFolderAngles)

# create filtered timestamp tables and figures using Prof. Allums algorihm
meaned_threes_av_data = mf.filterData(basedir+outputDirUnfiltered+valedoFolderAv, basedir+outputDirFiltered+valedoFolderAv, 10, 2.5)
#TODO: Adjust function "filterData" so it works for angles as well.


# Process SwayStar data
# Check if results folder already exists
if not os.path.exists(basedir+outputDirUnfiltered+swayFolderAv):
    os.makedirs(basedir+outputDirUnfiltered+swayFolderAv)

if not os.path.exists(basedir+outputDirUnfiltered+swayFolderAngles):
    os.makedirs(basedir+outputDirUnfiltered+swayFolderAngles)

# Calculate values of interest for every axis and create figures
for i in range(len(listSway)):
    print '\n----------------------------------------\nComputing SwayStar data ...'
    extractedData = mf.extractDataSwayStar(basedir+'/'+listSway[i])

    axisName = ['SwayStar_AV_roll', 'SwayStar_AV_pitch', 'SwayStar_angle_roll', 'SwayStar_angle_pitch']
    yAxis = ['deg/s', 'deg/s', 'deg', 'deg']
    for j in range(1, 3):
        mf.calculateValues(extractedData[0], extractedData[j], axisName[j-1], yAxis[j-1], basedir+outputDirUnfiltered+swayFolderAv, 's',  'unfiltered_')

        if j == 2: #Plot data for pitch axis with corresponding data from valedo
            mf.drawDoublePlot(axisName[j-1]+'_double', 's', yAxis[j-1], extractedData[0], meaned_threes_av_data[0], extractedData[j], meaned_threes_av_data[1], basedir+outputDirUnfiltered+swayFolderAv)

        # Histogram
        mf.drawHisto(extractedData[j], axisName[j-1], basedir+outputDirUnfiltered+swayFolderAv)
        # mf.drawHistoXrange(extractedData[j], 'SwayStar_'+axisName[j-1], basedir+'results/', -0.1, 0.1)
    for j in range(3, 5):
        mf.calculateValues(extractedData[0], extractedData[j], axisName[j-1], yAxis[j-1], basedir+outputDirUnfiltered+swayFolderAngles, 's',  'unfiltered_')

        # Histogram
        mf.drawHisto(extractedData[j], axisName[j-1], basedir+outputDirUnfiltered+swayFolderAngles)
        # mf.drawHistoXrange(extractedData[j], 'SwayStar_'+axisName[j-1], basedir+'results/', -0.1, 0.1)
print 'done!'

# #Process Valedo data
# #Calculate values of interest for every axis and create figures
# for i in range(len(listValedo)):
#     print '\n----------------------------------------\nData from: Valedo '+listValedo[i][-11:-4]
#
#     axisName = ['valedo_x-axis', 'valedo_y-axis', 'valedo_z-axis']
#
#     for j in range(1, 4):
#         print '\n'+axisName[j-1]+':'
#         mf.calculateValues(extractedData[0], extractedData[j], listValedo[i][-11:-4]+'_'+axisName[j-1], basedir+outputDirUnfiltered, 'ms',  'unfiltered_')
#
#         #Histogram
#         mf.drawHisto(extractedData[j], listValedo[i][-11:-4]+'_'+axisName[j-1], basedir+outputDirUnfiltered)
#
#