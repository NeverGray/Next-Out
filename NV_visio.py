import re
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd

import NV_run
import NV_settings

try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

from pathlib import Path

ns = {"Visio": "http://schemas.microsoft.com/office/visio/2012/main"}


def valid_simtime(simtime, df, gui=""):
    timeseries_index = df.index.unique(0)  # Creates a series of unique times
    timeseries_list = timeseries_index.tolist()
    time = float(simtime)
    if time == -1 or time > timeseries_list[-1]:
        time = timeseries_list[-1]
        NV_run.run_msg(gui, f'Using last simulation time {time}')
    elif not time in timeseries_list:
        for x in timeseries_list:
            if x - time > 0:
                time = x
                break
        NV_run.run_msg(gui, f"Could not find requested simulation time. Using {time}")
    return time


def get_visXML(visio_template):
    VZip = zipfile.ZipFile(visio_template)
    names = VZip.namelist()
    vxmls = {}
    for name in names:
        m = re.match("visio/pages/[^/]+[.xml]$", name)
        if m:
            vxmls[name] = VZip.read(name)  # Create dictionary of name paths and files
    return vxmls


# code to modify XML file for emergency (or PIT) simualtions
def emod_visXML(vxml, data, ses_output_str="Not Available", simtime=0.00, output_meta_data={}):
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
    file_path = Path(ses_output_str)
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
                ShapeChild = NV01_text(ShapeChild, ns, value)
    # Update Sub-NV01 The "../.." at the end of the string moves the selection up two tiers (Section, then shape)
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
        ses_airflow = get_df_values(data["SSA"], (simtime, SegID), "Airflow")
        airflow = str(round(abs(ses_airflow), 1))
        ses_velocity = get_df_values(data["SSA"], (simtime, SegID), "Air_Velocity")
        velocity = str(round(abs(ses_velocity), 1))
        ses_airtemp = get_df_values(data["SST"], (simtime, SegID, SubID), "Air_Temp")
        airtemp = str(round(ses_airtemp, 1)) + "°"
        ses_WallTemp = get_df_values(data["SST"], (simtime, SegID, SubID), "Wall_Temp")
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
                ShapeChild = NV01_text(ShapeChild, ns, value)
        find_string = ".//Visio:Cell[@N='FlipX']"
        Shape = NV01_arrow(Shape, find_string, ns, flip)  # Flip arrow as needed
    # Update Damper Shapes
    for Shape in P1root.findall(".//Visio:Row[@N='Damper_Segment']../..", ns):
        Shape = update_damper(Shape, output_meta_data['damper_position'], ns)
    return P1root

def update_damper(shape, damper_position_dict, ns):
    try:
        SegID = int(shape.find(".//Visio:Row[@N='Damper_Segment']/Visio:Cell", ns).get("V")) 
    except:
        SegID = -1
    status = damper_position_dict.get(SegID)
    damper_settings = NV_settings.damper_settings.get(status)
    shape_text = shape.find(".//Visio:Shape[@Name='NV01_Damper_Position']",ns)
    shape_text = NV01_text(shape_text, ns, damper_settings['status'])
    shape_child = shape.find(".//Visio:Shape[@Name='Damper_Closed_Lines']", ns)
    line_shapes = shape_child.findall(".//Visio:Shape",ns)
    for line_shape in line_shapes:
        if line_shape.find(".//Visio:Cell[@N='LineColor']",ns) is None:
            line_properties ={
                'N':'LineColor',
                'Y': damper_settings['line_color_v'],
                'F':damper_settings['line_color_f']
            }
            ET.SubElement(line_shape,'Cell',attrib=line_properties)
        else:
            try:
                line_shape.find(".//Visio:Cell[@N='LineColor']",ns).set('V',damper_settings['line_color_v'])
                line_shape.find(".//Visio:Cell[@N='LineColor']",ns).set('F',damper_settings['line_color_f'])
            except:
                print('No LineColor cells are there')
    '''#for shape_babe in shape_child.findall(".//Visio:Cell[@N='LineColor']", ns):
    #    shape_babe.set("V",damper_settings['line_color_v'])
    #    shape_babe.set("F",damper_settings['line_color_f'])'''
    return shape


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

def NV01_text(ShapeChild, ns, value):
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


def write_visio(vxmls, visio_template, new_visio ,gui=""):
    # Sample Zip source code from https://stackoverflow.com/questions/513788/delete-file-from-zipfile-with-the-zipfile-module
    # TODO Write file to memory, BytesIO, then to file.
    with zipfile.ZipFile(visio_template, "r") as zin:
        try:
            with zipfile.ZipFile(new_visio, "w") as zout:
                for item in zin.infolist():
                    buffer = zin.read(item.filename)
                    # Write any files not updated by this code
                    if not (item.filename in vxmls):  
                        zout.writestr(item, buffer, compress_type=compression)
                zout.comment = b"Mfwfs_Hsbz"
        except:
            msg = ("Error writing "
                + str(new_visio)
                + ". Try closing the file and process again."
            )
            NV_run.run_msg(gui, msg)         
    try:
        with zipfile.ZipFile(new_visio, "a") as zappend:
            for name, vxml in vxmls.items():
                temp_string = ET.tostring(vxml, encoding="utf-8", xml_declaration=True)
                zappend.writestr(name, temp_string, compress_type=compression)
        NV_run.run_msg(gui,f'Created Visio Diagram {new_visio.name}')
    except:
        msg = "Error writing " + str(new_visio) + ". Try closing the file and process again."
        NV_run.run_msg(gui, msg)

def create_visio(settings, data, output_meta_data, gui=""):
    settings["simtime"] = valid_simtime(settings["simtime"], data["SSA"], gui)
    time_4_name = int(settings["simtime"])
    time_suffix = "-" + str(time_4_name) + ".vsdx"
    settings["new_visio"] = NV_run.get_results_path2(settings, output_meta_data, time_suffix)
    # Read in VISIO Template and update with SES OUtput
    vxmls = get_visXML(settings["visio_template"])  # gets the pages in the VISIO XML.
    for name, vxml in vxmls.items():
        vxmls[name] = emod_visXML(
            vxmls[name], data, settings["ses_output_str"][0][:-4], settings["simtime"], output_meta_data
        )
    write_visio(vxmls, settings["visio_template"], settings["new_visio"],gui)

if __name__ == "__main__":
    file_path_string = "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Python2021/siinfern.out"
    visio_template = "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Projects and Issues/2021-09-01 Stencils/Damper_064_pp.vsdx"
    results_folder_str = "C:/Users/msn/OneDrive - Never Gray/Software Development/Next-Vis/Projects and Issues/2021-09-01 Stencils"
    settings = {
        "ses_output_str": [file_path_string],
        "visio_template": visio_template,
        "results_folder_str": results_folder_str,
        "simtime": 9999.0,
        "version": "tbd",
        "control": "First",
        "output": ["Visio"],
    }
    NV_run.single_sim(settings)
    print('Finished')
