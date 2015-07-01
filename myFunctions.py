__author__ = 'Kevin_Mattmueller'
from pylab import *
import xlrd
import numpy as np
import matplotlib.pyplot as plt
import os
import xlsxwriter

def graph(formula, x_range):
    x = np.array(x_range)
    y = eval(formula)
    plt.plot(x, y)
    plt.show()

def drawPlot(axisName, yLabel, timeStamps, values, baseDirectory):
    # fit = polyfit(timeStamps, values, 1)
    # # plot data
    # x = np.array(range(int(np.min(timeStamps)), int(np.max(timeStamps))))
    # y = eval(str(fit[0])+"*x+"+str(fit[1]))
    # plt.axis([int(np.min(timeStamps)), int(np.max(timeStamps)), int(np.min(values)), int(np.max(values))])
    plt.title(axisName)
    plt.xlabel('sec')
    plt.ylabel(yLabel)
    # plt.xlim([0,100])
    # plt.plot(x, y)
    plt.plot(timeStamps, values)
    plt.savefig(baseDirectory+axisName+'.png')
    plt.clf()

def drawTwinPlot(axisName, yLabel, timeStampsValedoSingle, timeStampsValedoFiltered, valuesValedoSingle, valuesValedoFiltered, baseDirectory):
    # fit = polyfit(timeStamps, values, 1)
    # # plot data
    # x = np.array(range(int(np.min(timeStamps)), int(np.max(timeStamps))))
    # y = eval(str(fit[0])+"*x+"+str(fit[1]))
    # plt.axis([int(np.min(timeStamps)), int(np.max(timeStamps)), int(np.min(values)), int(np.max(values))])
    plt.title(axisName)
    plt.xlabel('sec')
    plt.ylabel(yLabel)
    #plt.xlim([0,100])
    # plt.plot(x, y)
    plt.plot(timeStampsValedoSingle, valuesValedoSingle, label='Valedo 1 sensor unfiltered')
    plt.plot(timeStampsValedoFiltered, valuesValedoFiltered, label='Valedo 3 sensors filtered(+ shift)')
    plt.legend(loc=1,prop={'size':7.5})
    plt.savefig(baseDirectory+axisName+'.png')
    plt.clf()

def drawMultiPlot(axisName, yLabel, timeStampsValedoSingle, timeStampsValedoFiltered, timeStampsSway, valuesValedoSingle, valuesValedoFiltered, valuesSway, baseDirectory):
    # fit = polyfit(timeStamps, values, 1)
    # # plot data
    # x = np.array(range(int(np.min(timeStamps)), int(np.max(timeStamps))))
    # y = eval(str(fit[0])+"*x+"+str(fit[1]))
    # plt.axis([int(np.min(timeStamps)), int(np.max(timeStamps)), int(np.min(values)), int(np.max(values))])
    plt.title(axisName)
    plt.xlabel('sec')
    plt.ylabel(yLabel)
    # plt.xlim([0,100])
    # plt.plot(x, y)
    plt.plot(timeStampsValedoSingle, valuesValedoSingle, label='Valedo 1 sensor unfiltered(- shift)')
    plt.plot(timeStampsValedoFiltered, valuesValedoFiltered, label='Valedo 3 sensors filtered(+ shift)')
    plt.plot(timeStampsSway, valuesSway, label='SwayStar')
    plt.legend(loc=1,prop={'size':7.5})
    plt.savefig(baseDirectory+axisName+'.png')
    plt.clf()

