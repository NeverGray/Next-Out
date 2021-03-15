import pandas as pd
import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED
import xml.etree.ElementTree as ET
import re
import os

def valid_simtime(simtime, data):
    timeseries_index = data.index.unique(0) #Creates a series of unique times
    timeseries_list = timeseries_index.tolist()
    time = float(simtime)
    if time == -1 or time > timeseries_list[-1]:
        time = timeseries_list[-1]
        print('Using last simulation time ', time)
    elif not time in timeseries_list:
        for x in timeseries_list:
            if (x - time >0):
                time = x
                break
        print('Could not find requested simulation time. Using ',time)
    return time

def get_visXML(visname):
    VZip = zipfile.ZipFile(visname)
    names = VZip.namelist()
    vxmls={}
    for name in names:
        m = re.match('visio/pages/[^/]+[.xml]$',name)
        if m:
            vxmls[name] = VZip.read(name) #Create dictionary of name paths and files
    return vxmls

#TODO Write function to update text of elements in Visio XML file

#code to modify XML file for emergency simualtions
def emod_visXML(vxml, data, simname="Not Available", simtime = 0.00): 
    P1root=ET.fromstring(vxml) #create XML element from the string
    ET.register_namespace('','http://schemas.microsoft.com/office/visio/2012/main') #Need to register name space to reproduce file.
    ET.register_namespace('r','http://schemas.openxmlformats.org/officeDocument/2006/relationships')
    ns = {'Visio': 'http://schemas.microsoft.com/office/visio/2012/main'} #Namespace dictionary to ease file navigation
    #Airflow arrow shape update
    #Find all shape with sub-child NV01_SegID. The "../.." at the end of the string moves the selection up two tiers to Shape
    for Shape in P1root.findall(".//Visio:Row[@N='NV01_SegID']../.." , ns): 
        SegID=int(Shape.find(".//Visio:Row[@N='NV01_SegID']/Visio:Cell",ns).get('V')) #Get the value for the Segment ID from XML and save as SegID
        SubID=1
        try: #Pull airflow from the dataframe, if it does not exist, use an airflow 999.9
            ses_airflow = data.loc[(simtime,SegID,SubID),"Airflow"]
        except:
            ses_airflow = -999.9
        airflow=str(round(abs(ses_airflow),1)) #The absolute airflow as a string
        ShapeChild=Shape.find(".//Visio:Shape[@Name='NV01_AirFlow']",ns) #Selects the NV01_Airflow Object
        #ET.SubElement(ShapeChild,"Text").text=airflow 
        ShapeBabe=ShapeChild.find(".//Visio:Text",ns) #Select the child's babe with text value
        if ET.iselement(ShapeBabe): #If element already exists, change the value
            ShapeBabe.text=airflow
        else:     
            ET.SubElement(ShapeChild,"Text").text=airflow #Adds text element and value if elemnt doesn't exist
        #Determine arrow direction
        if (ses_airflow >= 0):
            Flip=0
        else:
            Flip=1    
        ShapeChild=Shape.find(".//Visio:Cell[@N='FlipX']",ns) #Find all Flipx propertiesin the file       
        if ET.iselement(ShapeChild):
            ShapeChild.set('V',str(Flip))
        else:
            ET.SubElement(Shape,"Cell",V=str(Flip),N='FlipX')
    #Update all shapes with simple text
    text_shapes = [ #Define all simple shates with simple text
        [".//Visio:Shape[@Name='NV01_SimNam']",simname],
        [".//Visio:Shape[@Name='NV01_SimTime']",str(int(simtime))]
        ]
    for ts in text_shapes: #Iterate through all samples with simple text
        P1root = text_update(ts[0],ts[1],P1root,ns)
    #ET.ElementTree(P1root).write("page1.xml",encoding='utf-8',xml_declaration=True) #TODO eliminate writing to disk in this procedure
    return P1root

def text_update(find_string, text_value, root, ns):
    for Shape in root.findall(find_string,ns):
        ShapeChild=Shape.find(".//Visio:Text",ns)
        if ET.iselement(ShapeChild):
            ShapeChild.text = text_value
        else:
            ET.SubElement(Shape,"Text").text= text_value #previously str(Airflow)#TODO eliminate writing to disk in this procedure
    return root


def write_visio(vxmls, visname, new_visio):
    #Sample Zip source code from https://stackoverflow.com/questions/513788/delete-file-from-zipfile-with-the-zipfile-module
    with zipfile.ZipFile(visname, 'r') as zin:
        with zipfile.ZipFile(new_visio, 'w') as zout:
            for item in zin.infolist(): 
                buffer = zin.read(item.filename)
                if not (item.filename in vxmls): #File was not updated by this code
                    zout.writestr(item, buffer,compress_type=compression)                   
            zout.comment= b'Mfwfs_Hsbz'
    temp = new_visio[:-4] + ".xml" #unique file names to all multiprocessing
    with zipfile.ZipFile (new_visio, 'a') as zappend:
        for name, vxml in vxmls.items():
            #TODO speedup file writing after updating to Python 3.8. Otherwise, cannot write xml_declaration easily
            ET.ElementTree(vxml).write(temp, encoding='utf-8', xml_declaration=True)
            zappend.write(temp,name,compress_type = compression)
            os.remove(temp)
    print("Created Visio Diagram ",new_visio)

def update_visio(settings,data):
    vxmls = get_visXML(settings['visname']) #gets the pages in the VISIO XML.
    for name, vxml in vxmls.items():
        vxmls[name] = emod_visXML(vxmls[name],data, settings['simname'][:-4], settings['simtime'])
    write_visio(vxmls, settings['visname'], settings['new_visio'])