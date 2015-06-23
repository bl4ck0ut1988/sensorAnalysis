__author__ = 'Kevin_Mattmueller'


import myFunctions as mf
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import os

directoryName = raw_input("Enter name of Directory: ")
basedir = "C:/users/kevin/desktop/"+directoryName+"/"
# basedir = "C:/users/bl4ck0ut88/desktop/"+directoryName+"/"
outputDirMultiPlots = 'multi_plots/'
outputDirUnfiltered = 'results_unfiltered/'
outputDirFiltered = 'results_filtered/'
valedoFolderAngles = 'Valedo_angles/'
valedoFolderAv = 'Valedo_av/'
swayFolderAngles = 'SwayStar_angles/'
swayFolderAv = 'SwayStar_av/'
files = os.listdir(basedir)

# Check if results folders already exists. If no, create them.
if not os.path.exists(basedir+outputDirFiltered):
    os.makedirs(basedir+outputDirFiltered)

if not os.path.exists(basedir+outputDirUnfiltered):
    os.makedirs(basedir+outputDirUnfiltered)

if not os.path.exists(basedir+outputDirMultiPlots):
    os.makedirs(basedir+outputDirMultiPlots)

# create output data file
# open(basedir+outputDirUnfiltered+'output_data.txt', 'w')

listValedo = []
listSway = []
listExtractedValedoData = []
# Seperate files by file type
for i in range(len(files)):
    if files[i].endswith('.txt') and not files[i].startswith('shift'):
        listValedo.append(files[i])
    elif files[i].endswith('.xlsx'):
        listSway.append(files[i])

# Set shift for valedo data
timeShift = -1.75
valueShift = 0.0

# create a list with the data from all 3 valedo sensors
for i in range(len(listValedo)):
    extractedData = mf.extractDataValedo(basedir+'/'+listValedo[i], timeShift)
    listExtractedValedoData.append(extractedData)

#Create a copy of the extracted Valedo data for further modifications (shifted plots)
unfilteredValedoData = listExtractedValedoData[:]

# create a time stamp table with AV values for each axis of the 3 valedo sensors
for i in range(1, 4):
    mf.buildTimestampTable(listExtractedValedoData, i, basedir+outputDirUnfiltered+valedoFolderAv, 'av')

# create a time stamp table with angle values for each axis of the 3 valedo sensors
# for i in range(4, 7):
#     mf.buildTimestampTable(listExtractedValedoData, i, basedir+outputDirUnfiltered+valedoFolderAngles, 'angles')

# Compute raw data (angular velocity) and generate figures
mf.computeRawData(basedir+outputDirUnfiltered+valedoFolderAv, basedir+outputDirUnfiltered+valedoFolderAv, 'deg/s')

# Compute raw data (angles) and generate figures
# mf.computeRawData(basedir+outputDirUnfiltered+valedoFolderAngles, basedir+outputDirUnfiltered+valedoFolderAngles, 'deg')

# create filtered timestamp tables and figures using Prof. Allums algorihm
sdFactor = 1.75
sampleRange = 10
meaned_threes_av_data = mf.filterData(basedir+outputDirUnfiltered+valedoFolderAv, basedir+outputDirFiltered+valedoFolderAv, sampleRange, sdFactor)


#Create copy of the filtered data of valedo yaw(x)-axis and shift it (+10% of range)
unshiftedYawValedo = meaned_threes_av_data[0][:]
yawShift = (np.max(unshiftedYawValedo[1])-np.min(unshiftedYawValedo[1]))*0.1
for i in range(len(unshiftedYawValedo[1])):
    unshiftedYawValedo[1][i] += yawShift

#create plot for yaw axis (unfiltered sensor 1 vs meaned_threes)
mf.drawTwinPlot('Valedo_ang.vel._yaw(x)_axis_single_vs_3_filtered', 'deg/s', listExtractedValedoData[0][0], unshiftedYawValedo[0], listExtractedValedoData[0][1], unshiftedYawValedo[1], basedir+outputDirMultiPlots)

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

    axisName = ['SwayStar_ang.vel._roll', 'SwayStar_ang.vel._pitch', 'SwayStar_angle_roll', 'SwayStar_angle_pitch']
    yAxis = ['deg/sec', 'deg/sec', 'deg', 'deg']
    singleTrigger = 0 # This trigger makes sure, that the time stamps for the cut only get subtracted once (for the single sensor data only)
    cutCountSingle = 0
    cutCountSingleRear = 0

    for j in range(1, 3):
        #Calculate Values of interest for meaned data and create plots before modifying the data for shifted plots
        valuesOfInterest = mf.calculateValues(extractedData[0], extractedData[j], axisName[j-1], yAxis[j-1], basedir+outputDirUnfiltered+swayFolderAv, 'unfiltered_')

        #Evaluate cutting lines for meaned valedos and single sensor valedo
        cutCountMeans = 0
        cutCountMeansRear = 0

        for k in range(len(meaned_threes_av_data[j][0])):
            if meaned_threes_av_data[j][0][k] >= 0:
                break
            cutCountMeans += 1

        for k in range(len(meaned_threes_av_data[j][0])):
            if meaned_threes_av_data[j][0][k] >= np.max(extractedData[0]):
                cutCountMeansRear += 1

        if not singleTrigger == 1:
            for k in range(len(unfilteredValedoData[0][0])):
                if unfilteredValedoData[0][0][k] >= 0:
                    break
                cutCountSingle += 1

        if not singleTrigger == 1:
            for k in range(len(unfilteredValedoData[0][0])):
                if unfilteredValedoData[0][0][k] >= np.max(extractedData[0]):
                    cutCountSingleRear += 1

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
        mf.drawMultiPlot(axisName[j-1]+'_with_valedo_data', yAxis[j-1], unfilteredValedoData[0][0],  meaned_threes_av_data[j][0], extractedData[0], unfilteredValedoData[0][j+1],  meaned_threes_av_data[j][1], extractedData[j], basedir+outputDirMultiPlots)

        # Histogram
        mf.drawHisto(extractedData[j], axisName[j-1], basedir+outputDirUnfiltered+swayFolderAv, valuesOfInterest)
        # mf.drawHistoXrange(extractedData[j], 'SwayStar_'+axisName[j-1], basedir+'results/', -0.1, 0.1, valuesOfInterest)
    for j in range(3, 5):
        valuesOfInterest = mf.calculateValues(extractedData[0], extractedData[j], axisName[j-1], yAxis[j-1], basedir+outputDirUnfiltered+swayFolderAngles, 'unfiltered_')

        # Histogram
        mf.drawHisto(extractedData[j], axisName[j-1], basedir+outputDirUnfiltered+swayFolderAngles, valuesOfInterest)
        # mf.drawHistoXrange(extractedData[j], 'SwayStar_'+axisName[j-1], basedir+'results/', -0.1, 0.1, valuesOfInterest)

#write valedo time shift into output file:
outputFile = open(basedir+'shift_valedo.txt', 'w')
outputFile.write('Time shift valedo: '+str(timeShift)+' sec\n')
outputFile.write('y-shift of valedo data (single(-) and meaned_threes(+)): '+str(valedoShiftY)+' %\n')
outputFile.close()

print 'done!'