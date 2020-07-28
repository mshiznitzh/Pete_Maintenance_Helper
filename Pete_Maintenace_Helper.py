#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "MiKe Howard"
__version__ = "0.1.0"
__license__ = "MIT"


import logging
from logzero import logger
from taskw import TaskWarrior
import pandas as pd
import glob
import os
import datetime as DT
import xlsxwriter
from typing import Optional
from xlsxwriter.worksheet import (
    Worksheet, cell_number_tuple, cell_string_tuple)
import multiprocessing



#from xlsxwriter.utility import xl_rowcol_to_cell
from dateutil.tz import tzutc
import numpy as np


#OS Functions
def filesearch(word=""):
    """Returns a list with all files with the word/extension in it"""
    logger.info('Starting filesearch')
    file = []
    for f in glob.glob("*"):
        if word[0] == ".":
            if f.endswith(word):
                file.append(f)

        elif word in f:
            file.append(f)
            #return file
    logger.debug(file)
    return file

def Change_Working_Path(path):
    # Check if New path exists
    if os.path.exists(path):
        # Change the current working Directory
        try:
            os.chdir(path)  # Change the working directory
        except OSError:
            logger.error("Can't change the Current Working Directory", exc_info = True)
    else:
        print("Can't change the Current Working Directory because this path doesn't exits")

#Pandas Functions
def Excel_to_Pandas(filename):
    logger.info('importing file ' + filename)
    df=[]
    try:
        df = pd.read_excel(filename)
    except:
        logger.error("Error importing file " + filename, exc_info=True)

    df=Cleanup_Dataframe(df)
    logger.debug(df.info(verbose=True))
    return df

def Cleanup_Dataframe(df):
    logger.info('Starting Cleanup_Dataframe')
    logger.debug(df.info(verbose=True))
    # Remove whitespace on both ends of column headers
    df.columns = df.columns.str.strip()

    # Replace whitespace in column header with _
    df.columns = df.columns.str.replace(' ', '_')

    return df


def Create_tasks_for_Precon_meetings(myprojects, schedule):
# This filters Pre construnction meeting in the future of Released projects
    precons_df=schedule[(schedule['Activity_Description'] == 'Pre-Construction Meeting') &
             (schedule['Schedule_Status'] == 'Active') &
             (schedule['Percent_Complete'] <= 100 ) &
             (schedule['Planned_Finish'] >= DT.datetime.now()) &
             (schedule['Project_Status'] == 'Released' )]

    outputdf = precons_df[precons_df.Project_ID.isin(list(myprojects.PETE_ID))]


    for index, row in outputdf.iterrows():

        description = 'Check if I have an invite to ' + row['Activity_Description']
        project = str(row['Project_ID']) + ':' + row['Name']
        duedate = row['Planned_Finish'] - DT.timedelta(days=7)

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')
        #p.start()
    # p.join()

def Create_tasks_for_Waterfalls(myprojects, scheduledf):
    # This filters Waterfall schedules that are in draft of Released projects
    Draft_Waterfalls=scheduledf[(scheduledf['Activity_Description'] == 'Waterfall Start') &
                             (scheduledf['Schedule_Status'] == 'Draft') &
                            (scheduledf['Project_Status'] == 'Released') &
                                pd.notnull(scheduledf['Planned_Construction_Ready'])]

    outputdf = Draft_Waterfalls[Draft_Waterfalls.Project_ID.isin(list(myprojects.PETE_ID))]


    for index, row in outputdf.iterrows():

        description = 'Waterfall needs to baselined'
        project = str(row['Project_ID']) + ':' + row['Name']
        duedate = DT.datetime.today()

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')
        #p.start()
    #p.join()
    

def Create_task_for_Final_Engineering_with_draft_schedules(myprojects, scheduledf):
    # This filters Waterfall schedules that are in draft of Released projects

    filterdf=scheduledf[(scheduledf['Activity_Description'] == 'Final Engineering') &
                        (scheduledf['Schedule_Status'] == 'Draft') &
                        (scheduledf['Project_Status'] == 'Released')]

    outputdf = filterdf[filterdf.Project_ID.isin(list(myprojects.PETE_ID))]

    for index, row in outputdf.iterrows():

        description = 'Check with Engineering on when a schedule will be finalized'
        project = str(row['Project_ID']) + ':' + row['Name']
        duedate = DT.datetime.today()

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')
        #p.start()
    #p.join()