# Calculation of values of interest
def calculateValues(timeStamps, values, axisName, yLabel, baseDirectory, filterStatus):

    fit = polyfit(timeStamps, values, 1)

    #Draw plots with input data
    drawPlot(axisName, yLabel, timeStamps, values, baseDirectory)

    fit_fn = poly1d(fit) # fit_fn is now a function which takes in x and returns an estimate for y

    # Calculate rms
    sumSqr = 0
    for i in range(len(timeStamps)):
        xValue = values[i] - fit_fn(timeStamps[i])
        sumSqr += math.pow(xValue, 2)
    rms = math.sqrt((sumSqr/len(values)))

    #Copy list of values and sort it small --> big
    sortedValues = values[:]
    sortedValues.sort()

    # set and print the values below
    roundDigits = 4
    min = "min: "+str(np.round(np.min(values), roundDigits))
    max = "max: "+str(np.round(np.max(values), roundDigits))
    mean = "mean: "+str(np.round(np.mean(values), roundDigits))
    ptp = "ptp: "+str(np.round((np.max(values)-np.min(values)), roundDigits))
    ptp90 = "ptp90%: "+str(np.round(((sortedValues[(len(sortedValues)-1)-(len(sortedValues)/20)])-(sortedValues[len(sortedValues)/20])), roundDigits))
    sd = "standard deviation: "+str(np.round(np.std(values), roundDigits))
    rms = "noise (rms): "+str(np.round(rms, roundDigits))

    # open and write into output file:
    outputFile = open(baseDirectory+filterStatus+'output_data.txt', 'a')
    outputFile.write(axisName+"\n")
    outputFile.write(min+'\n')
    outputFile.write(max+'\n')
    outputFile.write(mean+'\n')
    outputFile.write(ptp+'\n')
    outputFile.write(ptp90+'\n')
    # outputFile.write("Linear Reg. Function: "+str(fit_fn)+'\n')
    outputFile.write(sd+'\n')
    outputFile.write(rms+'\n\n')
    outputFile.close()

    #Save values of interest into a list and return it for further use
    valuesOfInterest = []
    valuesOfInterest.append(mean)
    valuesOfInterest.append(sd)
    valuesOfInterest.append(ptp90)
    return valuesOfInterest


# Creates histogram with 40 bins (automatically sets range)
def drawHisto(listOfValues, axisName, saveDirectory, valuesOfInterest):

    plt.title(axisName)
    plt.hist(listOfValues, bins=40, label=str(valuesOfInterest[0]+'\n'+valuesOfInterest[1]+'\n'+valuesOfInterest[2]))
    plt.legend(loc=1,prop={'size':7.5})
    plt.savefig(saveDirectory+axisName+'_histo.png')
    plt.clf()


# Creates a histogram with 40 bins using the ptp range of the data
def drawHistoXrange(listOfValues, axisName, saveDirectory, x_min, x_max, valuesOfInterest):

    plt.title(axisName)
    plt.xlim(x_min, x_max)
    plt.hist(listOfValues, bins=40, label=str(valuesOfInterest[0]+'\n'+valuesOfInterest[1]+'\n'+valuesOfInterest[2]))
    plt.legend(loc=1,prop={'size': 7.5})
    plt.savefig(saveDirectory+axisName+'_histo.png')
    plt.clf()


# Extracts timestamps and corresponding angular velocities (x,y,z)
# Returns a list, containing 4 more sub lists with timestamps and angular Velocities (x,y,z)
# Lists can be accessed by index: [0]: timestamps, [1] AV x-axis, [2] AV y-axis, [3] AV z-axis,
def extractDataValedo(fileLocation):
    sensorData = open(fileLocation)
    extractedData = []
    timeStamp = []
    avx = []
    avy = []
    avz = []
    ax = []
    ay = []
    az = []

    # read trough every line of .txt file and extract timestamp + x,y,z Angular Velocities
    for line in sensorData.readlines():
        if not line.startswith("Sensor"):
            splittedLine = line.split(",")
            timeStamp.append(float(splittedLine[1])/1000)
            avx.append(float(splittedLine[14]))
            avy.append(float(splittedLine[15]))
            avz.append(float(splittedLine[16][:-2]))

    #Create a unfiltered copy for each data set
    extractedData.append(timeStamp)
    extractedData.append(avx)
    extractedData.append(avy)
    extractedData.append(avz)
    extractedData.append(ax)
    extractedData.append(ay)
    extractedData.append(az)

    # Calculate angles
    # Angle (t+1) = Angle (t) + Velocity (t)*Sampling interval
    for i in range(1, 4):
        for j in range(len(extractedData[i])):
            if j == 0:
                extractedData[i+3].append(0.0+extractedData[i][j]*extractedData[i-1][j])
            else:
                extractedData[i+3].append(extractedData[i+3][j-1]+extractedData[i][j-1]*(extractedData[i-1][j]-extractedData[i-1][j-1]))

    return extractedData


