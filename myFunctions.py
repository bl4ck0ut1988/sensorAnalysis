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

def calculateValues(timeStamps, values, axisName, baseDirectory, timeUnit):

    fit = polyfit(timeStamps, values, 1)
    #plot data
    x = np.array(range(int(np.min(timeStamps)), int(np.max(timeStamps))))
    y = eval(str(fit[0])+"*x+"+str(fit[1]))
    #plt.axis([int(np.min(timeStamps)), int(np.max(timeStamps)), int(np.min(values)), int(np.max(values))])
    plt.title(axisName)
    plt.xlabel(timeUnit)
    plt.ylabel('deg/s')
    plt.plot(x, y)
    plt.plot(timeStamps, values)
    plt.savefig(baseDirectory+'results/'+axisName+'.png')
    plt.clf()
    #plt.show()

    fit_fn = poly1d(fit) # fit_fn is now a function which takes in x and returns an estimate for y
    #calculate sd


    #Calculate rms
    sumSqr = 0
    for i in range(len(timeStamps)):
        xValue = values[i] - fit_fn(timeStamps[i])
        sumSqr += math.pow(xValue, 2)
    rms = math.sqrt((sumSqr/len(values)))

    #set and print the values below
    min = "Min: "+str(np.min(values))
    max = "Max: "+str(np.max(values))
    mean = "Mean: "+str(np.mean(values))
    ptp = "Peak to peak range: "+str(np.max(values)-np.min(values))
    sd = "Standard Deviation: "+str(np.std(values))
    rms = "Noise (rms): "+str(rms)
    print values
    print min+'\n', max+'\n', mean+'\n', ptp+'\n', rms+'\n'

    #open and write into output file:
    outputFile = open(baseDirectory+'results/output_data.txt', 'a')
    outputFile.write(axisName+"\n")
    outputFile.write(min+'\n')
    outputFile.write(max+'\n')
    outputFile.write(mean+'\n')
    outputFile.write(ptp+'\n')
    #outputFile.write("Linear Reg. Function: "+str(fit_fn)+'\n')
    outputFile.write(sd+'\n')
    outputFile.write(rms+'\n\n')
    outputFile.close()
    return rms


def drawHisto(listOfValues, axisName, saveDirectory): #Creates histogram with 40 bins using the ptp range of the data

    plt.title(axisName)
    plt.hist(listOfValues, bins=40)
    plt.savefig(saveDirectory+axisName+'_histo.png')
    plt.clf()

def drawHistoXrange(listOfValues, axisName, saveDirectory, x_min, x_max): #Creates histogram with 40 bins using the ptp range of the data

    plt.title(axisName)
    plt.xlim(x_min, x_max)
    plt.hist(listOfValues, bins=40)
    plt.savefig(saveDirectory+axisName+'_histo.png')
    plt.clf()


#Returns a list, containing 4 more lists with timestamps and angular Velocities (x,y,z)
#Lists can be accessed by index: [0]: timestamps, [1] AV x-axis, [2] AV y-axis, [3] AV z-axis,
def extractDataTxt(fileLocation):
    sensorData = open(fileLocation)
    extractedData = []
    timeStamp = []
    avx = []
    avy = []
    avz = []

    #read trough every line of .txt file and extract timestamp + x,y,z Angular Velocities
    for line in sensorData.readlines():
        if not line.startswith("Sensor"):
            splittedLine = line.split(",")
            timeStamp.append(float(splittedLine[1]))
            avx.append(float(splittedLine[14]))
            avy.append(float(splittedLine[15]))
            avz.append(float(splittedLine[16][:-2]))

    extractedData.append(timeStamp)
    extractedData.append(avx)
    extractedData.append(avy)
    extractedData.append(avz)

    return extractedData


def extractDataExcel(fileLocation): #Won't work if Excel file is open
    sensorData = xlrd.open_workbook(fileLocation)
    worksheet = sensorData._sheet_list[0]
    extractedData = []
    timeStamp = []
    av_roll = []
    av_pitch = []

    for i in range(2, worksheet.nrows): #Iterate over all relevant lines in excel file and extract values.
        timeStamp.append(worksheet.cell_value(i, 3))
        av_roll.append(worksheet.cell_value(i, 4))
        av_pitch.append(worksheet.cell_value(i, 5))

    extractedData.append(timeStamp)
    extractedData.append(av_roll)
    extractedData.append(av_pitch)

    return extractedData


def buildTimestampTable(listOfExtractedDataValedo, axis, baseDirectory):

    timeStamps = []
    axes = {1: 'x', 2: 'y', 3: 'z'}

    #Check if results folder already exists
    folderName = 'timestamp_tables'
    if not os.path.exists(baseDirectory+folderName):
        os.makedirs(baseDirectory+folderName)

    print 'Creating '+axes[axis]+'-axis.xlsx ...\n'

    #collect every existing timestamp from the valedo data.
    for dataSet in listOfExtractedDataValedo:
        for timeStamp in dataSet[0]:
            if timeStamp not in timeStamps:
                timeStamps.append(timeStamp)
    timeStamps.sort()

    #setup excel file
    workbook = xlsxwriter.Workbook(baseDirectory+folderName+'/'+axes[axis]+'-axis.xlsx')
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

    print axes[axis]+'-axis.xlsx was created successfully!\n'


