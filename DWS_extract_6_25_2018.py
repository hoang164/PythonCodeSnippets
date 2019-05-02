# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 14:01:42 2018

This will go through the database on the HD  and look at at db files for study information
@author: HoangT04
"""

import sqlite3
import pandas as pd
import os
import time
import datetime
import numpy as np                                                
import csv
from lxml import etree as ET
import sys
                                                                                                                                                              
def searchDB(BaseDir= "/var/STJ/Clinical/systemStudy"):
    t0= time.time()
    #BaseDir= "/var/STJ/Clinical/systemStudy"
    col=['studyID','directory','year','beginTime','endTime','duration','dws_version','system','studyTypes', 'physicians','patient_gender','diagnosis','numEvents','eventsDescription','numImages','numSegment','numAutoSegment']
    outdf= pd.DataFrame(columns=col) 
    row=-1
    for root,dirs, files in os.walk(BaseDir):   
        if not "dws.db" in files: continue #go find dws.db files        
        row=row+1
        #get the studyID:
        a= root.split('/')
        for i in a:
            if i.startswith('study_'): #ex: study_artvrp21002_2017_02_13_12_05_48
                studyID= i
                splitdash= i.split('_')
                for b in splitdash: 
                    if b.startswith('201'): year= b                
            if i.startswith('201'): year= i.split('_')[0]    
        dws= os.path.join(root,'dws.db')    
        print(root)

        try: #don't have permission to open some files, it will skip those files
            con= sqlite3.connect(dws) #connect dws.db to SQLite database
            cursor = con.cursor() #create cursor object 
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") 
        except: continue

        outdf.loc[row,'studyID']=studyID
        outdf.loc[row,'directory']= root
        outdf.loc[row,'year']=year   

        #DWS.db contains tables with names:

        tableNames=['studyTypes','studies', 'physicians','patients','Segment', 'AutoSegment','Image','events','catheters','diagnosis']
        #open each table to process:

        for tabName in tableNames: #for each table
            try:
                table= pd.read_sql_query("SELECT * from {}".format(tabName), con)
            except:
                continue
            if tabName== 'studyTypes':
                valueList=[]
                for i in table['value']: valueList= valueList+[i+',']
                outdf.loc[row,'studyTypes']=  ''.join(valueList)
            if tabName== 'studies': 
                outdf.loc[row,'system']= table['system_name'][0]
                outdf.loc[row,'dws_version']=table['dws_version'][0]
            if tabName=='physicians':
                outdf.loc[row,'physicians']= table['value'][0]
            if tabName=='patients':
                outdf.loc[row,'patient_gender']=table['gender'][0]
            if tabName=='Segment': 
                outdf.loc[row,'numSegment']=len(table['events_key'])         
            if tabName== 'AutoSegment':
                outdf.loc[row,'numAutoSegment']= len(table['timeval_key'])            
            if tabName== 'events':
                outdf.loc[row,'numEvents']= len(table['events_key'])
                valueList=[]
                for i in table['description']: 
                    i.replace('/','//')
                    i.replace(';','/')
                    valueList= valueList+[i+';']
                outdf.loc[row,'eventsDescription']=  ''.join(valueList)
            if tabName=='diagnosis':
                outdf.loc[row,'diagnosis']=table['value'][0]
            if tabName=='Image':
                outdf.loc[row,'numImages']=len(table['events_key'])

        #get time from piud.log:    
        piudDir= os.path.join(root[0:-9],'studyLog/piud.log')

        if not os.path.isfile(piudDir):continue
        with open(piudDir) as f:
            for line in f:
                #print(line)
                if 'Begin online study' in line:
                    beginTime= line[7:15]
                if 'End of realtime study' in line:
                    endTime= line[7:15]
        FMT= '%H:%M:%S'
        tdelta= datetime.datetime.strptime(endTime, FMT) - datetime.datetime.strptime(beginTime, FMT)
        outdf.loc[row,'beginTime']= beginTime
        outdf.loc[row,'endTime']=endTime
        outdf.loc[row,'duration']= tdelta
        break
    t1= time.time()
    print('time took to run 1st part: ', t1-t0)
    return outdf

def CathInfo(historical):                  
    # This will go through the xml files in Historical folder to extract catheter information: 
    historicalFile=[]
    impFilterFile=[]
    systemStateFile=[]
    for files in os.listdir(historical):
        filesdir= os.path.join(historical,files)
        if files.startswith('enGuides') and files.endswith('.xml') and os.path.getsize(filesdir)>0:
            historicalFile= files
        if files.startswith('impFilter') and files.endswith('.xml') and os.path.getsize(filesdir)>0:
            impFilterFile= files
        if files.startswith('systemState') and files.endswith('.xml') and os.path.getsize(filesdir)>0:
            systemStateFile= files
    #some files conversion failed causing xml files to have 0 bytes so should skip this
    if not historicalFile or not impFilterFile or not systemStateFile:
        print('Path with empty xml files, consider re-converting:', historical)
        return []
    print(historicalFile) #Question: is it ok to use last file assuming this is the latest version?
    path= os.path.join(historical,historicalFile)
    try:
        tree= ET.parse(path)
    except: 
        print('trying to parse this path: ',path)
        return []

    root= tree.getroot() 
    Cathlist=[] #Cath id 
    Brandlist=[] #Catheter brand names
    Manulist=[] #Catheter manufacturer
    Typelist=[] #Catheter types
    Modellist=[] #Catheter models
    Polaritylist=[] #Catheter polarity 
    NameList=[]
    ForceCath= 'N'
    SensorEnabledCath='N'
    HDGridCath= 'N'
    ECG='N'
    Respiration='N'
    PatchImp='N'
    
    lastVal='temp'
    for a in root.iter('CatheterId'): 
        if a.text==lastVal: continue #so don't repeat 
        lastVal= a.text
        if str(a.text)=='0' or str(a.text)=='1' or str(a.text)=='2': continue
        elif str(a.text)=='8':
            ForceCath = 'Y'
            continue
        else:
            if int(a.text)<50: continue
            Cathlist= Cathlist+ [str(a.text)+';'] #list of catheter ID used in the study!
    for a in root.iter('BrandName'):
        if str(a.text)=='None' : continue
        if 'Grid' in str(a.text): HDGridCath= 'Y'
        Brandlist= Brandlist+[str(a.text)+';']
    for a in root.iter('Manufacture'):
        if str(a.text)=='None': continue
        Manulist=Manulist+[str(a.text)+';']
    for a in root.iter('Type'):
        if str(a.text)=='None': continue
        if 'Sensor Enabled' in str(a.text): SensorEnabledCath='Y'
        if 'Contact Force' in str(a.text): ForceCath ='Y'
        Typelist=Typelist+[str(a.text)+';']
    for a in root.iter('Model'):
        if str(a.text)=='None': continue
        Modellist=Modellist+[str(a.text)+';']
    for a in root.iter('Polarity'):
        if str(a.text)=='None': continue
        Polaritylist= Polaritylist+ [str(a.text)+';']
    for a in root.iter('Name'):
        if str(a.text)=='ECG': 
            ECG='Y'
            continue
        if str(a.text)=='Respiration': 
            Respiration='Y'
            continue
        if str(a.text)=='Patch Imp': 
            PatchImp='Y'
            continue
        NameList= NameList+ [str(a.text)+';']
    cathCount= len(Cathlist) #number of catheter used

    impFilterPath= os.path.join(historical,impFilterFile)
    tree= ET.parse(impFilterPath)
    root= tree.getroot() 
    Filter= []
    for child in root:
        #print(child.tag, child.attrib)
        for content in child: 
            for subcontent in content:
                if subcontent.tag=='SelectedLowpassFilter':
                    Filter= subcontent.text
            

    systemStatePath= os.path.join(historical,systemStateFile)
    tree= ET.parse(systemStatePath)
    root= tree.getroot() 
    MagNavType=[]
    for child in root:
        #print(child.tag, child.attrib)
        for content in child: 
            for subcontent in content:
                if subcontent.tag=='MagneticNavigationType':
                    MagNavType= subcontent.text

    
    return ''.join(Cathlist), ''.join(NameList), ''.join(Brandlist), ''.join(Manulist), ''.join(Typelist), ''.join(Modellist), cathCount, ForceCath, SensorEnabledCath, HDGridCath,''.join(Polaritylist), Filter, MagNavType, ECG, Respiration,PatchImp

#looking at folder ensiteModel, file AutoMarkSummaryList.csv
def EnsiteInfo(ensiteModelPath):
    #ensiteModelPath= 'C:\\Users\\HoangT04\\Documents\\DataBaseWithPython\\study_dwsG700104_2017_01_02_01_45_24\\ensiteModel'
    AutoMarkPath= os.path.join(ensiteModelPath, 'AutoMarkSummaryList.csv')
    if not os.path.isfile(AutoMarkPath): return []
    with open(AutoMarkPath) as csvfile:
        reader= csv.reader(csvfile)
        for row in reader: #row is a list
            if '# of RF episodes:' in str(row):
                RFepisodes= [int(s) for s in row[0].split( ) if s.isdigit()][0]
            if '# of lesions:' in str(row):
                lesionsNum= [int(s) for s in row[0].split( ) if s.isdigit()][0]
            if '# of transitions:' in str(row):
                transitionNum= [int(s) for s in row[0].split( ) if s.isdigit()][0]
            if 'RF time:' in str(row):
                RFtime= [int(s) for s in row[0].split( ) if s.isdigit()][0]
            if 'Lesion Spacing param:' in str(row):
                lesionSpacing= [int(s) for s in row[0].split( ) if s.isdigit()][0]

    geometryPath= os.path.join( ensiteModelPath,'geometry.xml')
    print(geometryPath)
    if not os.path.isfile(geometryPath): 
        return[]
    try: 
        with open(geometryPath, 'rb') as xml_file:
            tree= ET.parse(xml_file)
            root= tree.getroot()
    except:
        return[]
    paramNames=['CompensatedGeo','MagneticGeo','MediGuideGeo','ProjOnDif','MaxProjDist','UpperGatingThres','LowerGatingThres','GateGeoPoints','GateFiducials','MagneticToNavexCount','EditSurfacesCount','DifRegistration','DifSurfaceSets']
    paramValues= [0]*len(paramNames)
    lookForThese=['Compensated','IsMagnetic','IsMediGuide','ProjOnDif','MaxProjDist','UpperGatingThreshold','LowerGatingThreshold','GateGeoPoints','GateFiducials','count','NumSurfaces','Registered','NumSurfaceSets']
    for child in root:
        for content in child:
            for subcontent in content:
                if str(subcontent.tag) in lookForThese: 
                    i= lookForThese.index(str(subcontent.tag))
                    paramValues[i]= subcontent.text
                for each in subcontent:
                    if str(each.tag) in lookForThese: 
                       i= lookForThese.index(str(each.tag))
                       paramValues[i]= each.text 
    print(paramNames)
    print(paramValues)
                    
    return RFepisodes, lesionsNum, transitionNum, RFtime, lesionSpacing

def FilterSettingInfo(settingsPath):
    filterList=['Powerline50Hz']
    filterParam=['F']
    for files in os.listdir(settingsPath):
        if'bioFilter.xml'  in files:
            path= os.path.join(settingsPath,'bioFilter.xml' )
            try:
                tree= ET.parse(path)
                root= tree.getroot()
            except:
                return []
            for child in root:
                for content in child:
                    for subcontent in content:
                        if not 'Filter' in subcontent.tag:
                            filterParam[0]='T'
                            continue
                        filterList= filterList+[str(subcontent.tag)]
                        for subsub in subcontent:
                            highlow=[]
                            if 'FilterHighpass' in subsub.tag:
                                high=subsub.text
                            if 'FilterLowpass' in subsub.tag:
                                low=subsub.text
                        highlow=highlow+[str(high)]+[str(low)]
                        filterParam= filterParam+[str(highlow)]
    return filterList, filterParam


#given a data directory, list studies within the directory, open the DWSsummary file, check if that study ID is there
def dataSummary(inputDir= '/var/STJ/Clinical/systemStudy'):
#inputDir= '/var/STJ/Clinical/systemStudy' #input is something likethis
    dataDf= searchDB(inputDir)    #pd.read_csv('DWSsummary_Clinical2017.csv', encoding='cp1252')
    for studyID in os.listdir(inputDir):
        #find matching study ID
        i= np.where(dataDf['studyID'].str.match(studyID))
        if len(i[0])<1: continue
        print(studyID)

        #add Cathter info to data
        basePath= os.path.join(inputDir,studyID)
        historical= os.path.join(basePath, 'historical')
        allList= CathInfo(historical)
        if not allList: continue
        newcols= ['CatheterID','CathterName','CatheterBrands','CatheterManufacturers','CatheterTypes','CatheterModel','CatheterCount','ForceCath', 'SensorEnabledCath', 'HDGridCath','Polarity','ImpedanceFilter','MagneticNavigationType','ECG','Respiration','PathImp']
        a=0
        for item in newcols:
            try:
                dataDf.loc[i[0],item]= allList[a]
            except:
                print('DataDf.loc problem, line 153', i[0], item)
            a=a+1

        #add RF info to data
        ensiteModelPath= os.path.join(basePath, 'ensiteModel')
        allFound= EnsiteInfo(ensiteModelPath)
        if not allFound: continue
        
        newcols= ['RFepisodes','lesionsNum', 'transitionNum','RFtime','lesionSpacing']
        a=0
        print(i[0])
        for item in newcols:
            try:
                dataDf.loc[i[0],item]= allFound[a]
            except:
                print('DataDf.loc problem, line 165', i[0], item)
            a=a+1
        
        #add Filter settings info to data
        settingsPath= os.path.join(basePath, 'settings')
        colNames, colVals= FilterSettingInfo(settingsPath)
        print(colNames, colVals)
        if not colNames or not colVals: continue      
        newcols= colNames
        a=0
        print(i[0])
        for item in newcols:
            try:
                dataDf.loc[i[0],item]= colVals[a]
            except:
                print('DataDf.loc problem', i[0], item)
            a=a+1
        break

    dataDf.to_csv('dataSummary_06.25.2018.csv', index=False)
    print('Done')
    print(dataDf.iloc[0])
if __name__== '__main__':
    dataSummary(sys.argv[1]) #input will be a directory
    