def Create_task_for_Released_projects_missing_Construnction_Ready_Date(myprojects, scheduledf):
    # This filters Waterfall schedules that are in draft of Released projects

    filterdf = scheduledf[(scheduledf['Activity_Description'] == 'Waterfall Start') &
                            (scheduledf['Project_Status'] == 'Released') &
                                pd.isnull(scheduledf['Planned_Construction_Ready'])]

    outputdf = filterdf[filterdf.Project_ID.isin(list(myprojects.PETE_ID))]

    for index, row in outputdf.iterrows():

        description = 'Check with Engineering on populating the construction ready date'
        project = str(row['Project_ID']) + ':' + row['Name']
        duedate = DT.datetime.today()+DT.timedelta(days=5)

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')
        #p.start()
    #p.join()

def Create_task_for_ESID_before_Energiztion(myprojects, scheduledf):
    #

    filterdf = scheduledf[(scheduledf['Activity_Description'] == 'Project Energization') &
                          (scheduledf['Estimated_In-Service_Date'] < scheduledf['Planned_Finish'])]

    outputdf = filterdf[filterdf.Project_ID.isin(list(myprojects.PETE_ID))]

    for index, row in outputdf.iterrows():

        description = 'Project Energization is after Estimated In-Service Date'
        project = str(row['Project_ID']) + ':' + row['Name']
        duedate = DT.datetime.today() + DT.timedelta(days=5)

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')


def Create_task_for_Electrical_Prints_Start(myprojects, scheduledf):
    filterdf = scheduledf[(scheduledf['Activity_Description'] == 'Electrical Design') &
                              (scheduledf['Planned_Start'] + (scheduledf['Planned_Finish'] - scheduledf['Planned_Start'])/2 <= DT.datetime.today() )  &
                              (pd.isnull(scheduledf['Actual_Start'])) &
                              (scheduledf['Planned_Finish'] >= DT.datetime.today())]
    outputdf = filterdf[filterdf.Project_ID.isin(list(myprojects.PETE_ID))]
    for index, row in outputdf.iterrows():

        description = 'Check with Engineering on if Electrical Designs were started'
        project = str(row['Project_ID']) + ':' + row['Name']
        duedate = DT.datetime.today()

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')


def Create_task_for_Electrical_Prints(scheduledf):

    # This filters Prints with finished dates past 5 days past today without an actual finish

    filterdf = scheduledf[(scheduledf['Activity_Description'] == 'Electrical Design') &
                          (scheduledf['Planned_Finish'] <= DT.datetime.today() - DT.timedelta(days=5) ) &
                          (pd.isnull(scheduledf['Actual_Finish']))]
    outputdf=filterdf
    for index, row in outputdf.iterrows():

        description = 'Check with Engineering on when Electrical Designs will be issued'
        project = str(row['Project_ID']) + ':' + row['Name']
        duedate = DT.datetime.today()

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')



        #p.start()
    #p.join()

def Create_task_for_Relay_Settings(scheduledf):
    # This filters Prints with finished dates past 5 days past today without an actual finish

    filterdf = scheduledf[(scheduledf['Activity_Description'] == 'Create Relay Settings') &
                          (scheduledf['Planned_Finish'] <= DT.datetime.today() + DT.timedelta(days=5)) &
                          (pd.isnull(scheduledf['Actual_Finish']))]
    outputdf = filterdf
    for index, row in outputdf.iterrows():

        description = 'Check with Relay Setter on when settings are going to be issued'
        project = str(row['Project_ID']) + ':' + row['Name']
        duedate = DT.datetime.today() + DT.timedelta(hours=8)

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')

        filterdf = scheduledf[(scheduledf['Activity_Description'] == 'Create Relay Settings') &
                              (scheduledf['Planned_Start'] + (scheduledf['Planned_Finish'] - scheduledf[
                                  'Planned_Start']) / 2 <= DT.datetime.today()) &
                              (pd.isnull(scheduledf['Actual_Start'])) &
                              (scheduledf['Planned_Finish'] >= DT.datetime.today())]
        outputdf = filterdf
        for index, row in outputdf.iterrows():

            description = 'Check with with Relay Setter on when settings are going to be started'
            project = str(row['Project_ID']) + ':' + row['Name']
            duedate = DT.datetime.today() + DT.timedelta(hours=8)

            if row['Project_Tier'] == 1.0:
                priority = 'H'

            elif row['Project_Tier'] == 2.0:
                priority = 'M'

            elif row['Project_Tier'] == 3.0:
                priority = 'L'

            else:
                priority = None

            Add_Task(description, project, duedate, priority, 'PMH')