# Extracts timestamps and corresponding angular velocities (roll and pitch)
# Returns a list containing 3 more sub lists with timestamps and angular velocities (pitch and roll)
# Lists can be accessed by index: [0]: timestamps, [1] AV roll-axis, [2] AV pitch-axis, [3] A roll-axis, [4] A pitch-axis
def extractDataSwayStar(fileLocation): #Won't work if Excel file is open
    sensorData = xlrd.open_workbook(fileLocation)
    worksheet = sensorData._sheet_list[0]
    extractedData = []
    timeStamp = []
    a_roll = []
    av_roll = []
    a_pitch = []
    av_pitch = []

    for i in range(2, worksheet.nrows): # Iterate over all relevant lines in excel file and extract values.
        timeStamp.append(worksheet.cell_value(i, 0))
        a_roll.append(worksheet.cell_value(i, 1))
        a_pitch.append(worksheet.cell_value(i, 2))
        av_roll.append(worksheet.cell_value(i, 4))
        av_pitch.append(worksheet.cell_value(i, 5))

    extractedData.append(timeStamp)
    extractedData.append(av_roll)
    extractedData.append(av_pitch)
    extractedData.append(a_roll)
    extractedData.append(a_pitch)

    return extractedData


def buildTimestampTable(listOfExtractedDataValedo, axis, destinationDirectory, valType):

    timeStamps = []
    axes = {1: 'x', 2: 'y', 3: 'z', 4: 'x', 5: 'y', 6: 'z'}

    # Check if results folder already exists
    if not os.path.exists(destinationDirectory):
        os.makedirs(destinationDirectory)

    print 'Creating '+axes[axis]+'-axis_'+valType+'.xlsx ...\n'

    # collect every existing timestamp from the valedo data.
    for dataSet in listOfExtractedDataValedo:
        for timeStamp in dataSet[0]:
            if timeStamp not in timeStamps:
                timeStamps.append(timeStamp)
    timeStamps.sort()

    # setup output excel file
    workbook = xlsxwriter.Workbook(destinationDirectory+'/valedo_'+axes[axis]+'-axis_'+valType+'.xlsx')
    worksheet = workbook.add_worksheet()
    cellWidth = 15
    worksheet.set_column('A:A', cellWidth)
    worksheet.set_column('B:B', cellWidth)
    worksheet.set_column('C:C', cellWidth)
    worksheet.set_column('D:D', cellWidth)
    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'Timestamp', bold)
    worksheet.write('B1', 'Value Sensor1', bold)
    worksheet.write('C1', 'Value Sensor2', bold)
    worksheet.write('D1', 'Value Sensor3', bold)

    for i in range(len(timeStamps)): #iterate over every time stamp
        worksheet.write(i+1, 0, timeStamps[i])
        for j in range(0, 3): #iterate over every dataset
            for k in range(len(listOfExtractedDataValedo[j][0])): #iterate over every timestamp in each data set
                if timeStamps[i] == listOfExtractedDataValedo[j][0][k]: #check if current time stamp(from timeStamps) is uncluded. If yes, write value in sheet
                    worksheet.write(i+1, j+1, listOfExtractedDataValedo[j][axis][k])

    workbook.close()

    print axes[axis]+'-axis_'+valType+'.xlsx was created successfully!\n'