def filterData(fileLocation):
    print 'Computing filtered data for all axes ...'
    files = os.listdir(fileLocation+'timestamp_tables')
    axisDataFiles = []

    #create folder for output excel file (filtered)
    folderName = 'filtered'
    if not os.path.exists(fileLocation+'timestamp_tables/'+folderName):
        os.makedirs(fileLocation+'timestamp_tables/'+folderName)

    #Extract the desired excel files with the axis data
    for i in range(len(files)):
        if files[i].endswith('.xlsx'):
            axisDataFiles.append(files[i])

    #Extract timestamps and values from one axis (e.g. x-axis) and do calculations
    for i in range(len(axisDataFiles)):
        timeStamps = []
        sensor1 = []
        sensor2 = []
        sensor3 = []

        sensorData = xlrd.open_workbook(fileLocation+'timestamp_tables/'+axisDataFiles[i])
        worksheetIn = sensorData._sheet_list[0]
        numberOfValues = worksheetIn.nrows-1 #subtract the line with sensor names
        for j in range(1, worksheetIn.nrows-(numberOfValues % 5)):
            timeStamps.append(worksheetIn.cell_value(j, 0))
            sensor1.append(worksheetIn.cell_value(j, 1))
            sensor2.append(worksheetIn.cell_value(j, 2))
            sensor3.append(worksheetIn.cell_value(j, 3))

        #Sum all lists for current axis to simplify accessing via index
        currentAxisData = []
        currentAxisData.append(timeStamps)
        currentAxisData.append(sensor1)
        currentAxisData.append(sensor2)
        currentAxisData.append(sensor3)

        for j in range(1, 4): #loop trough every sensor(1-3)
            tempFilteredList = currentAxisData[j][:] #create copy of current list (new gaps will be added to this list).
            print 'Len of current list: '+str(len(currentAxisData[j]))
            for k in range(0, len(currentAxisData[j])-5, 5): #take current 10 values for the algorithm and afterwards move forward 5 "steps". Note that the untouched values are cut out of the analysis
                tempValueList = []
                #print str(k)+' - '+str(k+10)+': '
                for m in range(10):
                    if not currentAxisData[j][k+m] == '': #Extract the current Values (without gaps). --> used for calculation of mean/sd
                        tempValueList.append(currentAxisData[j][k+m])

                #print tempValueList

                tempMean = np.mean(tempValueList)
                tempSd = np.std(tempValueList)

                #check criteria for every value in the filtered list and replace with gap if out of range.
                for m in range(10):
                    if not tempFilteredList[k+m] == '': #before comparing to mean and sd, make sure it is a float
                        if tempFilteredList[k+m] > (tempMean+1.75*tempSd) or tempFilteredList[k+m] < (tempMean-1.75*tempSd):
                            tempFilteredList[k+m] = ''

                # print 'Mean: '+str(np.mean(tempValueList))
                # print 'sd: '+str(np.std(tempValueList))
                # print 'End:'+str(k+10)+'--------------------------'

            currentAxisData[j] = tempFilteredList #set the corrected (filtered list) with added gaps

        #Setup the excel output file for the filtered data of a specific axis for all 3 sensors.
        workbook = xlsxwriter.Workbook(fileLocation+'timestamp_tables/'+folderName+'/filtered_'+axisDataFiles[i])
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

        sensorMeans = []

        #Write timestamps and filtered values into output excel file and compute mean of 3 sensors.
        for j in range(len(currentAxisData[0])): #iterate over every line of the data and exclude the values untouched by the algorithm
            tempSensorData = []
            worksheetOut.write(j+1, 0, currentAxisData[0][j]) # Write timestamp into output excel file

            for k in range(1, 4): #iterate over all sensor and add value(if no gap), calculate mean and add to list
                if not currentAxisData[k][j] == '': #Exclude gaps for mean calculation
                    tempSensorData.append(currentAxisData[k][j])
                worksheetOut.write(j+1, k, currentAxisData[k][j])

            #if tempSensorData isnt an empty list, mean it and write value into excel output file.
            if tempSensorData:
                sensorMean = np.mean(tempSensorData)
                sensorMeans.append(sensorMean)
                worksheetOut.write(j+1, 4, sensorMean)
            else:
                worksheetOut.write(j+1, 4, '')

        #Computes mean and sd for a specific axis for each sensor over time:
        for j in range(1, 4):
            valuesWithoutGaps = []
            for k in range(len(currentAxisData[j])): #Exclude the values untouched by the algorithm
                if not currentAxisData[j][k] == '': #Exclude gaps for mean and sd calculations
                    valuesWithoutGaps.append(currentAxisData[j][k])

            worksheetOut.write(j, len(currentAxisData)+2, 'Sensor '+str(j), bold)
            worksheetOut.write(j, len(currentAxisData)+3, np.mean(valuesWithoutGaps))
            worksheetOut.write(j, len(currentAxisData)+4, np.std(valuesWithoutGaps))

        #Computes mean and sd for averaged Values
        worksheetOut.write(len(currentAxisData), len(currentAxisData)+2, 'Averaged Values:', bold)
        worksheetOut.write(len(currentAxisData), len(currentAxisData)+3, np.mean(sensorMeans))
        worksheetOut.write(len(currentAxisData), len(currentAxisData)+4, np.std(sensorMeans))

        #Draw and save Histogram (x-range: -0.1 - 0.1)
        drawHisto(sensorMeans, axisDataFiles[i][:-5], fileLocation+'timestamp_tables/'+folderName+'/')
        #drawHistoXrange(sensorMeans, axisDataFiles[i][:-5], fileLocation+'timestamp_tables/'+folderName+'/', -0.1, 0.1)

        workbook.close()

    print 'done !'