#def Project_Start_60_Days_Out_No_Outages
#def Check_Estimated_In_Service_Date():
#def Construction_Ready_Date():
#def Check_Program_Manager_Resource():
#def Check_Construction_Manager_Resource():
#def Check_WaterFall_Draft_State():
#def Check_Start_Date_Relay_Settings():


def Genrate_Physical_Prints_Report(scheduledf):
    writer = pd.ExcelWriter('Metro West Physical Prints Report.xlsx', engine='xlsxwriter')

    scheduledf = scheduledf[scheduledf['Region'] == 'METRO WEST']

    for district in np.sort(scheduledf.Work_Center.dropna().unique()):

        Energization_df = scheduledf[(scheduledf['Activity_Description'] == 'Project Energization') &
                                     (scheduledf['Schedule_Status'] == 'Active') &
                                     (scheduledf['Project_Status'] == 'Released') &
                                     (scheduledf['Work_Center'] == district)]


        P_design = scheduledf[(scheduledf['Activity_Description'] == 'Physical Design') &
                                           (scheduledf['Schedule_Status'] == 'Active') &
                                           (scheduledf['Project_Status'] == 'Released') &
                                           (scheduledf['Work_Center'] == district)]

        Energization_df=Energization_df.assign(Project_Energization = Energization_df['Planned_Start'])
        dates = Energization_df[['Project_Energization', 'Project_ID']]
        P_design = pd.merge(dates, P_design, on=['Project_ID'], suffixes=('', '_y'), how='right')



        P_design = P_design.assign(Physical_Design_Start=P_design['Planned_Start'])
        P_design = P_design.assign(Physical_Design_Finish=P_design['Planned_Finish'])

        P_design['Project_Name'] = P_design.Name
        P_design['PETE_ID'] = P_design.Project_ID

        P_design.sort_values(by=['Project_Energization', 'Estimated_In-Service_Date'], inplace=True)
        P_design.set_index('Project_ID')
       # P_design['Estimated_In-Service_Date'] = P_design['Estimated_In-Service_Date'].dt.date
        P_design['Physical_Design_Start'] = P_design['Physical_Design_Start'].dt.date
        P_design['Physical_Design_Finish'] = P_design['Physical_Design_Finish'].dt.date
        P_design['Planned_Finish'] = P_design['Planned_Finish'].dt.date
     #   P_design['Actual_Finish'] = P_design['Actual_Finish'].dt.date
        P_design['Project_Energization'] = P_design['Project_Energization'].dt.date


        P_design['Physical_Design_Start'] = P_design['Physical_Design_Start'].dropna().astype(str)
        P_design['Physical_Design_Finish'] = P_design['Physical_Design_Finish'].dropna().astype(str)
        P_design['Project_Energization'] = P_design['Project_Energization'].dropna().astype(str)
        P_design['Estimated_In-Service_Date'] = P_design['Estimated_In-Service_Date'].dropna().astype(str)

        P_design.loc[pd.notnull(P_design.Actual_Start), 'Physical_Design_Start'] = 'Started'
        P_design.loc[pd.notnull(P_design.Actual_Finish), 'Physical_Design_Finish'] = 'Finished'

        P_design = P_design[list(('PETE_ID',
                                  'Project_Name',
                                  'Physical_Design_Start',
                                  'Physical_Design_Finish',
                                  'Comments',
                                  'Project_Energization',
                                  'Estimated_In-Service_Date',
                                  ))]

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # Save the unformatted results
        P_design.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
        P_design.to_excel(writer, index=False, sheet_name=district)

        # Get workbook
        workbook = writer.book
        worksheet = writer.sheets[district]

        # There is a better way to so this but I am ready to move on
        #note that PETE ID is diffrent from the ID used to take you to a website page
        #x=0
        #for row in filterdf.iterrows():
         #   worksheet.write_url('A' + str(2+x),
          #                  'https://pete.corp.oncor.com/pete.web/project-details/' + str(filterdf['Project_ID'].values[x] + 24907),
           #                 string=str('%05.0f' % filterdf['Project_ID'].values[x]))  # Implicit format
           # x=x+1

        cell_format = workbook.add_format()
        cell_format.set_align('center')
        worksheet.set_column('A:I', None, cell_format)



        for x  in range(9):
            set_column_autowidth(worksheet, x)

    writer.save()
    writer.close()

