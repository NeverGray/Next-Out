import re
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd
import win32com.client

import NO_run
import NV_settings
import NV_Tunnel_Segment
from NV_CONSTANTS import DEGREE_SYMBOL

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
        #NO_run.run_msg(gui, f'Using last simulation time {time}')
    elif not time in timeseries_list:
        for x in timeseries_list:
            if x - time > 0:
                time = x
                break
        NO_run.run_msg(gui, f"Could not find requested simulation time. Using {time}")
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
def emod_visXML(vxml, data, file_stem, simtime=0.00, output_meta_data={},gui=""):
    P1root = ET.fromstring(vxml)  # create XML element from the string
    ET.register_namespace(
        "", "http://schemas.microsoft.com/office/visio/2012/main"
    )  # Need to register name space to reproduce file.
    ET.register_namespace(
        "r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    )
    #TODO Move simtime outside of page file to speed up processing
    simtime_df = data["SSA"].loc[simtime]
    # SimInfo-NV01 text fields
    sim_base_name = file_stem
    try:
        if output_meta_data['ses_version'] == 'SI from IP':
            sim_base_name = sim_base_name + '_SI'
        elif output_meta_data['ses_version'] == 'IP from SI':
            sim_base_name = sim_base_name + '_IP'
    except:
        NO_run.run_msg(gui, f'Error checking SES version')   

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
                ShapeChild = NV02_text(value, ShapeChild)
    
    # Damper
    for Shape in P1root.findall(".//Visio:Row[@N='Damper_Segment']../..", ns):
        try:
            update_damper(Shape, output_meta_data['damper_position'])
        except:
            NO_run.run_msg(gui, f'Error Updating Damper')
    
    # Fan
    for Shape in P1root.findall(".//Visio:Row[@N='Fan_Segment']../..", ns):
        try:
            update_fan(Shape, output_meta_data['form5_fan_data'], simtime, ns)
        except:
            NO_run.run_msg(gui, f'Error Updating Fan')
    
    # Jet Fan Segments
    if not('jet_fan_data' in output_meta_data):
        output_meta_data['jet_fan_data'] = None
    for Shape in P1root.findall(".//Visio:Row[@N='Jet_Fan_Segment']../..", ns):
        try:
            update_jet_fan(Shape, output_meta_data['jet_fan_data'], simtime, ns)
        except:
            NO_run.run_msg(gui, f'Error Updating Jet Fan')
    
    # Airflow_NV02
    if P1root.find(".//Visio:Row[@N='Airflow_NV02']../..", ns) is not None:
        for shape in P1root.findall(".//Visio:Row[@N='Airflow_NV02']../..", ns):
            try:
                update_airflow_NV02(simtime_df, shape)
            except:
                NO_run.run_msg(gui, f'Error updating airflow_NV02')
    
    # Velocity_NV02
    if P1root.find(".//Visio:Row[@N='Velocity_NV02']../..", ns) is not None:
        for shape in P1root.findall(".//Visio:Row[@N='Velocity_NV02']../..", ns):
            try:
                update_velocity_NV02(simtime_df, shape)
            except:
                NO_run.run_msg(gui, f'Error Updating velocity_NV02')
    
    # Temperature_NV02
    if P1root.find(".//Visio:Row[@N='Temperature_seg_NV02']../..", ns) is not None:
        #TODO Reduce time by moving SST_simtime outside of this script
        SST_simtime = data['SST'].loc[simtime]
        for shape in P1root.findall(".//Visio:Row[@N='Temperature_seg_NV02']../..", ns):
            try:
                update_temperature_NV02(simtime_df, SST_simtime, shape)
            except:
                NO_run.run_msg(gui, f'Error Updating velocity_NV02')
    
    # Update Tunnel Segments
    if P1root.find(".//Visio:Row[@N='Tunnel_Segment_NV01']../..", ns) is not None:
        #TODO Reduce time by moving segment_time_df outside of this script
        segment_time_df = NV_Tunnel_Segment.create_segment_info(data, output_meta_data, simtime)
        for shape in P1root.findall(".//Visio:Row[@N='Tunnel_Segment_NV01']../..", ns):
            try:
                update_tunnel_segment(shape, segment_time_df)       
            except:
                NO_run.run_msg(gui, f'Error Updating Tunnel Segment')
    return P1root

def update_temperature_NV02(simtime_df, SST_simtime, shape):
    seg_id = int(shape.find(".//Visio:Row[@N='Temperature_seg_NV02']/Visio:Cell", ns).get("V", default =-1))
    sub_id = int(shape.find(".//Visio:Row[@N='temperature_sub_NV02']/Visio:Cell", ns).get("V", default =-1))
    #Default values 1 of 2
    end_arrow = '5'
    begin_arrow = '0'
    if seg_id in simtime_df.index:
        #Update for all values (see previous code)
        ses_airflow = simtime_df.loc[seg_id]['Airflow']
        airflow = str(round(abs(ses_airflow), 1))
        if (ses_airflow < 0):  
            end_arrow = '0'
            begin_arrow = '5'
    else:
        airflow = 'Airflow?'
    # Default values if actaul values aren't found
    airtemp = 'Air Temp?'
    walltemp = 'Wall Temp?'
    actual_airflow = "Actual Flow?"  
    # Lookup values from post-processed data
    if (seg_id,sub_id) in SST_simtime.index:
        ses_airtemp = SST_simtime.loc[seg_id,sub_id]['Air_Temp']
        if not pd.isna(ses_airtemp):  
            airtemp = str(round(ses_airtemp, 1)) + DEGREE_SYMBOL
        if 'Wall_Temp' in SST_simtime.columns:
            ses_WallTemp = SST_simtime.loc[seg_id,sub_id]['Wall_Temp']
            if not pd.isna(ses_WallTemp): 
                walltemp = str(round(ses_WallTemp, 1)) + DEGREE_SYMBOL
        if 'Actual_Airflow_NV' in SST_simtime.columns:
            Actual_Airflow_NV = SST_simtime.loc[seg_id,sub_id]['Actual_Airflow_NV']
            if not pd.isna(Actual_Airflow_NV):
                actual_airflow = str(round(abs(Actual_Airflow_NV), 1))

    # Update Arrow
    name = 'Arrow_NV02'
    cell_n_v_dictionary ={
                'EndArrow': end_arrow,
                'BeginArrow': begin_arrow
            }
    update_shape(shape, name, cell_n_v_dictionary)  
    # Update text
    shape_dict = {
            ".//Visio:Shape[@Name='airflow_text_NV02']": airflow,
            ".//Visio:Shape[@Name='air_temp_text_NV02']": airtemp,
            ".//Visio:Shape[@Name='wall_temp_text_NV02']": walltemp,
            ".//Visio:Shape[@Name='actual_airflow_text_NV02']": actual_airflow
        }
    for find_string, value in shape_dict.items():
        child = shape.find(find_string, ns)
        NV02_text(value, child)

def update_airflow_NV02(simtime_df, shape):
    seg_id = int(shape.find(".//Visio:Row[@N='Airflow_NV02']/Visio:Cell", ns).get("V", default =-1))
            #Default values 1 of 2
    end_arrow = '5'
    begin_arrow = '0'
    if seg_id in simtime_df.index:
        ses_airflow = simtime_df.loc[seg_id]['Airflow']
        airflow = str(round(abs(ses_airflow), 1))
        if (ses_airflow < 0):  
            end_arrow = '0'
            begin_arrow = '5'
    else:
        airflow = 'Airflow?'
            #Update arrows
    name = 'Arrow_NV02'
    cell_n_v_dictionary ={
                'EndArrow': end_arrow,
                'BeginArrow': begin_arrow
            }
    update_shape(shape, name, cell_n_v_dictionary)    
    child = shape.find(".//Visio:Shape[@Name='airflow_text_NV02']",ns)
    NV02_text(airflow, child)

def update_velocity_NV02(simtime_df, shape):
    seg_id = int(shape.find(".//Visio:Row[@N='Velocity_NV02']/Visio:Cell", ns).get("V", default =-1))
            #Default values 1 of 2
    end_arrow = '5'
    begin_arrow = '0'
    if seg_id in simtime_df.index:
        ses_airflow = simtime_df.loc[seg_id]['Air_Velocity']
        airflow = str(round(abs(ses_airflow), 1))
        if (ses_airflow < 0):  
            end_arrow = '0'
            begin_arrow = '5'
    else:
        airflow = 'Velocity?'
            #Update arrows
    name = 'Arrow_NV02'
    cell_n_v_dictionary ={
                'EndArrow': end_arrow,
                'BeginArrow': begin_arrow
            }
    update_shape(shape, name, cell_n_v_dictionary)    
    child = shape.find(".//Visio:Shape[@Name='velocity_text_NV02']",ns)
    NV02_text(airflow, child)

def NV02_text(value, child):
    if ET.iselement(child):
        babe = child.find(".//Visio:Text", ns)
        if ET.iselement(babe):
            babe.text = value
        else:
            ET.SubElement(child,"Text").text = value

def update_tunnel_segment(shape, segment_time_df):
    # Look up values for segment values
    seg_id = int(
        shape.find(".//Visio:Row[@N='Tunnel_Segment_NV01']/Visio:Cell[@N='Value']",ns).get('V', default=-1))
    #Default values 1 of 2
    end_arrow = '5'
    begin_arrow = '0'
    train_fire_values = NV_settings.train_fire_values
    if seg_id in segment_time_df.index:
        data_airflow = segment_time_df.loc[seg_id]['Airflow']
        airflow = str(round(abs(data_airflow), 1))
        if (data_airflow < 0):  
            end_arrow = '0'
            begin_arrow = '5'
        active_fire = segment_time_df.loc[seg_id]['active_fire']
        train_present = segment_time_df.loc[seg_id]['train_present']
        # Update Template
    else: #Default values 2 of 2
        airflow = 'Airflow?'
        active_fire = 'unknown'
        train_present = 'unknown'
    #Update arrows, fire, and train
    name = 'Arrow_NV02'
    cell_n_v_dictionary ={
        'EndArrow': end_arrow,
        'BeginArrow': begin_arrow
    }
    update_shape(shape, name, cell_n_v_dictionary)
    name = 'Fire'
    cell_n_v_dictionary ={
        "FillForegndTrans": train_fire_values[active_fire],
        "FillBkgndTrans": train_fire_values[active_fire]
        }
    update_shape(shape, name, cell_n_v_dictionary)
    name = 'Train'
    cell_n_v_dictionary ={
        "FillForegndTrans": train_fire_values[train_present],
        "FillBkgndTrans": train_fire_values[train_present]
        }
    update_shape(shape, name, cell_n_v_dictionary)
    #Update Text
    child = shape.find(".//Visio:Shape[@Name='airflow_text_NV02']",ns)
    NV02_text(airflow, child)

def update_shape(shape, child_name, cell_n_v_dictionary):
    child_string = ".//Visio:Shape[@Name='{}']"
    child = shape.find(child_string.format(child_name), ns)
    if ET.iselement(child):
        for n_value, v_value in cell_n_v_dictionary.items():
            babe_string = ".//Visio:Cell[@N='{}']"
            babe = child.find(babe_string.format(n_value),ns)
            if ET.iselement(babe):
                babe.set('V', v_value)
            else:
                ET.SubElement(child,"Cell",N=n_value,V=v_value)

def update_damper(shape, damper_position_dict):
    SegID = int(shape.find(".//Visio:Row[@N='Damper_Segment']/Visio:Cell", ns).get("V", default=-1)) 
    status = damper_position_dict.get(SegID)
    if status is None:
        status = "STATUS?"
    shape_text = shape.find(".//Visio:Shape[@Name='NV01_Damper_Position']",ns)
    shape_text = NV02_text(status, shape_text)
    shape_child = shape.find(".//Visio:Shape[@Name='Damper_Closed_Lines']", ns)
    line_shapes = shape_child.findall(".//Visio:Shape",ns)
    damper_settings = NV_settings.damper_settings.get(status)
    for line_shape in line_shapes:
        line_shape = update_shape_NV01(line_shape,damper_settings)

def update_fan(shape, form5_fan_data, simtime, ns):
    seg_id = int(shape.find(".//Visio:Row[@N='Fan_Segment']/Visio:Cell", ns).get("V",default=-1)) 
    # Determine appropriate settings for seg_id: On, Off, or unknown
    if form5_fan_data is None:
        fan_status = "unknown"
        fan_direction = 1
    elif seg_id in form5_fan_data.index:
        fan_on = float(form5_fan_data.at[seg_id,"fan_on"])
        fan_off = float(form5_fan_data.at[seg_id,"fan_off"])
        if fan_on < simtime < fan_off:
            fan_status = "on"
        else:
            fan_status = "off"
        if fan_status == "on":
            fan_direction = int(form5_fan_data.at[seg_id,"fan_direction"])
        else:
            fan_direction = "fan_arrow_off"
    else:
        fan_status = "unknown"
        fan_direction = 1
    # Modify Fan_Blades for fan_status
    fan_settings = NV_settings.fan_settings.get(fan_status)
    shape_child = shape.find(".//Visio:Shape[@Name='Fan_Blades']", ns)
    shape_toddlers = shape_child.findall(".//Visio:Shape",ns)
    for shape_toddler in shape_toddlers:
        shape_toddler = update_shape_NV01(shape_toddler,fan_settings)
    # Modify Fan_center_line for fan direction
    fan_settings = NV_settings.fan_settings.get(fan_direction)
    shape_child = shape.find(".//Visio:Shape[@Name='Fan_center_line']", ns)
    shape_child = update_shape_NV01(shape_child,fan_settings)

def update_jet_fan(shape, jet_fan_data, simtime, ns):
    seg_id = int(shape.find(".//Visio:Row[@N='Jet_Fan_Segment']/Visio:Cell", ns).get("V",default=-1))
    jet_fan_direction = 'positive'
    jet_fan_status = "off"
    if jet_fan_data is not None:
        if seg_id in jet_fan_data.index:
            fan_on = float(jet_fan_data.at[seg_id,"jet_fan_on"])
            fan_off = float(jet_fan_data.at[seg_id,"jet_fan_off"])
            if fan_on < simtime < fan_off:
                jet_fan_status = "on"
                velocity_discharge = float(jet_fan_data.at[seg_id,"discharge_velocity"])
                if velocity_discharge < 0:
                    jet_fan_direction = 'negative'
    shape_child = shape.find(".//Visio:Shape[@Name='jet_fan_outter_shell']", ns)
    shape_child = update_shape_NV01(shape_child,NV_settings.jet_fan_power[jet_fan_status])
    if jet_fan_direction == 'positive':
        shape_child = shape.find(".//Visio:Shape[@Name='Arrow_positive']", ns)
        shape_child = update_shape_NV01(shape_child,NV_settings.line_black)
        shape_child = shape.find(".//Visio:Shape[@Name='Arrow_negative']", ns)
        shape_child = update_shape_NV01(shape_child,NV_settings.line_white)
    else:
        shape_child = shape.find(".//Visio:Shape[@Name='Arrow_positive']", ns)
        shape_child = update_shape_NV01(shape_child,NV_settings.line_white)
        shape_child = shape.find(".//Visio:Shape[@Name='Arrow_negative']", ns)
        shape_child = update_shape_NV01(shape_child,NV_settings.line_black)


def update_shape_NV01(shape, settings_dict):
    for key, value in settings_dict.items():
        attribute_n = key[:-2]
        value_setting = key[-1]
        search_string = ''.join([".//Visio:Cell[@N='",attribute_n,"']"])
        if shape.find(search_string,ns) is None:
            attributes={
                'N':attribute_n,
                value_setting : value
            }
            ET.SubElement(shape,"Cell",attrib=attributes)
        else:
            shape.find(search_string,ns).set(value_setting,value)
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
            NO_run.run_msg(gui, msg)         
    try:
        with zipfile.ZipFile(new_visio, "a") as zappend:
            for name, vxml in vxmls.items():
                temp_string = ET.tostring(vxml, encoding="utf-8", xml_declaration=True)
                zappend.writestr(name, temp_string, compress_type=compression)
        NO_run.run_msg(gui,f'Created Visio Diagram {new_visio.name}.')
    except:
        msg = "Error writing " + str(new_visio) + ". Try closing the file and process again."
        NO_run.run_msg(gui, msg)

def convert_visio(new_visio,settings_output,gui):
    try:
        #https://stackoverflow.com/questions/10214003/can-python-win32com-use-visio-or-any-program-without-popping-up-a-gui
        visio = win32com.client.Dispatch("Visio.InvisibleApp")
        doc = visio.Documents.Open(str(new_visio))
        if "visio_2_pdf" in settings_output:
            new_pdf = new_visio.with_suffix('.pdf')
            doc.ExportAsFixedFormat( 1, str(new_pdf), 1, 0)
            NO_run.run_msg(gui,f'Created PDF of {new_visio.name}')
        if ("visio_2_png" in settings_output) or ("visio_2_svg" in settings_output):   
        #Export document as PNG 
            pages = doc.Pages
            for page in pages:
                if len(pages) == 1:
                    new_png = new_visio.with_suffix('.png')
                    new_svg = new_visio.with_suffix('.svg')
                else:
                    new_name = new_visio.stem + '-' + str(page)
                    new_name2 = new_visio.parent/new_name
                    new_png = new_name2.with_suffix('.png')
                    new_svg = new_name2.with_suffix('.svg')             
                if page.Background != -1: #Only print foreground page
                    if "visio_2_png" in settings_output:
                        page.Export(str(new_png))
                    if "visio_2_svg" in settings_output:
                        page.Export(str(new_svg))
            NO_run.run_msg(gui,f'Created png or svg or both of {new_visio.name}') 
        visio.Application.Quit()
    except:
        if visio is not None:
            visio.Application.Quit()
        msg = 'Error creating PDF or PNG for '+ str(new_visio)
        NO_run.run_msg(gui, msg)

def create_visio(settings, data, output_meta_data, gui=""):
    settings["simtime"] = valid_simtime(settings["simtime"], data["SSA"], gui)
    time_4_name = int(settings["simtime"])
    time_suffix = "-" + str(time_4_name) + ".vsdx"
    settings["new_visio"] = NO_run.get_results_path2(settings, output_meta_data, time_suffix)
    msg = "Creating Visio diagram " + settings["new_visio"].name + " for simulation time " + str(settings["simtime"]) + "."
    NO_run.run_msg(gui, msg)
    # Read in VISIO Template and update with SES OUtput
    vxmls = get_visXML(settings["visio_template"])  # gets the pages in the VISIO XML.
    file_stem = output_meta_data['file_path'].stem
    for name, vxml in vxmls.items():
        vxmls[name] = emod_visXML(
            vxmls[name], data, file_stem, settings["simtime"], output_meta_data, gui
        )
    write_visio(vxmls, settings["visio_template"], settings["new_visio"],gui)
    for setting in settings["output"]:
        if "visio_2_" in setting:
            convert_visio(settings["new_visio"],settings["output"],gui)
            break
    if 'visio_open' in settings["output"]:
        try:
            msg = f'Opening {settings["new_visio"].name} in Visio.'
            NO_run.run_msg(gui, msg)
            visio = win32com.client.Dispatch("Visio.Application")
            doc = visio.Documents.Open(str(settings["new_visio"]))
        except:
            if visio is not None:
                visio.Application.Quit()
            msg = 'Error Openning '+ str(settings["new_visio"])
            NO_run.run_msg(gui, msg)

if __name__ == "__main__":
    one_output_file = ['C:/Simulations/Demonstration/SI Samples/siinfern-detailed.out']
    two_output_files = ['C:/Simulations/Demonstration/SI Samples/siinfern-detailed.out', 'C:/Simulations/Demonstration/SI Samples/sinorm-detailed.out']
    many_output_files = ['C:/Simulations/Demonstration/SI Samples\\coolpipe.out', 'C:/Simulations/Demonstration/SI Samples\\siinfern-detailed.out', 'C:/Simulations/Demonstration/SI Samples\\siinfern.out', 'C:/Simulations/Demonstration/SI Samples\\sinorm-detailed.out', 'C:/Simulations/Demonstration/SI Samples\\sinorm.out', 'C:/Simulations/Demonstration/SI Samples\\Test02R01.out', 'C:/Simulations/Demonstration/SI Samples\\Test06.out']
    #If using input file, change 'file_type' value to 'input_file
    two_input_files = ['C:/Simulations/Demonstration/SI Samples/siinfern-detailed.inp', 'C:/Simulations/Demonstration/SI Samples/sinorm-detailed.inp']
    many_input_files = ['C:/Simulations/Demonstration/SI Samples\\coolpipe.inp', 'C:/Simulations/Demonstration/SI Samples\\siinfern-detailed.inp', 'C:/Simulations/Demonstration/SI Samples\\siinfern.inp', 'C:/Simulations/Demonstration/SI Samples\\sinorm-detailed.inp', 'C:/Simulations/Demonstration/SI Samples\\sinorm.inp', 'C:/Simulations/Demonstration/SI Samples\\Test02R01.inp', 'C:/Simulations/Demonstration/SI Samples\\Test06.inp']
    settings = {
        'ses_output_str': one_output_file, 
        'visio_template': 'C:/Simulations/Demonstration/Next Vis Samples1p21.vsdx', 
        'results_folder_str': 'C:/Simulations/1p30 Testing', 
        'simtime': -1, 
        'conversion': '', 
        'control': 'First', 
        'output': ['Excel', 'Visio', '', '', 'Route', '', '', '', ''], 
        'file_type':'', #'input_file', 
        'path_exe': 'C:/Simulations/_Exe/SVSV6_32.exe'}
    NO_run.single_sim(settings)
    print('Finished')