def computeRawData(fileSource, fileDestination, unit):
    print 'Computing unfiltered data for all axes ...'
    files = os.listdir(fileSource)
    axisDataFiles = []

    # Extract the desired excel files with the axis data
    for i in range(len(files)):
        if files[i].endswith('.xlsx'):
            axisDataFiles.append(files[i])

    # Extract timestamps and values from one axis (e.g. x-axis) and do calculations
    for i in range(len(axisDataFiles)):
        timeStamps = []
        sensor1 = []
        sensor2 = []
        sensor3 = []

        sensorData = xlrd.open_workbook(fileSource+axisDataFiles[i])
        worksheetIn = sensorData._sheet_list[0]
        numberOfValues = worksheetIn.nrows-1 # subtract the line with sensor names
        for j in range(1, worksheetIn.nrows-(numberOfValues % 5)):
            timeStamps.append(worksheetIn.cell_value(j, 0))
            sensor1.append(worksheetIn.cell_value(j, 1))
            sensor2.append(worksheetIn.cell_value(j, 2))
            sensor3.append(worksheetIn.cell_value(j, 3))

        # Sum all lists for current axis to simplify accessing via index
        currentAxisData = []
        currentAxisData.append(timeStamps)
        currentAxisData.append(sensor1)
        currentAxisData.append(sensor2)
        currentAxisData.append(sensor3)

        # Write timestamps and filtered values into output excel file and compute mean of 3 sensors.
        sensorMeans = []
        timeStampsMeans = []

        for j in range(len(currentAxisData[0])): # iterate over every line of the data and exclude the values untouched by the algorithm
            tempSensorData = []

            for k in range(1, 4): # iterate over all sensors and add value(if no gap), calculate mean and add to list
                if not currentAxisData[k][j] == '': # Exclude gaps for mean calculation
                    tempSensorData.append(currentAxisData[k][j])

            # if tempSensorData isnt an empty list, mean it and write timestamp + value into excel output file and lists.
            if tempSensorData:
                sensorMean = np.mean(tempSensorData)
                timeStampsMeans.append(currentAxisData[0][j]) #Add current timestamp for meaned values to list
                sensorMeans.append(sensorMean)

        # calculate Values for current axis (mean of all 3 sensors)

        valuesOfInterest = calculateValues(timeStampsMeans, sensorMeans, 'mean_'+axisDataFiles[i][:-5]+'_unfiltered', unit, fileDestination, 'unfiltered_')

        # Draw and save Histogram for current axis (mean of all 3 sensors)
        drawHisto(sensorMeans, 'mean_'+axisDataFiles[i][:-5]+'_unfiltered', fileDestination, valuesOfInterest)
        # drawHistoXrange(sensorMeans, axisDataFiles[i][:-5], fileLocation+'timestamp_tables/'+folderName+'/', -0.1, 0.1, valuesOfInterest)