def Genrate_Electrical_Prints_Report(scheduledf):
    writer = pd.ExcelWriter('Metro West Electrical Prints Report.xlsx', engine='xlsxwriter')

    scheduledf = scheduledf[scheduledf['Region'] == 'METRO WEST']

    for district in np.sort(scheduledf.Work_Center.dropna().unique()):
        Energization_df = scheduledf[(scheduledf['Activity_Description'] == 'Project Energization') &
                                     (scheduledf['Schedule_Status'] == 'Active') &
                                     (scheduledf['Project_Status'] == 'Released') &
                                     (scheduledf['Work_Center'] == district)]

        E_design = scheduledf[(scheduledf['Activity_Description'] == 'Electrical Design') &
                                           (scheduledf['Schedule_Status'] == 'Active') &
                                           (scheduledf['Project_Status'] == 'Released') &
                                           (scheduledf['Work_Center'] == district)]

        E_design = E_design.assign(Electrical_Design_Start=E_design['Planned_Start'])
        E_design = E_design.assign(Electrical_Design_Finish=E_design['Planned_Finish'])

        Energization_df=Energization_df.assign(Project_Energization = Energization_df['Planned_Start'])
        dates = Energization_df[['Project_Energization', 'Project_ID']]
        E_design = pd.merge(dates, E_design, on=['Project_ID'], suffixes=('', '_y'), how='right')

        E_design['Project_Name'] = E_design.Name
        E_design['PETE_ID'] = E_design.Project_ID



        E_design.sort_values(by=['Project_Energization', 'Estimated_In-Service_Date'], inplace=True)
        E_design.set_index('PETE_ID')
        E_design['Estimated_In-Service_Date'] = E_design['Estimated_In-Service_Date'].dt.date
        E_design['Electrical_Design_Start'] = E_design['Electrical_Design_Start'].dt.date
        E_design['Electrical_Design_Finish'] = E_design['Electrical_Design_Finish'].dt.date
        E_design['Planned_Finish'] = E_design['Planned_Finish'].dt.date
       # E_design['Actual_Finish'] = E_design['Actual_Finish'].dt.date
        E_design['Project_Energization'] = E_design['Project_Energization'].dt.date


        E_design['Electrical_Design_Start'] = E_design['Electrical_Design_Start'].dropna().astype(str)
        E_design['Electrical_Design_Finish'] = E_design['Electrical_Design_Finish'].dropna().astype(str)
        E_design['Project_Energization'] = E_design['Project_Energization'].dropna().astype(str)
        E_design['Estimated_In-Service_Date'] = E_design['Estimated_In-Service_Date'].dropna().astype(str)

        E_design.loc[pd.notnull(E_design.Actual_Start), 'Electrical_Design_Start'] = 'Started'
        E_design.loc[pd.notnull(E_design.Actual_Finish), 'Electrical_Design_Finish'] = 'Finished'

        E_design = E_design[list(('PETE_ID',
                                  'Project_Name',
                                  'Electrical_Design_Start',
                                  'Electrical_Design_Finish',
                                  'Comments',
                                  'Project_Energization',
                                  'Estimated_In-Service_Date',
                                  ))]

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # Save the unformatted results
        E_design.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
        E_design.to_excel(writer, index=False, sheet_name=district)

        # Get workbook
        workbook = writer.book
        worksheet = writer.sheets[district]

        # There is a better way to so this but I am ready to move on
        #note that PETE ID is diffrent from the ID used to take you to a website page
        #x=0
        #for row in filterdf.iterrows():
         #   worksheet.write_url('A' + str(2+x),
          #                  'https://pete.corp.oncor.com/pete.web/project-details/' + str(filterdf['Project_ID'].values[x] + 24907),
           #                 string=str('%05.0f' % filterdf['Project_ID'].values[x]))  # Implicit format
           # x=x+1

        cell_format = workbook.add_format()
        cell_format.set_align('center')
        worksheet.set_column('A:I', None, cell_format)



        for x  in range(9):
            set_column_autowidth(worksheet, x)

    writer.save()
    writer.close()

