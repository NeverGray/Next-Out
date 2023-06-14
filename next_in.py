import os
import re
import shutil
from pathlib import Path

import numpy as np
import pandas as pd


class Next_In():
    def __init__(self, next_in_path, save_path, ses_version, iteration_sheet=""):
        # Read in next-in excel to a dataframe
        self.ses_version = ses_version
        self.save_path = save_path
        self.next_in_path = next_in_path
        self.iteration_sheet = iteration_sheet
        self.copy_then_read()
        #Create blank dataframe with 8 columns
        self.input_df = pd.DataFrame()
        for i in range(0,8):
           self.input_df.insert(i,i,np.nan)
        #Create empty list to collect map data 
        self.map_list =[]
        self.create_input_from_next_in()
        
    def create_input_from_next_in(self):
        self.form_01()
        self.form_01_variables()
        self.form_02()
        self.form_03()
        self.form_04()
        self.form_05()
        self.form_06()
        self.form_07()
        self.form_07c()
        self.form_07d()
        self.form_08()
        self.form_09()
        self.form_10()
        self.form_11()
        self.form_12()
        self.form_13()
        self.form_14()
        self.create_base_string()
        if self.iteration_sheet == "":
            self.save_base_file_as_input()
        else:
            self.create_map_df()
            self.iteration()
    
    def copy_then_read(self):
        copy_of_file = shutil.copyfile(self.next_in_path, self.next_in_path.parent/'next-vis.tmp')
        self.next_in = pd.read_excel(copy_of_file, sheet_name=None, na_values='', keep_default_na=False, header=None)
        os.unlink(copy_of_file)

    def read_worksheet(self, name):
        worksheet_df = self.next_in[name]
        worksheet_df.name = name
        return worksheet_df
    
    def rows_to_input_df(self, worksheet_df, start_row, start_column, columns_to_read, number_of_rows=1, column_to_text=0, num_cells_4_text=0):
        end_column = start_column + columns_to_read
        end_row = start_row + number_of_rows
        new_line_number = len(self.input_df)
        if column_to_text == 0:
            if number_of_rows == 1:
                row_list = worksheet_df.iloc[start_row,start_column:end_column].values.tolist()
                for i in range(columns_to_read,8):
                    row_list.append(np.nan)
                self.input_df.loc[len(self.input_df)] = row_list
            else:
                df = worksheet_df.iloc[start_row:end_row,start_column:end_column]
                df.columns = range(df.shape[1])
                if columns_to_read < 8: #If there are less than 8 entries, add blanks
                    for i in range(columns_to_read, 8):
                        df.insert(i,i,np.nan)
                self.input_df = pd.concat([self.input_df, df], ignore_index=True, axis=0)

        #If there is text in the input, use this function
        elif column_to_text > 0 and number_of_rows == 1:
            text_input =  worksheet_df.at[start_row, start_column + column_to_text - 1]
            text_input_list = self.split_text_to_list(text_input, num_cells_4_text)
            if column_to_text == 1: #Text before number values
                row_list_collection = worksheet_df.iloc[start_row:end_row,start_column + 1:end_column].values.tolist()
                text_input_list.extend(row_list_collection[0])
                row_list = text_input_list
            else: # Assume text is at end of line
                row_list_collection = worksheet_df.iloc[start_row:end_row,start_column:start_column + column_to_text -1].values.tolist()
                row_list_collection[0].extend(text_input_list)
                row_list = row_list_collection[0] 
            # Add the list to the dataframe
            data_columns = len(row_list)
            for i in range(data_columns+1,9):
                row_list.extend([np.nan])
            self.input_df.loc[len(self.input_df)] = row_list #Add to last line of inputfile dataframe
        
        #Map values from next-in to input file
        for next_in_row in range(start_row, end_row):
            entry_number = 0
            entry_to_text = column_to_text - 1 
            new_line_number = new_line_number + (next_in_row - start_row)
            for next_in_column in range(start_column, end_column):
                mapping = [worksheet_df.name, start_row, next_in_column, new_line_number, entry_number, 1]
                if entry_number == entry_to_text: #If the entry is text, enter how many entries become text
                    mapping[5] = num_cells_4_text
                    entry_number = entry_number + num_cells_4_text
                else:
                    entry_number +=1
                self.map_list.append(mapping)

 
    def columns_to_row_input(self, worksheet_df, start_row, start_column, rows_to_read, row_to_text=0, num_cells_4_text=0):
        #TODO - Update when for over 8 data points
        #TODO - Speedup when adding an individual row as a list instead of concatting
        end_row = start_row + rows_to_read
        new_line_number = len(self.input_df)
        if row_to_text == 0:
            row_list = worksheet_df.iloc[start_row:end_row,start_column].transpose().values.tolist()
            for i in range(rows_to_read,8):
                row_list.append(np.nan)
            self.input_df.loc[len(self.input_df)] = row_list
        elif row_to_text > 0:
            text_input =  worksheet_df.at[start_row + row_to_text -1, start_column]
            text_input_list = self.split_text_to_list(text_input, num_cells_4_text)
            if row_to_text == 1: #Text before number values
                row_list_collection = worksheet_df.iloc[start_row + 1:end_row,start_column].transpose().values.tolist()
                text_input_list.extend(row_list_collection)
                row_list = text_input_list
            else: #Assum text is at end of line
                row_list_collection = worksheet_df.iloc[start_row:end_row-1,start_column].transpose().values.tolist()
                row_list_collection.extend(text_input_list)
                row_list = row_list_collection
            # Add the list to the dataframe
            data_columns = len(row_list)
            for i in range(data_columns+1,9):
                row_list.extend([np.nan]) 
            self.input_df.loc[len(self.input_df)] = row_list
        #If there is text in the input, use this function

        #Map values from next-in to input file
        entry_number = 0
        entry_to_text = row_to_text - 1 
        for next_in_row in range(start_row, end_row):
            mapping = [worksheet_df.name, next_in_row, start_column, new_line_number, entry_number, 1]
            if entry_number == entry_to_text: #If the entry is text, enter how many entries become text
                mapping[5] = num_cells_4_text
                entry_number = entry_number + num_cells_4_text
            else:
                entry_number +=1
            self.map_list.append(mapping)

    def split_text_to_list(self, text_input, num_cells_4_text):
            text_input_list = []
            for i in range (0, num_cells_4_text*10, 10):
                if type(text_input) is str:
                    text_input_list.append(text_input[i:i+10])
                else: #Incase text_input is empty put in 10 spaces
                    text_input_list.append(' '*10)
            return(text_input_list)
    
    def create_map_df(self):
        self.map_df = pd.DataFrame(self.map_list)
        column_names = ['form name','next-in row','next-in column','input line','input entry','number of entries']
        self.map_df.columns = column_names
        self.map_df.set_index([column_names[0],column_names[1],column_names[2]], inplace = True)

    def form_01(self):
        worksheet_df = self.read_worksheet('F01')
        row = 2
        column = 3
        row_1B = 22
        for i in range (row,row_1B,1):
            self.rows_to_input_df(worksheet_df, i, column, columns_to_read=1, number_of_rows = 1, column_to_text=1, num_cells_4_text=8)
        #Delete empty rows (displayed with 80 spaces) from the bottom of the titles until you find a row with text
        row_is_blank = self.input_df.apply(lambda row: row.str.count(' ').sum() == 80, axis=1)
        found_text = False #Initialy, assume the row is blank and text will not be found
        for i in range(19, 0, -1):
            if not found_text: #Assume you haven't found the bottom line with text yet
                if row_is_blank.iloc[i]:
                    self.input_df.drop(index=i, inplace=True)
                    self.map_list.pop()
                else:
                    found_text = True #You found the bottom line with text. Stop deleting text
        row = row_1B
        rows_to_read_dict ={
            'Form 1B': 3,
            'Form 1C': 8,
            'Form 1D': 7,
            'Form 1E': 8,
            'Form 1F': 8,
            'Form 1G': 8,
            'Form 1H': 5           
        }
        difference_4_ip = ['Form 1D', 'Form 1H']
        for key, value in rows_to_read_dict.items():
            rows_to_read = value
            #IP version has a different in Form 1D and does not use Form 1H
            if self.ses_version == 'SI' or key not in difference_4_ip:
                self.columns_to_row_input(worksheet_df, row, column, rows_to_read)
            elif self.ses_version == 'IP' and key == 'Form 1D': #IF IP and Form 1D
                self.columns_to_row_input(worksheet_df, row, column, rows_to_read)
                last_input = len(self.input_df) - 1
                for si_col in range (6,4,-1):
                    ip_col = si_col + 1
                    self.input_df.iloc[last_input, ip_col] = self.input_df.iloc[last_input, si_col]
                    self.input_df.iloc[last_input, si_col] = 0
            row = row + rows_to_read
    
    #Read in Form 1 variables to create later forms
    def form_01_variables(self):
        worksheet_df = self.read_worksheet('F01')
        column = 3 #This replaces 'column' in the exec function below with the value 3
        variable_row={
            'train_performance_option':25,
            'environmental_control_load':28,
            'line_segments':33,
            'sections':34,
            'vent_sections':35,
            'nodes':15,
            'unsteady_heat_sources':38,
            'environment_control_zones':42,
            'trains_in_operation':44,
            'impulse_fan_types':45,
            'air_curtain_fan_types':64,
            'cooling_pipes':68
        }
        # Create variables from the Variable row aboove.
        for key, value in variable_row.items():
            exec(f'self.{key} = worksheet_df.iloc[{value},column]') 
        self.restart_file_name = worksheet_df.iloc[47,5]

    def form_02(self):
        #Form 2A
        worksheet_df = self.read_worksheet('F02A')
        num_line_sec= self.sections - self.vent_sections #Number of line sections for tunnels
        start_row = 4
        start_column = 1
        columns_to_read = 5
        self.rows_to_input_df(worksheet_df, start_row, start_column, columns_to_read, num_line_sec)
        #Form 2B
        if self.vent_sections > 0:
            worksheet_df = self.read_worksheet('F02B')
            start_row = 4
            start_column = 1
            columns_to_read = 4
            self.rows_to_input_df(worksheet_df, start_row, start_column, columns_to_read, self.vent_sections)

    def form_03(self):
        worksheet_df = self.read_worksheet('F03')
        # Form 3A line - requires extra attention because of text
        row = 4
        while (row < len(worksheet_df)):
            column = 1 #Reset back to the first column 
            if not pd.isna(worksheet_df.iloc[row,column]): #If this is not a NaN value
                #Form 3A Part 1
                columns_to_read = 3
                self.rows_to_input_df(worksheet_df, row, column, columns_to_read, number_of_rows=1, column_to_text=3, num_cells_4_text =6)
                end_column= column + columns_to_read
                #Form 3A Part 2
                column = end_column
                columns_to_read = 5
                self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
                #Form 3B and 3C
                for i in [8,8,7]:
                    column = column + columns_to_read   # Starting point for column
                    columns_to_read = i
                    self.rows_to_input_df(worksheet_df, row, column, columns_to_read)

                #Form 3C Get data to read next information
                number_of_subsegments = worksheet_df.iloc[row, column + 5]
                number_of_heat_sources = worksheet_df.iloc[row, column + 6]  # Number of subsegments

                # Form 3D
                column = column + columns_to_read
                columns_to_read = 6
                #if number_of_heat_sources == 1:
                #    self.rows_to_input_df(worksheet_df, row, column, columns_to_read, number_of_rows=1, column_to_text=6, num_cells_4_text=0)
                if number_of_heat_sources > 0:
                    row_heat_source = row
                    for i in range(0, number_of_heat_sources):
                        row_heat_source = row + i
                        self.rows_to_input_df(worksheet_df, row_heat_source, column, columns_to_read, number_of_rows=1, column_to_text=6, num_cells_4_text=3)
                # Form 3E
                column = column + columns_to_read
                end_subsegment = 0
                number_of_subsegment_entries = 0
                columns_to_read = 5
                while end_subsegment < number_of_subsegments:  # Inner loop.
                    row_2_read = row + number_of_subsegment_entries
                    self.rows_to_input_df(worksheet_df, row_2_read, column, columns_to_read)
                    end_subsegment = worksheet_df.loc[row_2_read, column + 1]
                    number_of_subsegment_entries +=1

                #Form 3F
                if self.environmental_control_load in [1,2]:
                    column = column + columns_to_read
                    columns_to_read = 7
                    self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
                #Determine where to restart from in Form 3A
                number_of_rows_down = max(1,number_of_subsegment_entries, number_of_heat_sources)
                row = row + number_of_rows_down - 1
            row = row + 1 #Added incase the dataframe is larger then the data set.
    
    def form_04(self):
        worksheet_df = self.read_worksheet('F04')
        # Form 3A line - requires extra attention because of text
        row = 4
        for i in range(0, self.unsteady_heat_sources):
            column = 1
            columns_to_read = 3
            self.rows_to_input_df(worksheet_df, row, column, columns_to_read, number_of_rows=1, column_to_text=1, num_cells_4_text =4)
            column = column + columns_to_read
            columns_to_read = 6
            self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
            row +=1

    def form_05(self):
        worksheet_df = self.read_worksheet('F05')
        # Form 3A line - requires extra attention because of text
        row = 4
        while (row < len(worksheet_df)):
            column = 1
            if not pd.isna(worksheet_df.iloc[row,column]): #If value is not blank
                #Form 5A Part 1
                columns_to_read = 3
                self.rows_to_input_df(worksheet_df, row, column, columns_to_read, number_of_rows=1, column_to_text=3, num_cells_4_text =6)
                end_column= column + columns_to_read
                segment_type = worksheet_df.at[row,column+1]
                #Form 5B
                column = end_column
                columns_to_read = 8
                self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
                end_column= column + columns_to_read
                number_of_sub = worksheet_df.at[row,column]
                #Form 5C
                column = end_column
                columns_to_read = 4
                off_set = 4
                if segment_type ==3:
                    self.rows_to_input_df(worksheet_df, row, column + off_set, columns_to_read)
                else:
                    self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
                end_column = column + columns_to_read + off_set
                #Form 5D
                column = end_column
                columns_to_read = 7
                for i in range (0,number_of_sub):             
                    read_row = row + i
                    self.rows_to_input_df(worksheet_df, read_row, column, columns_to_read)
            row = row + max(number_of_sub,1)

    def form_06(self):
        worksheet_df = self.read_worksheet('F06')
        # Form 3A line - requires extra attention because of text
        row = 4
        start_column = 1
        column = start_column
        node_to_column ={ #Column, number of data points
            1:[10,5],
            2:[15,3],
            3:[18,4],
            4:[22,5],
            5:[27,5],
            6:[39,6],
            8:[45,6]
        }
        while (row < len(worksheet_df)):
            if (not pd.isna(worksheet_df.iloc[row,column])):
                column = 1
                columns_to_read = 3
                self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
                aero_type = worksheet_df.iloc[row,column +1]
                thermo_type = worksheet_df.iloc[row,column + 2]
                #Form 6B if necessary
                if thermo_type == 3:
                    column = column + columns_to_read
                    columns_to_read = 6
                    self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
                if aero_type in node_to_column.keys():
                    column = node_to_column[aero_type][0]
                    columns_to_read = node_to_column[aero_type][1]
                    self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
                if thermo_type == 2:
                    column = 32
                    columns_to_read = 38
                    self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
            column = start_column
            row +=1

    def form_07(self):
        worksheet_df = self.read_worksheet('F07')
        # Form 3A line - requires extra attention because of text
        row = 4
        column = 1
        while (row < len(worksheet_df)):
            if not pd.isna(worksheet_df.iloc[row,column]):
                column = 1
                columns_to_read = 5
                self.rows_to_input_df(worksheet_df, row, column, columns_to_read, number_of_rows=1, column_to_text=1, num_cells_4_text =4)
                for i in [8,8]:
                    column = column + columns_to_read   # Starting point for column
                    columns_to_read = i
                    self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
            row +=1
    
    def form_07c(self):
        worksheet_df = self.read_worksheet('F07C')
        row = 4
        column = 1
        while (row < len(worksheet_df)):
            if not pd.isna(worksheet_df.iloc[row,column]):
                column = 1
                columns_to_read = 7
                self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
            row +=1
    
    def form_07d(self):
        worksheet_df = self.read_worksheet('F07D')
        row = 4
        column = 1
        while (row < len(worksheet_df)):
            if not pd.isna(worksheet_df.iloc[row,column]):
                column = 1
                columns_to_read = 8
                self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
            row +=1

    def form_08(self):
        if self.train_performance_option >0 :
            F08A_df = self.read_worksheet('F08A')
            row_8A = 4
            col_8A = 1
            row_8B = 3
            col_8B = 1
            row_8C = 4
            col_8C = 1
            row_8D = 6
            col_8D = 1
            row_8E = 5
            col_8E = 1
            row_8F = 4
            col_8F = 3
            while (row_8A < len(F08A_df)):
                if (not pd.isna(F08A_df.iloc[row_8A,col_8A])):
                    column = col_8A
                    columns_to_read = 1
                    self.rows_to_input_df(F08A_df, row_8A, column, columns_to_read, number_of_rows=1, column_to_text=1, num_cells_4_text =7)
                    column = column + columns_to_read
                    columns_to_read = 7
                    self.rows_to_input_df(F08A_df, row_8A, column, columns_to_read)
                    groups_of_trains = F08A_df.iloc[row_8A, column + 1] 
                    track_sections = F08A_df.iloc[row_8A, column + 2]
                    #Form 8B
                    columns_to_read = 3
                    if groups_of_trains > 1:
                        worksheet_df = self.read_worksheet('F08B')
                        self.rows_to_input_df(worksheet_df, row_8B, col_8B, columns_to_read, number_of_rows=groups_of_trains-1)
                    col_8B = col_8B + columns_to_read
                    #form 8C
                    columns_to_read = 8 
                    if self.train_performance_option in [1,2]:
                       worksheet_df = self.read_worksheet('F08C')   
                       self.rows_to_input_df(worksheet_df, row_8C, col_8C, columns_to_read, number_of_rows=track_sections) 
                    col_8C = col_8C + columns_to_read  
                    #form 8D
                    if self.train_performance_option == 1:
                        row_first = 1
                        rows_to_read = 2
                        worksheet_df = self.read_worksheet('F08D')
                        self.columns_to_row_input(worksheet_df, row_first, col_8D + 2, rows_to_read)
                        scheduled_stops = worksheet_df.iloc[row_first,col_8D + 2]
                        columns_to_read = 3
                        if scheduled_stops > 0:
                            self.rows_to_input_df(worksheet_df, row_8D, col_8D, columns_to_read, number_of_rows=scheduled_stops)
                        col_8D = col_8D + columns_to_read
                    #form 8E
                    if self.train_performance_option in [2,3]:
                        row_first = 1
                        columns_to_read = 1
                        worksheet_df = self.read_worksheet('F08E')
                        self.rows_to_input_df(worksheet_df, row_first, col_8E + 4, columns_to_read)
                        speed_time_points = int(worksheet_df.iloc[row_first,col_8E + 4])
                        #Read speed profile points
                        columns_to_read = 5
                        if speed_time_points > 0:
                            self.rows_to_input_df(worksheet_df, row_8E, col_8E, columns_to_read, number_of_rows = speed_time_points)
                        col_8E = col_8E + 5
                    #Form 8F
                    row_first = 1
                    rows_to_read = 2
                    worksheet_df = self.read_worksheet('F08F')
                    self.columns_to_row_input(worksheet_df, row_first, col_8F, rows_to_read)
                    number_of_sections = int(worksheet_df.iloc[row_first, col_8F])
                    columns_to_read = 1
                    self.rows_to_input_df(worksheet_df, row_8F, col_8F, columns_to_read, number_of_rows=number_of_sections)
                    col_8F = col_8F + 3
                row_8A +=1
                
    def form_09(self):
        if self.train_performance_option > 0:
            worksheet_df = self.read_worksheet('F09')
            row = 2
            col = 5
            row_form9I = 86
            row_form9J = 91
            row_form9K = 96
            onboard_flywheel = 1
            #Form 9A
            while (col < len(worksheet_df.columns)):
                if not pd.isna(worksheet_df.iloc[row,col]):
                    rows_to_read = 5
                    self.columns_to_row_input(worksheet_df, row, col, rows_to_read, row_to_text=1, num_cells_4_text=4)
                    row += rows_to_read
                    #Form 9B, C, D, E
                    for rows_to_read in [5,6,8,8,6]:
                        self.columns_to_row_input(worksheet_df, row, col, rows_to_read)
                        row += rows_to_read
                    #Form 9F Line 1
                    if self.train_performance_option != 3:
                        rows_to_read = 3
                        self.columns_to_row_input(worksheet_df, row, col, rows_to_read, row_to_text=1, num_cells_4_text=4)    
                        row += rows_to_read
                        #Form 9F Line 2, G lines 1, 2, and 3
                        for rows_to_read in [5,4,4,4]:
                            self.columns_to_row_input(worksheet_df, row, col, rows_to_read)
                            row += rows_to_read
                        #Form 9G, last line (4)
                        rows_to_read = 1
                        self.columns_to_row_input(worksheet_df, row, col, rows_to_read)
                        train_controller = worksheet_df.iloc[row,col]
                        row += rows_to_read
                        #Form 9H
                        if train_controller == 2: 
                            for rows_to_read in [5,5]:
                                self.columns_to_row_input(worksheet_df, row, col, rows_to_read)
                                row += rows_to_read
                            onboard_flywheel = worksheet_df.iloc[row-1,col]   
                        elif  train_controller == 3:
                            row += 10 #move to form 9H-A
                            for rows_to_read in [5,5,5]:
                                self.columns_to_row_input(worksheet_df, row, col, rows_to_read)
                                row += rows_to_read
                        #Form 9I
                        row = row_form9I
                        rows_to_read = 5
                        self.columns_to_row_input(worksheet_df, row, col, rows_to_read)
                        #Form 9J
                        if self.train_performance_option == 1:
                            row = row_form9J
                            rows_to_read = 5
                            self.columns_to_row_input(worksheet_df, row, col, rows_to_read)
                        #Form 9K
                        if onboard_flywheel == 2:
                            row = row_form9K
                            for rows_to_read in [5,7]:
                                self.columns_to_row_input(worksheet_df, row, col, rows_to_read)
                                row += rows_to_read
                row = 2
                col += 1

    def form_10(self):
        worksheet_df = self.read_worksheet('F10')
        # Form 3A line - requires extra attention because of text
        row = 4
        column = 1
        while (row < len(worksheet_df)):
            if not pd.isna(worksheet_df.iloc[row,column]):
                column = 1
                columns_to_read = 8
                self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
            row +=1

    def form_11(self):
        row_F11A = 4
        col_F11A = 1
        row_F11B_start = 2
        col_F11B = 1
        worksheet_df_f11A = self.read_worksheet('F11A')
        worksheet_df_f11B = self.read_worksheet('F11B')
        while (row_F11A < len(worksheet_df_f11A)):
            if not pd.isna(worksheet_df_f11A.iloc[row_F11A,col_F11A]):
                columns_to_read = 6
                self.rows_to_input_df(worksheet_df_f11A,row_F11A,col_F11A,columns_to_read)
                number_sections = worksheet_df_f11A.iloc[row_F11A, col_F11A + 1]
                read_sections = 0
                row_F11B = row_F11B_start
                if self.environment_control_zones > 1:
                    while(read_sections < number_sections):
                        if number_sections - read_sections > 8:
                            i = 8
                        else:
                            i = number_sections - read_sections
                        self.columns_to_row_input(worksheet_df_f11B,row_F11B,col_F11B,i)
                        read_sections = read_sections + i
                        row_F11B += i
                    col_F11B = col_F11B + 1
            row_F11A = row_F11A + 1

    def form_12(self):
        worksheet_df = self.read_worksheet('F12')
        self.columns_to_row_input(worksheet_df,1,3,2)
        row = 4
        column = 1
        while (row < len(worksheet_df)):
            if not pd.isna(worksheet_df.iloc[row,column]):
                column = 1
                columns_to_read = 7
                self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
            row +=1

    def form_13(self):
        worksheet_df = self.read_worksheet('F13')
        row = 3
        column = 1     
        columns_to_read = 4
        while (row < len(worksheet_df)):
            if not pd.isna(worksheet_df.iloc[row,column]):
                self.rows_to_input_df(worksheet_df, row, column, columns_to_read)
            row +=1

    def form_14(self):
        if self.cooling_pipes > 0:
            worksheet_df = self.read_worksheet('F14AB')
            worksheet_df2 = self.read_worksheet('F14C')
            #TODO Eventually put the vertical elements to horiztonal
            row_14AB = 3
            col_14AB = 1
            row_14C =  3
            col_14C = 1    
            while (row_14AB < len(worksheet_df)):
                col_14AB = 1
                if not pd.isna(worksheet_df.iloc[row_14AB,col_14AB]):
                    #Form 14A
                    columns_to_read = 1 #Cooling Pipe Description
                    self.rows_to_input_df(worksheet_df, row_14AB, col_14AB, columns_to_read, number_of_rows =1, column_to_text = 1, num_cells_4_text=8)
                    col_14AB +=columns_to_read
                    columns_to_read = 7
                    self.rows_to_input_df(worksheet_df, row_14AB, col_14AB, columns_to_read)
                    # Form 14B
                    inlets = worksheet_df.iloc[row_14AB,col_14AB]
                    sections = worksheet_df.iloc[row_14AB,col_14AB+1]
                    col_14AB +=columns_to_read
                    columns_to_read= 3
                    if inlets > 0:
                        for i in range(0, inlets):
                            self.rows_to_input_df(worksheet_df, row_14AB, col_14AB, columns_to_read)
                            row_14AB +=1
                    else:
                        row_14AB +=1 #To prevent a value of zero from creating an infinte loop
                    #Form 14C
                    if not pd.isna(worksheet_df2.iloc[row_14C,col_14C]):
                        columns_to_read = 1
                        start_row = row_14C
                        end_row = start_row + sections
                        start_column = col_14C
                        end_column = start_column + columns_to_read
                        df = worksheet_df2.iloc[start_row:end_row, start_column:end_column]
                        df.columns = range(df.shape[1])
                        df[0] = df[0].apply(lambda x: '+' + str(x) + '.' if x > 0 else x)
                        if columns_to_read < 8: #If there are less than 8 entries, add blanks
                            for i in range(columns_to_read, 8):
                                df.insert(i,i,np.nan)
                        #Add the new line to the input dataframe
                        self.input_df = pd.concat([self.input_df, df], ignore_index=True, axis=0)
                        col_14C +=1

    def create_base_string(self):
        self.base_string = ''
        for _, row in self.input_df.iterrows():
            line = ''
            for col in row:
                line += self.format_entry(col)
            self.base_string += line.rstrip() + '\n'

    def format_entry(self, col):
        formated_entry = ''
        if str(col) == 'nan': 
            formated_entry = ''.ljust(10)
        elif type(col) is int:
            if abs(col)> 99999999 or (abs(col) < 0.00001 and col !=0):
                value = '{:.3E}'.format(col)
                formated_entry= str(value).ljust(10)
            else:
                col = str(col)+'.'
                formated_entry= col.ljust(10)
        elif type(col) is float:
            if col == 0:
                value = "0."
            elif abs(col)> 99999999 or (abs(col) < 0.00001):
                value = '{:.3E}'.format(col)
            elif col == int(col): #If the value can be represented by an integer
                value = "{:.0f}".format(col) + '.'
            else:
                value = col
            formated_entry= str(value).ljust(10)
        else: #line is a string and needs additional spaces
            formated_entry= col.ljust(10)
        return formated_entry
    
    #Used to save base file as input
    def save_base_file_as_input(self):
        base_file_name = self.next_in_path.with_suffix(".inp")  
        with open(base_file_name, 'w') as f:
            f.write(self.base_string)

    #Used if trouble shooting is needed between file creation and formatting
    def save_unformatted_input_file(self):
        input_string = self.input_df.to_string(index=False, header=False, col_space=10, justify='left',  na_rep='')
        input_path_df_to_text = self.save_path.with_suffix(".txt")         
        with open(input_path_df_to_text,'w') as f:
            f.write(input_string)

    def iteration(self):
        #Read in the iteration input data into a data frame
        worksheet_df = self.read_worksheet(self.iteration_sheet)
        start_row = 5
        #Set the row limit to the last row with a valid file name
        row_limit = worksheet_df.iloc[:,1].last_valid_index()
        #Set the column limit to the row before the word Output
        output_column = worksheet_df.iloc[1].eq('Output').idxmax()
        end_input_column = output_column - 1
        self.iteration_input = worksheet_df.iloc[start_row:row_limit,0:end_input_column]
        #Setup the titles for the interation input data frame
        column_titles = worksheet_df.iloc[2,0:end_input_column]
        column_titles[0] = "Number"
        column_titles[1] = "File Name"
        self.iteration_input.columns = column_titles
         #Set up iteration output worksheet
        column_limit = worksheet_df.iloc[3].last_valid_index()
        self.iteration_output = worksheet_df.iloc[start_row:row_limit,output_column:column_limit]
        column_titles = worksheet_df.iloc[3,output_column:column_limit]
        self.iteration_output.columns = column_titles
        self.iteration_output.name = output_column
        #Create dictionary of mappting information for columns in iterations input data
        map_dictionary = {}
        input_paths_list = []
        for column in self.iteration_input.columns:
            if not pd.isna(column): #If there is a value of some kind, check for an equal sign
                if column[0] == '=':
                    form_name = column.split('\'')[1]
                    excel_rc = column.split('!')[1].replace('$','')
                    excel_column_letters = re.findall(r'[A-Za-z]', excel_rc)[0]
                    excel_row = re.findall(r'\d', excel_rc)[0]
                    map_row = int(excel_row) -1
                    # Calculate the column number when there are multiple letters, such as 'AA'
                    letter_number = 0
                    letter_multiplier = 1
                    for char in reversed(excel_column_letters):
                        letter_number += (ord(char.upper()) - ord('@')) * letter_multiplier
                        letter_multiplier = letter_multiplier * 26
                    map_column = letter_number - 1
                    map_dictionary[column] = self.map_df.loc[form_name,map_row,map_column].values.tolist()[0]
        #Create input files. Split the base_string into lines
        modified_lines = self.base_string.splitlines()
        for _, row in self.iteration_input.iterrows():
            # For each column, modify the appropriate line
            for key, map_location in map_dictionary.items():
                new_value = self.format_entry(row[key])
                line_number = map_location[0]
                entry_start = map_location[1] * 10
                entry_end = entry_start + (map_location[2]) * 10
                modified_lines_list = list(modified_lines[line_number])
                modified_lines_list[entry_start:entry_end] = new_value
                #TODO NEXT Modify then replace the line. Then combine back to create a base and save
                modified_lines[line_number] = "".join(modified_lines_list)
            #Join the lines back to a single, modified string
            modified_string = "\n".join(modified_lines)
            input_file_name = row['File Name'] + '.inp'
            save_name = self.save_path / input_file_name
            self.save_string_as_input(modified_string, save_name)
            input_paths_list.append(save_name)

    def save_string_as_input(self, string, save_name):
        with open(save_name, 'w') as f:
            f.write(string)

