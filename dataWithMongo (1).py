import datetime
from mongoengine import *
#This will set the structure for the data and will be called in scanEnSitewithMongo.py

#Segments
class SegmentInfo(EmbeddedDocument):
    SEG_TYPE= ['AUTO','MANUAL']
    seg_type= StringField(max_length=8, choices= SEG_TYPE) #not in csv yet,still need to find
    length= DateTimeField()#still need to find this

class Segment(EmbeddedDocument):
    name= StringField()
    info= ListField(EmbeddedDocumentField(SegmentInfo))
    def addSegmentInfo(self, seg: SegmentInfo):
        self.info.append(seg)

#Catheters
class CathInfo(EmbeddedDocument):
    brand= StringField()
    manufacturer= StringField()
    types= StringField()
    model= StringField()
    polarity= StringField()
    
class Catheter(EmbeddedDocument):
    ID= IntField(unique=False)
    name= StringField()  
    info= ListField(EmbeddedDocumentField(CathInfo))
    def addCathInfo(self, info: CathInfo):
        self.info.append(info)

#Maps
class MapsInfo(EmbeddedDocument):
    map_type= StringField()
    made_from= StringField()
    
class Maps(EmbeddedDocument):
    name= StringField()
    info= ListField(EmbeddedDocumentField(MapsInfo))
    def addMapsInfo(self, maps: MapsInfo):
        self.info.append(maps)
        
#The rest
class Ablation(EmbeddedDocument):
    start_time= StringField()
    end_time= StringField()
    duration= StringField()
    total_time= StringField()
    total_number= StringField()
    catheter_SN= StringField()

class TactiSys(EmbeddedDocument):
    SN= StringField()
    software_version= StringField()
    average_force= IntField()
    std_force= IntField()
    min_force= IntField()
    max_force= IntField()


        
        
class AutoMark(EmbeddedDocument):
    RF_episodes= IntField()
    lesions_num= IntField()
    transition_num= IntField()
    RF_time= IntField()
    lesion_spacing= IntField()

class Geometry(EmbeddedDocument):
    compensated= BooleanField()
    magnetic= BooleanField()
    mediGuide= BooleanField()
    project_on_DIF= BooleanField()
    navX_project_dist= IntField()
    upper_gating_threshold= IntField()
    lower_gating_threshold= IntField()
    gate_geo_points= BooleanField()
    gate_fiducials= BooleanField()
    magnetic_to_NavX_count= IntField()
    edit_surfaces_count= IntField()
    dif_registration= BooleanField()
    dif_surface= IntField()

class Patient(EmbeddedDocument):
    GENDER= ['NOT_SPECIFIED','MALE','FEMALE']
    gender= StringField(choices=GENDER)
    diagnosis= StringField()
    patient_weight= FloatField(min_value=None)
    
    
class Events(EmbeddedDocument):
    total_number= IntField()
    description= ListField() #this should be something else

class Filter(EmbeddedDocument):
    impedance= StringField()
    powerline_50Hz= BooleanField()#from settings folder
    mea_HP= IntField()
    mea_LP= IntField()
    ECG_HP= IntField()
    ECG_LP=IntField()
    EPCathBio_HP= IntField()
    EPCathBio_LP=IntField()
    bipol_HP= IntField()
    bipol_LP= IntField()
    analog_HP= IntField()
    analog_LP= IntField()

class Study(Document): #from studyLog folder
    studyID= StringField()
    year= StringField()
    beginTime= StringField() #can change this to datetime field later
    endTime= StringField()
    duration= StringField()
    dws_version= StringField() #from database Folder
    system= StringField()
    studyType= StringField()
    physicians= StringField()
    numImages= IntField()
    
    segments= ListField(EmbeddedDocumentField(Segment))
    def addSegment(self, seg: Segment):
        self.segments.append(seg)

    catheters= ListField(EmbeddedDocumentField(Catheter))
    def addCath(self, catheter: Catheter):
        self.catheters.append(catheter)

    ablations=  EmbeddedDocumentField(Ablation)

    geometry= EmbeddedDocumentField(Geometry)

    patient= EmbeddedDocumentField(Patient)

    events= EmbeddedDocumentField(Events)

    filters= EmbeddedDocumentField(Filter)

    maps= ListField(EmbeddedDocumentField(Maps))
    def addMap(self, m: Maps):
        self.maps.append(m)
    