def Genrate_Relay_Settings_Report(scheduledf):
    writer = pd.ExcelWriter('Metro West Relay Settings Report.xlsx', engine='xlsxwriter')

    scheduledf = scheduledf[scheduledf['Region'] == 'METRO WEST']

    for district in np.sort(scheduledf.Work_Center.dropna().unique()):

        filterdf = scheduledf[(scheduledf['Activity_Description'] == 'Create Relay Settings') &
                              #(pd.notnull(scheduledf['Planned_Start'])) &
                              (scheduledf['Schedule_Status'] == 'Active') &
                              (scheduledf['Project_Status'] == 'Released') &
                               (scheduledf['Work_Center'] == district)]

        Protection_Control_df = scheduledf[(scheduledf['Activity_Description'] == 'Protection and Control') &
                              (scheduledf['Schedule_Status'] == 'Active') &
                              (scheduledf['Project_Status'] == 'Released') &
                              (scheduledf['Work_Center'] == district)]

        Energization_df = scheduledf[(scheduledf['Activity_Description'] == 'Project Energization') &
                                           (scheduledf['Schedule_Status'] == 'Active') &
                                           (scheduledf['Project_Status'] == 'Released') &
                                           (scheduledf['Work_Center'] == district)]

        Protection_Control_df=Protection_Control_df.sort_values(by=['Planned_Start'])
        Protection_Control_df.drop_duplicates(subset='Project_ID', keep='last', inplace=True)
        Protection_Control_df['Earliest_PC_Delivery']=Protection_Control_df['Planned_Start']
        dates=Protection_Control_df[['Earliest_PC_Delivery','Project_ID']]
        filterdf = pd.merge(dates, filterdf, on=['Project_ID'], suffixes=('','_y'), how='right')


        Energization_df['Project_Energization'] = Energization_df['Planned_Start']
        dates = Energization_df[['Project_Energization', 'Project_ID']]
        filterdf = pd.merge(dates, filterdf, on=['Project_ID'], suffixes=('', '_y'), how='right')



        filterdf.sort_values(by=['Project_Energization', 'Estimated_In-Service_Date'], inplace=True)
        filterdf.set_index('Project_ID')
        filterdf['Estimated_In-Service_Date'] = filterdf['Estimated_In-Service_Date'].dt.date
        filterdf['Planned_Start'] = filterdf['Planned_Start'].dt.date
        filterdf['Actual_Start'] = filterdf['Actual_Start'].dt.date
        filterdf['Planned_Finish'] = filterdf['Planned_Finish'].dt.date
        filterdf['Actual_Finish'] = filterdf['Actual_Finish'].dt.date
        filterdf['Earliest_PC_Delivery'] = filterdf['Earliest_PC_Delivery'].dt.date
        filterdf['Project_Energization'] = filterdf['Project_Energization'].dt.date

        filterdf['Project_Name'] = filterdf.Name
        filterdf['PETE_ID'] = filterdf.Project_ID
        filterdf['Start_Date'] = filterdf.Planned_Start
        filterdf['Finish_Date'] = filterdf.Planned_Finish



        filterdf.loc[pd.notnull(filterdf.Actual_Start ), 'Start_Date'] = 'Started'
        filterdf.loc[pd.notnull(filterdf.Actual_Finish), 'Finish_Date'] = 'Finished'

        filterdf = filterdf[list(('PETE_ID',
                                  'Project_Name',
                                  'Start_Date',
                                  'Finish_Date',
                                  'Comments',
                                  'Estimated_In-Service_Date',
                                  'Project_Energization',
                                  'Earliest_PC_Delivery',
                                  'Relay_Setter_Project_Engineer',
                                  ))]

        filterdf['Start_Date'] = filterdf['Start_Date'].dropna().astype(str)
        filterdf['Finish_Date'] = filterdf['Finish_Date'].dropna().astype(str)
        filterdf['Project_Energization'] = filterdf['Project_Energization'].dropna().astype(str)
        filterdf['Earliest_PC_Delivery'] = filterdf['Earliest_PC_Delivery'].dropna().astype(str)
        filterdf['Estimated_In-Service_Date'] = filterdf['Estimated_In-Service_Date'].dropna().astype(str)



        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # Save the unformatted results
        filterdf.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
        filterdf.to_excel(writer, index=False, sheet_name=district)

        # Get workbook
        workbook = writer.book
        worksheet = writer.sheets[district]

        # There is a better way to so this but I am ready to move on
        #note that PETE ID is diffrent from the ID used to take you to a website page
        #x=0
        #for row in filterdf.iterrows():
         #   worksheet.write_url('A' + str(2+x),
          #                  'https://pete.corp.oncor.com/pete.web/project-details/' + str(filterdf['Project_ID'].values[x] + 24907),
           #                 string=str('%05.0f' % filterdf['Project_ID'].values[x]))  # Implicit format
           # x=x+1

        cell_format = workbook.add_format()
        cell_format.set_align('center')
        worksheet.set_column('A:I', None, cell_format)



        for x  in range(9):
            set_column_autowidth(worksheet, x)

    writer.save()
    writer.close()

