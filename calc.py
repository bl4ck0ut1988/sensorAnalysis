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
timeShift = -0.75
valueShift = 0.0

for i in range(len(listValedo)):
    extractedData = mf.extractDataValedo(basedir+'/'+listValedo[i], timeShift, valueShift)
    listExtractedValedoData.append(extractedData)

#  mf.drawPlot('test_axis_', 'deg/s', listExtractedValedoData[0][0], listExtractedValedoData[0][3], basedir)
unfilteredValedoData = listExtractedValedoData[:]

# create a time stamp table with AV values for each axis of the 3 valedo sensors
for i in range(1, 4):
    mf.buildTimestampTable(listExtractedValedoData, i, basedir+outputDirUnfiltered+valedoFolderAv, 'av')

# create a time stamp table with angle values for each axis of the 3 valedo sensors
for i in range(4, 7):
    mf.buildTimestampTable(listExtractedValedoData, i, basedir+outputDirUnfiltered+valedoFolderAngles, 'angles')

# Compute raw data (angular velocity) and generate figures
mf.computeRawData(basedir+outputDirUnfiltered+valedoFolderAv, basedir+outputDirUnfiltered+valedoFolderAv, 'deg/s')

# Compute raw data (angles) and generate figures
mf.computeRawData(basedir+outputDirUnfiltered+valedoFolderAngles, basedir+outputDirUnfiltered+valedoFolderAngles, 'deg')

# create filtered timestamp tables and figures using Prof. Allums algorihm
sdFactor = 1.75
sampleRange = 10
meaned_threes_av_data = mf.filterData(basedir+outputDirUnfiltered+valedoFolderAv, basedir+outputDirFiltered+valedoFolderAv, sampleRange, sdFactor)
#TODO: Adjust function "filterData" so it works for angles as well.


# Process SwayStar data
# Check if results folder already exists
if not os.path.exists(basedir+outputDirUnfiltered+swayFolderAv):
    os.makedirs(basedir+outputDirUnfiltered+swayFolderAv)

if not os.path.exists(basedir+outputDirUnfiltered+swayFolderAngles):
    os.makedirs(basedir+outputDirUnfiltered+swayFolderAngles)


# Calculate values of interest for every axis and create figures

valedoShiftY = 10 # y-shift of the valedo data in ..% in respect of the swayStar range (y-axis)

for i in range(len(listSway)):
    print '\n----------------------------------------\nComputing SwayStar data ...'
    extractedData = mf.extractDataSwayStar(basedir+'/'+listSway[i])

    axisName = ['SwayStar_AV_roll', 'SwayStar_AV_pitch', 'SwayStar_angle_roll', 'SwayStar_angle_pitch']
    yAxis = ['deg/sec', 'deg/sec', 'deg', 'deg']
    singleTrigger = 0 # This trigger makes sure, that the time stamps for the cut only get subtracted once (for the single sensor data only)
    cutCountSingle = 0
    cutCountSingleRear = int(np.max(unfilteredValedoData[0][0])-np.max(extractedData[0]))

    for j in range(1, 3):
        mf.calculateValues(extractedData[0], extractedData[j], axisName[j-1], yAxis[j-1], basedir+outputDirUnfiltered+swayFolderAv, 'unfiltered_')

        #Evaluate cutting lines for meaned valedos and single sensor
        cutCountMeans = 0
        cutCountMeansRear = int(np.max(meaned_threes_av_data[j][0])-np.max(extractedData[0]))

        for k in range(len(meaned_threes_av_data[j][0])):
            if meaned_threes_av_data[j][0][k] >= 0:
                break
            cutCountMeans += 1

        if not singleTrigger == 1:
            for k in range(len(unfilteredValedoData[0][0])):
                if unfilteredValedoData[0][0][k] >= 0:
                    break
                cutCountSingle += 1

        print 'counter single: '+str(cutCountSingle)

        #Cut out the overlapping valedo values from
        # meaned:
        for k in range(cutCountMeans):
            del meaned_threes_av_data[j][0][0]
            del meaned_threes_av_data[j][1][0]

        for k in range(cutCountMeansRear):
            del meaned_threes_av_data[j][0][-1]
            del meaned_threes_av_data[j][1][-1]

        # and single sensor(s)
        for k in range(cutCountSingle):
            if not singleTrigger == 1:
                del unfilteredValedoData[0][0][0]
            del unfilteredValedoData[0][j+1][0]

        for k in range(cutCountSingleRear):
            if not singleTrigger == 1:
                del unfilteredValedoData[0][0][-1]
            del unfilteredValedoData[0][j+1][-1]

        singleTrigger = 1

        #Shift values of valedo data before plotting (shift meaned threes up and single valeo sensor down 10% of valedo range)
        mf.shiftY(meaned_threes_av_data[j][1], unfilteredValedoData[0][j+1], (np.max(extractedData[j])-np.min(extractedData[j]))*valedoShiftY/100)

        #Plot data for pitch and roll axis with corresponding data from valedo (single unfiltered, 3 sensors filtered)
        mf.drawMultiPlot(axisName[j-1]+'_with_valedo_data', yAxis[j-1], extractedData[0], meaned_threes_av_data[j][0], unfilteredValedoData[0][0], extractedData[j], meaned_threes_av_data[j][1], unfilteredValedoData[0][j+1], basedir+outputDirUnfiltered+swayFolderAv)

        # Histogram
        mf.drawHisto(extractedData[j], axisName[j-1], basedir+outputDirUnfiltered+swayFolderAv)
        # mf.drawHistoXrange(extractedData[j], 'SwayStar_'+axisName[j-1], basedir+'results/', -0.1, 0.1)
    for j in range(3, 5):
        mf.calculateValues(extractedData[0], extractedData[j], axisName[j-1], yAxis[j-1], basedir+outputDirUnfiltered+swayFolderAngles, 'unfiltered_')

        # Histogram
        mf.drawHisto(extractedData[j], axisName[j-1], basedir+outputDirUnfiltered+swayFolderAngles)
        # mf.drawHistoXrange(extractedData[j], 'SwayStar_'+axisName[j-1], basedir+'results/', -0.1, 0.1)

#write valedo time shift into output file:
outputFile = open(basedir+outputDirUnfiltered+swayFolderAv+'shift_valedo.txt', 'w')
outputFile.write('Time shift valedo: '+str(timeShift)+' sec\n')
outputFile.write('y-shift of valedo data (single(-) and meaned_threes(+)): '+str(valedoShiftY)+' %\n')
outputFile.close()

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
#         mf.calculateValues(extractedData[0], extractedData[j], listValedo[i][-11:-4]+'_'+axisName[j-1], basedir+outputDirUnfiltered, 'unfiltered_')
#
#         #Histogram
#         mf.drawHisto(extractedData[j], listValedo[i][-11:-4]+'_'+axisName[j-1], basedir+outputDirUnfiltered)
#
#