def filterData(fileSource, fileDestination, sampleRange, sdFactor):
    print 'Computing filtered data for all axes ...'
    files = os.listdir(fileSource)
    axisDataFiles = []
    meaned_threes_data = []

    # Check if results folder already exists
    if not os.path.exists(fileDestination):
        os.makedirs(fileDestination)

    # Extract the desired excel files with the axis data
    for i in range(len(files)):
        if files[i].endswith('.xlsx'):
            axisDataFiles.append(files[i])

    # Extract timestamps and values from one axis (e.g. x-axis) and do calculations
    for i in range(len(axisDataFiles)):
        timeStamps = []
        sensor1 = []
        sensor2 = []
        sensor3 = []

        sensorData = xlrd.open_workbook(fileSource+axisDataFiles[i])
        worksheetIn = sensorData._sheet_list[0]
        numberOfValues = worksheetIn.nrows-1 #subtract the line with sensor names
        for j in range(1, worksheetIn.nrows-(numberOfValues % 5)):
            timeStamps.append(worksheetIn.cell_value(j, 0))
            sensor1.append(worksheetIn.cell_value(j, 1))
            sensor2.append(worksheetIn.cell_value(j, 2))
            sensor3.append(worksheetIn.cell_value(j, 3))

        # Sum all lists for current axis to simplify accessing via index
        currentAxisData = []
        currentAxisData.append(timeStamps)
        currentAxisData.append(sensor1)
        currentAxisData.append(sensor2)
        currentAxisData.append(sensor3)

        # loop trough every sensor(1-3)
        for j in range(1, 4):
            # create copy of current list (new gaps will be added to this list).
            tempFilteredList = currentAxisData[j][:]

            # Take the current 10 values for the calculations and afterwards advance 5 samples.
            # note that the samples untouched by the algorithm are cut out of the analysis.
            for k in range(0, len(currentAxisData[j])-5, 5):
                tempValueList = []
                for m in range(sampleRange):
                    # extract the current Values (without gaps). --> used for calculation of mean/sd
                    if not currentAxisData[j][k+m] == '':
                        tempValueList.append(currentAxisData[j][k+m])

                tempMean = np.mean(tempValueList)
                tempSd = np.std(tempValueList)

                # check criteria for every value in the filtered list and replace with gap if out of range.
                for m in range(sampleRange):
                    # before comparing to mean and sd, make sure it is a float
                    if not tempFilteredList[k+m] == '':
                        if tempFilteredList[k+m] > (tempMean+sdFactor*tempSd) or tempFilteredList[k+m] < (tempMean-sdFactor*tempSd):
                            tempFilteredList[k+m] = ''

            # set the corrected (filtered list) with added gaps
            currentAxisData[j] = tempFilteredList

        # Setup the excel output file for the filtered data of a specific axis for all 3 sensors.
        workbook = xlsxwriter.Workbook(fileDestination+'/filtered_'+axisDataFiles[i])
        worksheetOut = workbook.add_worksheet()
        cellWidth = 15
        worksheetOut.set_column('A:A', cellWidth)
        worksheetOut.set_column('B:B', cellWidth)
        worksheetOut.set_column('C:C', cellWidth)
        worksheetOut.set_column('D:D', cellWidth)
        worksheetOut.set_column('E:E', cellWidth)
        worksheetOut.set_column('G:G', cellWidth)
        worksheetOut.set_column('F:F', cellWidth-12)
        worksheetOut.set_column('H:H', cellWidth)
        worksheetOut.set_column('I:I', cellWidth)
        bold = workbook.add_format({'bold': True})
        worksheetOut.write('A1', 'Timestamp', bold)
        worksheetOut.write('B1', 'Value Sensor1', bold)
        worksheetOut.write('C1', 'Value Sensor2', bold)
        worksheetOut.write('D1', 'Value Sensor3', bold)
        worksheetOut.write('E1', 'Mean Sensors', bold)
        worksheetOut.write('H1', 'Mean:', bold)
        worksheetOut.write('I1', 'Sd:', bold)

        # Write timestamps and filtered values into output excel file and compute mean of 3 sensors.
        sensorMeans = []
        timeStampsMeans = []

        # iterate over every line of the data and exclude the values untouched by the algorithm
        for j in range(len(currentAxisData[0])):
            tempSensorData = []
            worksheetOut.write(j+1, 0, currentAxisData[0][j]) # Write timestamp into output excel file

            for k in range(1, 4): # iterate over all sensors and add value(if no gap), calculate mean and add to list
                if not currentAxisData[k][j] == '': # Exclude gaps for mean calculation
                    tempSensorData.append(currentAxisData[k][j])
                worksheetOut.write(j+1, k, currentAxisData[k][j])

            # if tempSensorData isnt an empty list,
            # mean it and write timestamp + value into excel output file and lists.
            if tempSensorData:
                sensorMean = np.mean(tempSensorData)
                timeStampsMeans.append(currentAxisData[0][j]) # Add current timestamp for meaned values to list
                sensorMeans.append(sensorMean)
                worksheetOut.write(j+1, 4, sensorMean)
            else:
                worksheetOut.write(j+1, 4, '')

        # Computes mean and sd for a specific axis for each sensor over time:
        for j in range(1, 4):
            valuesWithoutGaps = []
            for k in range(len(currentAxisData[j])): # Exclude the values untouched by the algorithm
                if not currentAxisData[j][k] == '': # Exclude gaps for mean and sd calculations
                    valuesWithoutGaps.append(currentAxisData[j][k])

            worksheetOut.write(j, len(currentAxisData)+2, 'Sensor '+str(j), bold)
            worksheetOut.write(j, len(currentAxisData)+3, np.mean(valuesWithoutGaps))
            worksheetOut.write(j, len(currentAxisData)+4, np.std(valuesWithoutGaps))

        # Computes mean and sd for averaged Values
        worksheetOut.write(len(currentAxisData), len(currentAxisData)+2, 'Averaged Values:', bold)
        worksheetOut.write(len(currentAxisData), len(currentAxisData)+3, np.mean(sensorMeans))
        worksheetOut.write(len(currentAxisData), len(currentAxisData)+4, np.std(sensorMeans))

        # calculate Values for current axis (mean of all 3 sensors)
        valuesOfInterest = calculateValues(timeStampsMeans, sensorMeans, 'mean_'+axisDataFiles[i][:-5]+'_filtered', 'deg/s', fileDestination, 'filtered_')

        # Draw and save Histogram for current axis (mean of all 3 sensors)
        drawHisto(sensorMeans, 'mean_'+axisDataFiles[i][:-5]+'_filtered', fileDestination, valuesOfInterest)
        # drawHistoXrange(sensorMeans, axisDataFiles[i][:-5], fileLocation+'timestamp_tables/'+folderName+'/', -0.1, 0.1, valuesOfInterest)


        # #Apply three-filter onto already filtered data to smoothen it
        # # New sample(t)= 0.25 * orig sample t-1 + 0.5 * orig sample t + 0.25 * orig sample t+1
        # sensorMeansThrees = []
        #
        # for j in range(1, len(sensorMeans)-1):
        #     sensorMeansThrees.append(0.25*sensorMeans[j-1]+0.5*sensorMeans[j]+0.25*sensorMeans[j+1])
        #
        # #Cut the first and last timeStamp out, because the corresponding value is not touched by the alogrithm
        # del timeStampsMeans[0]
        # del timeStampsMeans[-1]


        # Save meaned_threes_data for every axis into a list and return it
        # Add the currentAxisSet with the meaned_threes_data(timestamps, values) for each axis to "meaned_threes_data".
        currentAxisSet = []
        currentAxisSet.append(timeStampsMeans[:])
        currentAxisSet.append(sensorMeans)
        # currentAxisSet.append(sensorMeansThrees[:])
        meaned_threes_data.append(currentAxisSet)

        # calculate Values for current axis (mean of all 3 sensors)
        # valuesOfInterest = calculateValues(timeStampsMeans, sensorMeansThrees, 'mean_threes_'+axisDataFiles[i][:-5]+'_filtered', 'deg/s', fileDestination, 'filtered_')
        valuesOfInterest = calculateValues(timeStampsMeans, sensorMeans, axisDataFiles[i][:-5]+'_filtered', 'deg/s', fileDestination, 'filtered_')

        # Draw and save Histogram for current axis (mean of all 3 sensors)
        # drawHisto(sensorMeansThrees, 'mean_threes_'+axisDataFiles[i][:-5]+'_filtered', fileDestination, valuesOfInterest)
        drawHisto(sensorMeans, axisDataFiles[i][:-5]+'_filtered', fileDestination, valuesOfInterest)
        # drawHistoXrange(sensorMeans, axisDataFiles[i][:-5], fileLocation+'timestamp_tables/'+folderName+'/', -0.1, 0.1, valuesOfInterest)

        workbook.close()

    print 'done!'

    return meaned_threes_data