def get_column_width(worksheet: Worksheet, column: int) -> Optional[int]:
    """Get the max column width in a `Worksheet` column."""
    strings = getattr(worksheet, '_ts_all_strings', None)
    if strings is None:
        strings = worksheet._ts_all_strings = sorted(
            worksheet.str_table.string_table,
            key=worksheet.str_table.string_table.__getitem__)
    lengths = set()
    for row_id, colums_dict in worksheet.table.items():  # type: int, dict
        data = colums_dict.get(column)
        if not data:
            continue
        if type(data) is cell_string_tuple:
            iter_length = len(strings[data.string])
            if not iter_length:
                continue
            lengths.add(iter_length)
            continue
        if type(data) is cell_number_tuple:
            iter_length = len(str(data.number))
            if not iter_length:
                continue
            lengths.add(iter_length)
    if not lengths:
        return None
    return max(lengths)

def set_column_autowidth(worksheet: Worksheet, column: int):
    """
    Set the width automatically on a column in the `Worksheet`.
    !!! Make sure you run this function AFTER having all cells filled in
    the worksheet!
    """
    maxwidth = get_column_width(worksheet=worksheet, column=column)
    if maxwidth is None:
        return
    worksheet.set_column(first_col=column, last_col=column, width=maxwidth)

def Check_for_Task(description, project):
    logger.info("Starting Function")
    description = str(description)
    project = str(project)
    logger.info(description)
    logger.info(project)
    tw = TaskWarrior()
    tasks = tw.load_tasks()
    df_pending = pd.DataFrame(tasks['pending'])
    df_completed = pd.DataFrame(tasks['completed'])
    #if (description in df_pending.to_numpy()) and (project in df_pending.to_numpy()):
    try:
        return df_pending[(df_pending['description'] == description) & (df_pending['project'].apply(str) == project)]['id'].item()
    except:
        logger.info('Not found in pending')
    #elif (description in df_completed.values) and project in df_completed.values:
    try:
        return df_completed[(df_completed['description'] == description) & (df_completed['project'].apply(str) == str(project))]['id'].item()
    except:
        logger.info('Not found in completed')

    return 0

