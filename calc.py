__author__ = 'Kevin_Mattmueller'


import myFunctions as mf
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import os

directoryName = raw_input("Enter name of Directory: ")
#basedir = "C:/users/kevin/desktop/"+directoryName+"/"
basedir = "C:/users/bl4ck0ut88/desktop/"+directoryName+"/"
files = os.listdir(basedir)

#Check if results folder already exists
if not os.path.exists(basedir+'results'):
    os.makedirs(basedir+'results')

#create output data file
open(basedir+'results/output_data.txt', 'w')

listValedo = []
listSway = []
listExtractedValedoData = []

#Seperate files by file type
for i in range(len(files)):
    if files[i].endswith('.txt'):
        listValedo.append(files[i])
    elif files[i].endswith('.xlsx'):
        listSway.append(files[i])

#create a list with the data from all 3 valedo sensors
for i in range(len(listValedo)):
    extractedData = mf.extractDataTxt(basedir+'/'+listValedo[i])
    listExtractedValedoData.append(extractedData)

#create a time stamp table for each axis of the 3 valedo sensors
for i in range(1, 4):
    mf.buildTimestampTable(listExtractedValedoData, i, basedir)

mf.filterData(basedir)

#Process Valedo data
for i in range(len(listValedo)):
    print '\n----------------------------------------\nData from: Valedo '+listValedo[i][-11:-4]

    #Calculate values of interest for every axis
    axisName = ['x-axis', 'y-axis', 'z-axis']

    for j in range(1, 4):
        print '\n'+axisName[j-1]+':'
        rms = mf.calculateValues(extractedData[0], extractedData[j], listValedo[i][-11:-4]+'_'+axisName[j-1], basedir, 'ms')

        #Histogram
        mf.drawHisto(extractedData[j], listValedo[i][-11:-4]+'_'+axisName[j-1], basedir+'results/')


#Process SwayStar data
for i in range(len(listSway)):
    print '\n----------------------------------------\nData from SwayStar:'
    extractedData = mf.extractDataExcel(basedir+'/'+listSway[i])

    #Calculate values of interest for every axis
    axisName = ['roll-axis', 'pitch-axis']
    for j in range(1, 3):
        print '\n'+axisName[j-1]+':'
        rms = mf.calculateValues(extractedData[0], extractedData[j], 'SwayStar_'+axisName[j-1], basedir, 's')

        #Histogram
        mf.drawHisto(extractedData[j], 'SwayStar_'+axisName[j-1], basedir+'results/')
        #mf.drawHistoXrange(extractedData[j], 'SwayStar_'+axisName[j-1], basedir+'results/', -0.1, 0.1)