def filterDataThrees(fileSource, fileDestination, sampleRange, sdFactor):
    print 'Computing filtered data for all axes ...'
    files = os.listdir(fileSource)
    axisDataFiles = []
    meaned_threes_data = []

    # Check if results folder already exists
    if not os.path.exists(fileDestination):
        os.makedirs(fileDestination)

    # Extract the desired excel files with the axis data
    for i in range(len(files)):
        if files[i].endswith('.xlsx'):
            axisDataFiles.append(files[i])

    # Extract timestamps and values from one axis (e.g. x-axis) and do calculations
    for i in range(len(axisDataFiles)):
        timeStamps = []
        sensor1 = []
        sensor2 = []
        sensor3 = []

        sensorData = xlrd.open_workbook(fileSource+axisDataFiles[i])
        worksheetIn = sensorData._sheet_list[0]
        numberOfValues = worksheetIn.nrows-1 #subtract the line with sensor names
        for j in range(1, worksheetIn.nrows-(numberOfValues % 5)):
            timeStamps.append(worksheetIn.cell_value(j, 0))
            sensor1.append(worksheetIn.cell_value(j, 1))
            sensor2.append(worksheetIn.cell_value(j, 2))
            sensor3.append(worksheetIn.cell_value(j, 3))

        # Sum all lists for current axis to simplify accessing via index
        currentAxisData = []
        currentAxisData.append(timeStamps)
        currentAxisData.append(sensor1)
        currentAxisData.append(sensor2)
        currentAxisData.append(sensor3)

        for j in range(1, 4): # loop trough every sensor(1-3)
            tempFilteredList = currentAxisData[j][:] # create copy of current list (new gaps will be added to this list).

            for k in range(0, len(currentAxisData[j])-5, 5): # take current 10 values for the algorithm and afterwards move forward 5 "steps". Note that the untouched values are cut out of the analysis
                tempValueList = []
                for m in range(sampleRange):
                    if not currentAxisData[j][k+m] == '': # Extract the current Values (without gaps). --> used for calculation of mean/sd
                        tempValueList.append(currentAxisData[j][k+m])

                tempMean = np.mean(tempValueList)
                tempSd = np.std(tempValueList)

                # check criteria for every value in the filtered list and replace with gap if out of range.
                for m in range(sampleRange):
                    if not tempFilteredList[k+m] == '': # before comparing to mean and sd, make sure it is a float
                        if tempFilteredList[k+m] > (tempMean+sdFactor*tempSd) or tempFilteredList[k+m] < (tempMean-sdFactor*tempSd):
                            tempFilteredList[k+m] = ''

            currentAxisData[j] = tempFilteredList #set the corrected (filtered list) with added gaps

        # Setup the excel output file for the filtered data of a specific axis for all 3 sensors.
        workbook = xlsxwriter.Workbook(fileDestination+'/filtered_'+axisDataFiles[i])
        worksheetOut = workbook.add_worksheet()
        cellWidth = 15
        worksheetOut.set_column('A:A', cellWidth)
        worksheetOut.set_column('B:B', cellWidth)
        worksheetOut.set_column('C:C', cellWidth)
        worksheetOut.set_column('D:D', cellWidth)
        worksheetOut.set_column('E:E', cellWidth)
        worksheetOut.set_column('G:G', cellWidth)
        worksheetOut.set_column('F:F', cellWidth-12)
        worksheetOut.set_column('H:H', cellWidth)
        worksheetOut.set_column('I:I', cellWidth)
        bold = workbook.add_format({'bold': True})
        worksheetOut.write('A1', 'Timestamp', bold)
        worksheetOut.write('B1', 'Value Sensor1', bold)
        worksheetOut.write('C1', 'Value Sensor2', bold)
        worksheetOut.write('D1', 'Value Sensor3', bold)
        worksheetOut.write('E1', 'Mean Sensors', bold)
        worksheetOut.write('H1', 'Mean:', bold)
        worksheetOut.write('I1', 'Sd:', bold)

        # Write timestamps and filtered values into output excel file and compute mean of 3 sensors.
        sensorMeans = []
        timeStampsMeans = []

        # iterate over every line of the data and exclude the values untouched by the algorithm
        for j in range(len(currentAxisData[0])):
            tempSensorData = []
            worksheetOut.write(j+1, 0, currentAxisData[0][j]) # Write timestamp into output excel file

            for k in range(1, 4): # iterate over all sensors and add value(if no gap), calculate mean and add to list
                if not currentAxisData[k][j] == '': # Exclude gaps for mean calculation
                    tempSensorData.append(currentAxisData[k][j])
                worksheetOut.write(j+1, k, currentAxisData[k][j])

            # if tempSensorData isnt an empty list,
            # mean it and write timestamp + value into excel output file and lists.
            if tempSensorData:
                sensorMean = np.mean(tempSensorData)
                timeStampsMeans.append(currentAxisData[0][j]) # Add current timestamp for meaned values to list
                sensorMeans.append(sensorMean)
                worksheetOut.write(j+1, 4, sensorMean)
            else:
                worksheetOut.write(j+1, 4, '')

        # Computes mean and sd for a specific axis for each sensor over time:
        for j in range(1, 4):
            valuesWithoutGaps = []
            for k in range(len(currentAxisData[j])): # Exclude the values untouched by the algorithm
                if not currentAxisData[j][k] == '': # Exclude gaps for mean and sd calculations
                    valuesWithoutGaps.append(currentAxisData[j][k])

            worksheetOut.write(j, len(currentAxisData)+2, 'Sensor '+str(j), bold)
            worksheetOut.write(j, len(currentAxisData)+3, np.mean(valuesWithoutGaps))
            worksheetOut.write(j, len(currentAxisData)+4, np.std(valuesWithoutGaps))

        # Computes mean and sd for averaged Values
        worksheetOut.write(len(currentAxisData), len(currentAxisData)+2, 'Averaged Values:', bold)
        worksheetOut.write(len(currentAxisData), len(currentAxisData)+3, np.mean(sensorMeans))
        worksheetOut.write(len(currentAxisData), len(currentAxisData)+4, np.std(sensorMeans))

        # calculate Values for current axis (mean of all 3 sensors)
        valuesOfInterest = calculateValues(timeStampsMeans, sensorMeans, 'mean_'+axisDataFiles[i][:-5]+'_filtered', 'deg/s', fileDestination, 'filtered_')

        # Draw and save Histogram for current axis (mean of all 3 sensors)
        drawHisto(sensorMeans, 'mean_'+axisDataFiles[i][:-5]+'_filtered', fileDestination, valuesOfInterest)
        # drawHistoXrange(sensorMeans, axisDataFiles[i][:-5], fileLocation+'timestamp_tables/'+folderName+'/', -0.1, 0.1, valuesOfInterest)


        # Apply smoothing filter over 3 samples to data filtered with moving band filter over 10 samples
        # New sample(t)= 0.25 * orig sample t-1 + 0.5 * orig sample t + 0.25 * orig sample t+1
        sensorMeansThrees = []

        # Iterate over the original samples
        for j in range(1, len(sensorMeans)-1):
            # Calculate new sample and add it to a list
            sensorMeansThrees.append(0.25*sensorMeans[j-1]+0.5*sensorMeans[j]+0.25*sensorMeans[j+1])

        # Cut the first and last timeStamp out, because the corresponding values are not touched by the alogrithm
        del timeStampsMeans[0]
        del timeStampsMeans[-1]


        # Save meaned_threes_data for every axis into a list and return it
        # Add the currentAxisSet with the meaned_threes_data(timestamps, values) for each axis to "meaned_threes_data".
        currentAxisSet = []
        currentAxisSet.append(timeStampsMeans[:])
        currentAxisSet.append(sensorMeansThrees[:])
        meaned_threes_data.append(currentAxisSet)

        # calculate Values for current axis (mean of all 3 sensors)
        valuesOfInterest = calculateValues(timeStampsMeans, sensorMeansThrees, 'mean_threes_'+axisDataFiles[i][:-5]+'_filtered', 'deg/s', fileDestination, 'filtered_')


        # Draw and save Histogram for current axis (mean of all 3 sensors)
        drawHisto(sensorMeansThrees, 'mean_threes_'+axisDataFiles[i][:-5]+'_filtered', fileDestination, valuesOfInterest)
        # drawHistoXrange(sensorMeans, axisDataFiles[i][:-5], fileLocation+'timestamp_tables/'+folderName+'/', -0.1, 0.1, valuesOfInterest)

        workbook.close()

    print 'done!'

    return meaned_threes_data


#Function used for shifting the valedo datasets (single unfiltered and meaned filtered) for final figures.
def shiftY(upShiftList, downShiftList, shift):

    for i in range(len(upShiftList)):
        upShiftList[i] += shift

    for i in range(len(downShiftList)):
        downShiftList[i] -= shift

