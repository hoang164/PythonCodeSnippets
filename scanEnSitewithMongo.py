# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 13:37:06 2018
This will go through the dataSummary_new.csv file to organize the data into MongoDb

Data can be visualize in MongoDB Compass when connect to host=10.3.143.106:27017
dataSummary_new.csv is created using DWS_extract.py

@author: HoangT04
"""
#copy from scanEnSiteStudies.py 
from datetime import date
from pymongo import MongoClient
import sqlite3
from dataWithMongo import *
from mongoengine import *
import pandas as pd
import json
from bson import ObjectId


#Making a connection to Eric's MongoDB:
#connect(db='ensite', host='10.3.143.106:27017')
connect(db='ensite',host='mongodb://10.3.143.106:27017')
#right now it's putting everything into a 'study' collection under the 'test' database. Don't know why.
#register_connection('thuydb',name='ensite',db='ensite',host='mongodb://10.3.143.106:27017')
#Get data from the csv:
csvData= pd.read_csv('dataSummary_new.csv')
#this should have been data coming directly from the source, but didn't have time to do that

def convertToInt(value): 
    try: 
        temp= int(value)
        if type(temp)== type(1): return temp
        else: return 0
    except:
        return 0 #it's most likely a nan type 

def convertToBoolian(value):
    if type(value)== type(True):
        return value
    else: return False
    
for row in range(0, len(csvData)):
    try:
it        print(csvData.loc[row,'studyID'])
        study= Study(csvData.loc[row,'studyID'],
        year= str(csvData.loc[row,'year']),
        beginTime= str(csvData.loc[row,'beginTime']),
        endTime= str(csvData.loc[row,'endTime']),
        duration= str(csvData.loc[row,'duration']),
        dws_version= csvData.loc[row,'dws_version'], #from database Folder
        system= csvData.loc[row,'system'],
        studyType= csvData.loc[row,'studyType'],
        physicians= csvData.loc[row,'physicians'])
        
        print(dict(study.to_mongo()))
        #segments
        allSegmentsNames= str(csvData.loc[row,'SegmentNames'])
        if not allSegmentsNames: print('NoSegments')
        for i in allSegmentsNames.split(';')[:-1]:
            s1= Segment(name= i)
            s1.addSegmentInfo(SegmentInfo(seg_type='AUTO')) 
            study.addSegment(s1)
            study.save()
        
        #catheters
        cathNames= str(csvData.loc[row,'CatheterName']).split(';')[:-1]
        cathID= str(csvData.loc[row,'CatheterID']).split(';')[:-1]
        print(cathID)
        print(cathNames)
        cathBrands= str(csvData.loc[row,'CatheterBrands']).split(';')[:-1]
        cathManu= str(csvData.loc[row,'CatheterManufacturers']).split(';')[:-1]
        cathTypes= str(csvData.loc[row,'CatheterTypes']).split(';')[:-1]
        cathModels= str(csvData.loc[row,'CatheterModel']).split(';')[:-1]
        cathPolarity= str(csvData.loc[row,'Polarity']).split(';')[:-1]
        for i in range(len(cathNames)-1):
            c= Catheter(ID= cathID[i], name= cathNames[i] )
            c.addCathInfo(CathInfo(brand=cathBrands[i],manufacturer=cathManu[i]))
            study.addCath(c)
            study.save()
        
        #study.ablations= Ablation(start_time= str(csvData.loc[row,'AblationStartTime']),
#                                  end_time= str(csvData.loc[row,'AblationEndTime']),
#                                  duration= str(csvData.loc[row,'AblationDuration']),
#                                  total_time= str(csvData.loc[row,'TotalAblationTime']),
#                                  total_number= str(csvData.loc[row,'TotalNumberOfAblation']),
#                                  catheter_SN= str(csvData.loc[row,'AblationCatheterSN']))
 
        study.geometry= Geometry(   compensated= csvData.loc[row,'CompensatedGeo'],
                                    magnetic= csvData.loc[row,'MagneticGeo'],
                                    mediGuide= csvData.loc[row,'MediGuideGeo'],
                                    project_on_DIF= csvData.loc[row,'ProjOnDif'],
                                    navX_project_dist= convertToInt(csvData.loc[row,'MaxProjDist']),
                                    upper_gating_threshold= convertToInt(csvData.loc[row,'UpperGatingThres']),
                                    lower_gating_threshold= convertToInt(csvData.loc[row,'LowerGatingThres']),
                                    gate_geo_points= convertToInt(csvData.loc[row,'GateGeoPoints']),
                                    gate_fiducials= csvData.loc[row,'GateFiducials'],
                                    magnetic_to_NavX_count= convertToInt(csvData.loc[row,'MagneticToNavexCount']),
                                    edit_surfaces_count= convertToInt(csvData.loc[row,'EditSurfacesCount']),
                                    dif_registration= csvData.loc[row,'DifRegistration'],
                                    dif_surface= convertToInt(csvData.loc[row,'DifSurfaceSets']))
        study.save()
        
        patientGender= csvData.loc[row,'patient_gender']
        if patientGender.lower()=='female': patientGender='FEMALE'
        elif patientGender.lower()=='male':patientGender='MALE'
        else: patientGender='NOT_SPECIFIED'
        study.patient= Patient(gender= patientGender,
                        diagnosis= csvData.loc[row,'diagnosis'])
        study.save()
        
        study.events= Events(total_number= csvData.loc[row,'numEvents'],
                        description= [csvData.loc[row,'eventsDescription']])
        study.save()
        
        study.filters= Filter(  powerline_50Hz= convertToBoolian(csvData.loc[row,'Powerline50Hz']),#from settings folder
                                mea_HP= convertToInt(csvData.loc[row,'FilterMea_HP']),
                                mea_LP= convertToInt(csvData.loc[row,'FilterMea_LP']),
                                ECG_HP= convertToInt(csvData.loc[row,'FilterECG_HP']),
                                ECG_LP= convertToInt(csvData.loc[row,'FilterECG_LP']),
                                EPCathBio_HP= convertToInt(csvData.loc[row,'FilterEPCathBio_HP']),
                                EPCathBio_LP=convertToInt(csvData.loc[row,'FilterEPCathBio_LP']),
                                bipol_HP= convertToInt(csvData.loc[row,'FilterBipol_HP']),
                                bipol_LP= convertToInt(csvData.loc[row,'FilterBipol_PL']), #typo from the csv
                                analog_HP= convertToInt(csvData.loc[row,'FilterAnalog_HP']),
                                analog_LP= convertToInt(csvData.loc[row,'FilterAnalog_LP']))
        study.save()
        
        #maps
        mapNames= str(csvData.loc[row,'MapNames']).split(';')[:-1]
        if not mapNames: print('No Maps Found')
        for i in mapNames:
            print('i', i, type(i))
            m= Maps(name= i)
            if 'vt' or 'voltage' in i.lower():
                maptype= 'voltage'
            elif 'lat' in i.lower():
                maptype= 'lat'
            elif 'tachy' in i.lower():
                maptype= 'tachy'
            else:
                maptype='unknown'
            print('maptype:', maptype)
            m.addMapsInfo(MapsInfo(map_type= 'unknown'))
            print('MapsInfo added')
            study.addMap(m)
            print('saved map')
            study.save()
            print('map saved to study')
            
        study.save()
        print(dict(study.to_mongo()))
        
    except Exception as e:
        print(e)
        print(csvData.loc[row,'studyID'], 'ERROR: pass')


    
    