if __name__ == "__main__":
    #TODO - How to determine version of Input File? (SI or IP)
    directory_string = "C:\\Users\\msn\\OneDrive - Never Gray\\Software Development\\Next-Vis\\_Tasks\\Next-Sim Update\\Iterations\\"
    directory_string_IP = "C:\\Users\\msn\\OneDrive - Never Gray\\Software Development\\Next-Vis\\_Tasks\\Next-Sim Update\\InputTesting for IP\\"
    next_in_file_names = [
        'Test01.xlsm',
        'Test02R01.xlsm',
        'Test03.xlsm',
        'Test04.xlsm',
        'Test05.xlsm',
        'Test06.xlsm',
        'Test07.xlsm',
        'Test08.xlsm'
    ]
    next_in_file_names_IP = [
        'inferno-detailed.xlsm',
        'normal-detailed.xlsm',
        'TestIP01.xlsm',
        'TestIP02.xlsm',
        'TestIP03R01.xlsm',
        'TestIP04.xlsm',
        'TestIP05R01.xlsm',
        'TestIP06.xlsm'
    ]
    file_name = 'Next Iteration Sheet Rev07.xlsx'
    #for file_name in next_in_file_names_IP:
    path_string = directory_string + file_name
    next_in_path = Path(path_string)
    save_path = Path(directory_string)
    print(f'Reading file from Excel File {file_name}.')
    next_in = Next_In(next_in_path, save_path, ses_version='SI')
    print(f'Wrote {save_path.name}.')