def Add_Task(description, project, duedate, priority=None, tag=None):
    logger.info("Starting Function")
    tw = TaskWarrior()
    ID = 0
    ID = Check_for_Task(description, project)
    logger.info(ID)
    if ID == 0 :
        task=tw.task_add(description=description, priority=priority, project=project, due=duedate)
        ID = task['id']

    elif ID > 0:
        #Task exist update
        Update_Task(ID, 'due', duedate)

    if priority is not None:
        Update_Task(ID, 'priority', priority)

    if tag is not None:
        Update_Task(ID, 'tags', tag)


def Update_Task(ID, attribute, value):
    logger.info("Starting Function")
    logger.info(ID)
    logger.info("attribute = " + attribute)
    logger.info(value)
    tw = TaskWarrior()
    id, task = tw.get_task(id=ID)
    logger.info(task)

    try:
        if task[attribute] != value:
            task[attribute] = value
            tw.task_update(task)
    except KeyError:
        logger.info("Attribute has not been set so we are adding it")
        task[attribute] = value
        tw.task_update(task)

    logger.info(task)


#def Complete_Task():


def main():
    Project_Data_Filename='All Project Data Report Metro West or Mike.xlsx'
    Schedules_Filename = 'Metro West PETE Schedules (1).xlsx'
    """ Main entry point of the app """
    logger.info("Starting Pete Maintenance Helper")
    Change_Working_Path('./Data')
    Project_Data_df=Excel_to_Pandas(Project_Data_Filename)
    Project_Schedules_df=Excel_to_Pandas(Schedules_Filename)


    #Set Index for all Dataframes
    myprojectsdf = pd.DataFrame()
    scheduledf = pd.DataFrame()
    pd.set_option('precision', 0)
    for frame in dataframes:
        if 'PETE_ID' in frame.columns:
            #frame['PETE_ID'].astype(int)
            frame.set_index('PETE_ID')
            #frame = frame['PETE_ID'].astype(int)

            if myprojectsdf.empty:
                myprojectsdf = frame
            else:
                myprojectsdf = pd.concat([myprojectsdf, frame])

        elif 'Project_ID' in frame.columns:
            #frame['Project_ID'].astype(int)
            frame.set_index('Project_ID')
            if scheduledf.empty:
                scheduledf=frame
            else:
                scheduledf = pd.concat([scheduledf, frame])
        else:
            logger.info("Error Dataframe doesn't have Pete_ID or Project_ID")

        scheduledf['Estimated_In-Service_Date'] = pd.to_datetime(scheduledf['Estimated_In-Service_Date'])
        scheduledf['Planned_Start'] = pd.to_datetime(scheduledf['Planned_Start'])
        scheduledf['Actual_Start'] = pd.to_datetime(scheduledf['Actual_Start'].fillna(pd.NaT))
        scheduledf['Planned_Finish'] = pd.to_datetime(scheduledf['Planned_Finish'])
        scheduledf['Actual_Finish'] = pd.to_datetime(scheduledf['Actual_Finish'].fillna(pd.NaT))

    myprojectsdf.to_csv('myprojects.csv')
    scheduledf.to_csv('scheduledf.csv')



  #  Create_tasks_for_Precon_meetings(myprojectsdf, scheduledf)
  #  Create_tasks_for_Waterfalls(myprojectsdf, scheduledf)
  #  Create_task_for_Final_Engineering_with_draft_schedules(myprojectsdf, scheduledf)
  #  Create_task_for_Released_projects_missing_Construnction_Ready_Date(myprojectsdf, scheduledf)
  #  Create_task_for_ESID_before_Energiztion(myprojectsdf, scheduledf)
  #  Create_task_for_Electrical_Prints_Start(myprojectsdf, scheduledf)

  #  Create_task_for_Electrical_Prints(scheduledf)
  #  Create_task_for_Relay_Settings(scheduledf)

   # Genrate_Relay_Settings_Report(scheduledf)
   # Genrate_Electrical_Prints_Report(scheduledf)
   # Genrate_Physical_Prints_Report(scheduledf)

#

if __name__ == "__main__":
    """ This is executed when run from the command line """
    # Setup Logging
    logger = logging.getLogger('root')
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(logging.DEBUG)

    main()