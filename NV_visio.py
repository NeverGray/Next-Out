import zipfile

import pandas as pd

try:
    import zlib

    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ns = {"Visio": "http://schemas.microsoft.com/office/visio/2012/main"}


def valid_simtime(simtime, df):
    timeseries_index = df.index.unique(0)  # Creates a series of unique times
    timeseries_list = timeseries_index.tolist()
    time = float(simtime)
    if time == -1 or time > timeseries_list[-1]:
        time = timeseries_list[-1]
        print("Using last simulation time ", time)
    elif not time in timeseries_list:
        for x in timeseries_list:
            if x - time > 0:
                time = x
                break
        print("Could not find requested simulation time. Using ", time)
    return time


def get_visXML(visname):
    VZip = zipfile.ZipFile(visname)
    names = VZip.namelist()
    vxmls = {}
    for name in names:
        m = re.match("visio/pages/[^/]+[.xml]$", name)
        if m:
            vxmls[name] = VZip.read(name)  # Create dictionary of name paths and files
    return vxmls


# code to modify XML file for emergency (or PIT) simualtions
def emod_visXML(vxml, df_dict, simname="Not Available", simtime=0.00, output_meta_data={}):
    P1root = ET.fromstring(vxml)  # create XML element from the string
    ET.register_namespace(
        "", "http://schemas.microsoft.com/office/visio/2012/main"
    )  # Need to register name space to reproduce file.
    ET.register_namespace(
        "r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    )
    ns = {
        "Visio": "http://schemas.microsoft.com/office/visio/2012/main"
    }  # Namespace dictionary to ease file navigation

    # Update SimInfo-NV01 text fields
    file_path = Path(simname)
    sim_base_name = file_path.name
    file_time = output_meta_data.get("file_time") 
    shape_dict = {
        ".//Visio:Shape[@Name='NV01_SimNam']": sim_base_name,
        ".//Visio:Shape[@Name='NV01_FileTime']": file_time,
        ".//Visio:Shape[@Name='NV01_SimTime']": str(simtime),
    }
    for find_string, value in shape_dict.items():
        ShapeChilds = P1root.findall(find_string, ns)
        if ShapeChilds:
            for ShapeChild in ShapeChilds:
                ShapeChild = NV01_text(ShapeChild, find_string, ns, value)
    # Update Sub-NV01The "../.." at the end of the string moves the selection up two tiers (Section, then shape)
    for Shape in P1root.findall(".//Visio:Row[@N='NV01_SegID']../..", ns):
        # Get SegID and Sub-segment from XML
        try:
            SegID = int(
                Shape.find(".//Visio:Row[@N='NV01_SegID']/Visio:Cell", ns).get("V")
            ) 
        except:
            continue
        try: 
            SubID = int(
                Shape.find(".//Visio:Row[@N='NV01_Sub']/Visio:Cell", ns).get("V")
            )
        except:
            SubID = 1
        # Pull from data from SSA and SST dataframe
        ses_airflow = get_df_values(df_dict["SSA"], (simtime, SegID), "Airflow")
        airflow = str(round(abs(ses_airflow), 1))
        ses_velocity = get_df_values(df_dict["SSA"], (simtime, SegID), "AirVel")
        velocity = str(round(abs(ses_velocity), 1))
        ses_airtemp = get_df_values(df_dict["SST"], (simtime, SegID, SubID), "AirTemp")
        airtemp = str(round(ses_airtemp, 1)) + "°"
        ses_WallTemp = get_df_values(df_dict["SST"], (simtime, SegID, SubID), "WallTemp")
        walltemp = str(round(ses_WallTemp, 1)) + "°"
        # Determines if airflow needs to be flipped for negative airflow
        if (ses_airflow >= 0):  
            flip = 0
        else:
            flip = 1
        # Update shape with information {find_string: value}
        shape_dict = {
            ".//Visio:Shape[@Name='NV01_AirFlow']": airflow,
            ".//Visio:Shape[@Name='NV01_Velocity']": velocity,
            ".//Visio:Shape[@Name='NV01_AirTemp']": airtemp,
            ".//Visio:Shape[@Name='NV01_WallTemp']": walltemp,
        }
        for find_string, value in shape_dict.items():
            ShapeChild = Shape.find(find_string, ns)
            if ShapeChild:
                ShapeChild = NV01_text(ShapeChild, find_string, ns, value)
        find_string = ".//Visio:Cell[@N='FlipX']"
        Shape = NV01_arrow(Shape, find_string, ns, flip)  # Flip arrow as needed

    # Update Airflow-NV01
    return P1root


def get_df_values(df, df_indexes, column_name):
    try:
        df_value = df.at[df_indexes, column_name]
    except:
        df_value = 0.0
    return df_value


def NV01_arrow(Shape, find_string, ns, flip):
    ShapeTemp = Shape
    try:
        ShapeChild = Shape.find(find_string, ns)
        if ET.iselement(ShapeChild):  # If element already exists, change the value
            ShapeChild.set("V", str(flip))
        else:
            ET.SubElement(Shape, "Cell", V=str(flip), N="FlipX")
        return Shape
    except:
        print("Error with NV01_arrow")
        return ShapeTemp

def NV01_text(ShapeChild, find_string, ns, value):
    ShapeTemp = ShapeChild
    try:
        ShapeBabe = ShapeChild.find(".//Visio:Text", ns)
        if ET.iselement(ShapeBabe):  # If element already exists, change the value
            ShapeBabe.text = value  # Selects the NV01_Airflow ObjectShapeBabe=ShapeChild.find(".//Visio:Text",ns)
        else:
            ET.SubElement(
                ShapeChild, "Text"
            ).text = value  # Adds text element and value if elemnt doesn't exist
        return ShapeChild
    except:
        print("Error with NV01_text")
        return ShapeTemp


def SimInfo_NV01(Shape, find_string, ns, value):
    ShapeTemp = Shape
    try:
        ShapeChild = Shape.find(find_string, ns)
        ShapeBabe = ShapeChild.find(".//Visio:Text", ns)
        if ET.iselement(ShapeBabe):  # If element already exists, change the value
            ShapeBabe.text = value  # Selects the NV01_Airflow ObjectShapeBabe=ShapeChild.find(".//Visio:Text",ns)
        else:
            ET.SubElement(
                ShapeChild, "Text"
            ).text = value  # Adds text element and value if elemnt doesn't exist
        return Shape
    except:
        print("Error with SimInfo_NV01")
        return ShapeTemp


def write_visio(vxmls, visname, new_visio):
    # Sample Zip source code from https://stackoverflow.com/questions/513788/delete-file-from-zipfile-with-the-zipfile-module
    with zipfile.ZipFile(visname, "r") as zin:
        try:
            with zipfile.ZipFile(new_visio, "w") as zout:
                for item in zin.infolist():
                    buffer = zin.read(item.filename)
                    if not (
                        item.filename in vxmls
                    ):  # File was not updated by this code
                        zout.writestr(item, buffer, compress_type=compression)
                zout.comment = b"Mfwfs_Hsbz"
        except:
            print(
                "Error writing "
                + new_visio
                + ". Try closing the file and process again."
            )
    temp = new_visio[:-4] + ".xml"  # unique file names to all multiprocessing
    try:
        with zipfile.ZipFile(new_visio, "a") as zappend:
            for name, vxml in vxmls.items():
                # TODO speedup file writing after updating to Python 3.8. Otherwise, cannot write xml_declaration easily
                ET.ElementTree(vxml).write(temp, encoding="utf-8", xml_declaration=True)
                zappend.write(temp, name, compress_type=compression)
                os.remove(temp)
        print("Created Visio Diagram " + new_visio)
    except:
        print(
            "Error writing " + new_visio + ". Try closing the file and process again."
        )


def update_visio(settings, df_dict, output_meta_data):
    vxmls = get_visXML(settings["visname"])  # gets the pages in the VISIO XML.
    for name, vxml in vxmls.items():
        vxmls[name] = emod_visXML(
            vxmls[name], df_dict, settings["simname"][:-4], settings["simtime"], output_meta_data
        )
    write_visio(vxmls, settings["visname"], settings["new_visio"])
