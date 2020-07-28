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
    precons_df=schedule[(schedule['Grandchild'] == 'Pre-Construction Meeting') &
             (schedule['Schedule_Status'] == 'Active') &
             (schedule['Percent_Complete'] <= 100 ) &
             (schedule['Planned_Finish'] >= DT.datetime.now()) &
             (schedule['Project_Status'] == 'Released' )]

    outputdf = precons_df[precons_df.Project_ID.isin(list(myprojects.PETE_ID))]


    for index, row in outputdf.iterrows():

        description = 'Check if I have an invite to ' + row['Grandchild']
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
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
    Draft_Waterfalls=scheduledf[(scheduledf['Grandchild'] == 'Waterfall Start') &
                             (scheduledf['Schedule_Status'] == 'Draft') &
                            (scheduledf['Project_Status'] == 'Released') &
                                pd.notnull(scheduledf['Planned_Construction_Ready'])]

    outputdf = Draft_Waterfalls[Draft_Waterfalls.Project_ID.isin(list(myprojects.PETE_ID))]


    for index, row in outputdf.iterrows():

        description = 'Waterfall needs to baselined'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
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
    

def Create_task_for_Final_Engineering_with_draft_schedules(scheduledf):
    # This filters Waterfall schedules that are in draft of Released projects

    filterdf=scheduledf[(scheduledf['Grandchild'] == 'Final Engineering') &
                        (scheduledf['Schedule_Status'] == 'Draft') &
                        (scheduledf['Project_Status'] == 'Released')]

    outputdf = filterdf[filterdf.Project_ID.isin(list(myprojects.PETE_ID))]

    for index, row in outputdf.iterrows():

        description = 'Check with Engineering on when a schedule will be finalized'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
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

def Create_task_for_Released_projects_missing_Construnction_Ready_Date(scheduledf):
    # This filters Waterfall schedules that are in draft of Released projects

    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Waterfall Start') &
                          (pd.isnull(scheduledf['PLANNEDCONSTRUCTIONREADY'])) ]


    for index, row in filterdf.iterrows():

        description = 'Check with Engineering on populating the construction ready date'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
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

def Create_task_for_ESID_before_Energiztion(scheduledf):
    #

    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Project Energization') &
                          (scheduledf['Estimated_In-Service_Date'] < scheduledf['Finish_Date']) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A')]


    for index, row in filterdf.iterrows():

        description = 'Project Energization is after Estimated In-Service Date'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
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


def Create_task_for_Electrical_Prints_Start(scheduledf):
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Electrical Design') &
                              (scheduledf['Start_Date'] + (scheduledf['Finish_Date'] - scheduledf['Start_Date'])/2 <= DT.datetime.today() )  &
                              (scheduledf['Start_Date_Planned\Actual'] != 'A' ) &
                              (scheduledf['Finish_Date'] >= DT.datetime.today()) &
                              (scheduledf['Program_Manager'] != 'Michael Howard' )]

    for index, row in filterdf.iterrows():

        description = 'Check with Engineering on if Electrical Designs were started'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
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

    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Electrical Design') &
                          (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5) ) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A' )]
    outputdf=filterdf
    for index, row in outputdf.iterrows():

        description = 'Check with Engineering on when Electrical Designs will be issued'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
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

    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Create Relay Settings') &
                          (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A')]
    outputdf = filterdf
    for index, row in outputdf.iterrows():

        description = 'Check with Relay Setter on when settings are going to be issued'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
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

        filterdf = scheduledf[(scheduledf['Grandchild'] == 'Create Relay Settings') &
                              (scheduledf['Start_Date'] + (scheduledf['Finish_Date'] - scheduledf[
                                  'Start_Date']) / 2 <= DT.datetime.today()) &
                              (scheduledf['Finish_Date_Planned\Actual'] != 'A') &
                              (scheduledf['Finish_Date'] >= DT.datetime.today())]
        outputdf = filterdf
        for index, row in outputdf.iterrows():

            description = 'Check with with Relay Setter on when settings are going to be started'
            project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
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

    scheduledf = scheduledf[scheduledf['Region_Name'] == 'METRO WEST']

    for district in np.sort(scheduledf.Work_Center_Name.dropna().unique()):

        Energization_df = scheduledf[(scheduledf['Grandchild'] == 'Project Energization') &

                                     (scheduledf['Work_Center_Name'] == district)]


        P_design = scheduledf[(scheduledf['Grandchild'] == 'Physical Design') &

                                           (scheduledf['Work_Center_Name'] == district)]

        Energization_df=Energization_df.assign(Project_Energization = Energization_df['Start_Date'])
        dates = Energization_df[['Project_Energization', 'PETE_ID']]
        P_design = pd.merge(dates, P_design, on=['PETE_ID'], suffixes=('', '_y'), how='right')



        P_design = P_design.assign(Physical_Design_Start=P_design['Start_Date'])
        P_design = P_design.assign(Physical_Design_Finish=P_design['Finish_Date'])

        P_design['Project_Name'] = P_design.Project_Name_x
        P_design['PETE_ID'] = P_design.PETE_ID

        P_design.sort_values(by=['Project_Energization', 'Estimated_In-Service_Date'], inplace=True)
        P_design.set_index('PETE_ID')
       # P_design['Estimated_In-Service_Date'] = P_design['Estimated_In-Service_Date'].dt.date
        P_design['Physical_Design_Start'] = P_design['Physical_Design_Start'].dt.date
        P_design['Physical_Design_Finish'] = P_design['Physical_Design_Finish'].dt.date
       # P_design['Planned_Finish'] = P_design['Planned_Finish'].dt.date
     #   P_design['Actual_Finish'] = P_design['Actual_Finish'].dt.date
        P_design['Project_Energization'] = P_design['Project_Energization'].dt.date


        P_design['Physical_Design_Start'] = P_design['Physical_Design_Start'].dropna().astype(str)
        P_design['Physical_Design_Finish'] = P_design['Physical_Design_Finish'].dropna().astype(str)
        P_design['Project_Energization'] = P_design['Project_Energization'].dropna().astype(str)
        P_design['Estimated_In-Service_Date'] = P_design['Estimated_In-Service_Date'].dropna().astype(str)

        P_design.loc[P_design['Start_Date_Planned\Actual'] == 'A', 'Physical_Design_Start'] = 'Started'
        P_design.loc[P_design['Finish_Date_Planned\Actual'] == 'A', 'Physical_Design_Finish'] = 'Finished'

        outputdf = P_design[list(('PETE_ID',
                                  'Project_Name',
                                  'Physical_Design_Start',
                                  'Physical_Design_Finish',
                                  'Comments',
                                  'Project_Energization',
                                  'Estimated_In-Service_Date',
                                  ))]

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # Save the unformatted results
        outputdf.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
        outputdf.to_excel(writer, index=False, sheet_name=district)

        # Get workbook
        workbook = writer.book
        worksheet = writer.sheets[district]

        # There is a better way to so this but I am ready to move on
        # note that PETE ID is diffrent from the ID used to take you to a website page
        x = 0
        for row in P_design.iterrows():
            worksheet.write_url('A' + str(2 + x),
                                'https://pete.corp.oncor.com/pete.web/project-details/' + str(
                                    P_design['PROJECTID'].values[x]),
                                string=str('%05.0f' % P_design['PETE_ID'].values[x]))  # Implicit format
            x = x + 1

        cell_format = workbook.add_format()
        cell_format.set_align('center')
        worksheet.set_column('A:I', None, cell_format)



        for x  in range(9):
            set_column_autowidth(worksheet, x)

    writer.save()
    writer.close()

def Genrate_Electrical_Prints_Report(scheduledf):
    writer = pd.ExcelWriter('Metro West Electrical Prints Report.xlsx', engine='xlsxwriter')

    scheduledf = scheduledf[scheduledf['Region_Name'] == 'METRO WEST']

    for district in np.sort(scheduledf.Work_Center_Name.dropna().unique()):
        Energization_df = scheduledf[(scheduledf['Grandchild'] == 'Project Energization') &
                                     #(scheduledf['Schedule_Status'] == 'Active') &
                                  #   (scheduledf['Project_Status'] == 'Released') &
                                     (scheduledf['Work_Center_Name'] == district)]

        E_design = scheduledf[(scheduledf['Grandchild'] == 'Electrical Design') &
                                           #(scheduledf['Schedule_Status'] == 'Active') &
                                           #(scheduledf['Project_Status'] == 'Released') &
                                           (scheduledf['Work_Center_Name'] == district)]

        E_design = E_design.assign(Electrical_Design_Start=E_design['Start_Date'])
        E_design = E_design.assign(Electrical_Design_Finish=E_design['Finish_Date'])

        Energization_df=Energization_df.assign(Project_Energization = Energization_df['Start_Date'])
        dates = Energization_df[['Project_Energization', 'PETE_ID']]
        E_design = pd.merge(dates, E_design, on=['PETE_ID'], suffixes=('', '_y'), how='right')

        E_design['Project_Name'] = E_design.Project_Name_x
        E_design['PETE_ID'] = E_design.PETE_ID



        E_design.sort_values(by=['Project_Energization', 'Estimated_In-Service_Date'], inplace=True)
        E_design.set_index('PETE_ID')
        E_design['Estimated_In-Service_Date'] = E_design['Estimated_In-Service_Date'].dt.date
        E_design['Electrical_Design_Start'] = E_design['Electrical_Design_Start'].dt.date
        E_design['Electrical_Design_Finish'] = E_design['Electrical_Design_Finish'].dt.date
        E_design['Planned_Finish'] = E_design['Finish_Date'].dt.date
       # E_design['Actual_Finish'] = E_design['Actual_Finish'].dt.date
        E_design['Project_Energization'] = E_design['Project_Energization'].dt.date


        E_design['Electrical_Design_Start'] = E_design['Electrical_Design_Start'].dropna().astype(str)
        E_design['Electrical_Design_Finish'] = E_design['Electrical_Design_Finish'].dropna().astype(str)
        E_design['Project_Energization'] = E_design['Project_Energization'].dropna().astype(str)
        E_design['Estimated_In-Service_Date'] = E_design['Estimated_In-Service_Date'].dropna().astype(str)

        E_design.loc[E_design['Start_Date_Planned\Actual'] == 'A', 'Electrical_Design_Start'] = 'Started'
        E_design.loc[E_design['Finish_Date_Planned\Actual'] == 'A', 'Electrical_Design_Finish'] = 'Finished'

        Outputdf = E_design[list(('PETE_ID',
                                  'Project_Name',
                                  'Electrical_Design_Start',
                                  'Electrical_Design_Finish',
                                  'Comments',
                                  'Project_Energization',
                                  'Estimated_In-Service_Date',
                                  ))]

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # Save the unformatted results
        Outputdf.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
        Outputdf.to_excel(writer, index=False, sheet_name=district)

        # Get workbook
        workbook = writer.book
        worksheet = writer.sheets[district]

        # There is a better way to so this but I am ready to move on
        # note that PETE ID is diffrent from the ID used to take you to a website page
        x = 0
        for row in E_design.iterrows():
            worksheet.write_url('A' + str(2 + x),
                                'https://pete.corp.oncor.com/pete.web/project-details/' + str(
                                    E_design['PROJECTID'].values[x]),
                                string=str('%05.0f' % E_design['PETE_ID'].values[x]))  # Implicit format
            x = x + 1

        cell_format = workbook.add_format()
        cell_format.set_align('center')
        worksheet.set_column('A:I', None, cell_format)



        for x  in range(9):
            set_column_autowidth(worksheet, x)

    writer.save()
    writer.close()

def Genrate_Relay_Settings_Report(scheduledf):
    writer = pd.ExcelWriter('Metro West Relay Settings Report.xlsx', engine='xlsxwriter')

    scheduledf = scheduledf[scheduledf['Region_Name'] == 'METRO WEST']

    for district in np.sort(scheduledf.Work_Center_Name.dropna().unique()):

        filterdf = scheduledf[(scheduledf['Grandchild'] == 'Create Relay Settings') &
                              #(pd.notnull(scheduledf['Start_Date'])) &
                               (scheduledf['Work_Center_Name'] == district)]

        Protection_Control_df = scheduledf[(scheduledf['Grandchild'].str.contains('Relay')) &
                                (scheduledf['Grandchild'].str.contains('Complete Prewired Switching Station Control Center')) &
                             # (scheduledf['Schedule_Status'] == 'Active') &
                             # (scheduledf['Project_Status'] == 'Released') &
                              (scheduledf['Work_Center_Name'] == district)]

        Energization_df = scheduledf[(scheduledf['Grandchild'] == 'Project Energization') &
                                          # (scheduledf['Schedule_Status'] == 'Active') &
                                          # (scheduledf['Project_Status'] == 'Released') &
                                           (scheduledf['Work_Center_Name'] == district)]

        Protection_Control_df=Protection_Control_df.sort_values(by=['Start_Date'])
        Protection_Control_df.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
        Protection_Control_df['Earliest_PC_Delivery']=Protection_Control_df['Start_Date']
        dates=Protection_Control_df[['Earliest_PC_Delivery','PETE_ID']]
        filterdf = pd.merge(dates, filterdf, on=['PETE_ID'], suffixes=('','_y'), how='right')


        Energization_df['Project_Energization'] = Energization_df['Start_Date']
        dates = Energization_df[['Project_Energization', 'PETE_ID']]
        filterdf = pd.merge(dates, filterdf, on=['PETE_ID'], suffixes=('', '_y'), how='right')



        filterdf.sort_values(by=['Project_Energization', 'Estimated_In-Service_Date'], inplace=True)
        filterdf.set_index('PETE_ID')
        filterdf['Estimated_In-Service_Date'] = filterdf['Estimated_In-Service_Date'].dt.date
        filterdf['Start_Date'] = filterdf['Start_Date'].dt.date
        filterdf['Finish_Date'] = filterdf['Finish_Date'].dt.date
        filterdf['Earliest_PC_Delivery'] = filterdf['Earliest_PC_Delivery'].dt.date
        filterdf['Project_Energization'] = filterdf['Project_Energization'].dt.date

        filterdf['Project_Name'] = filterdf.Project_Name_x



        filterdf.loc[filterdf['Start_Date_Planned\Actual'] == 'A', 'Start_Date'] = 'Started'
        filterdf.loc[filterdf['Finish_Date_Planned\Actual'] == 'A', 'Finish_Date'] = 'Finished'

        outputdf = filterdf[list(('PETE_ID',
                                  'Project_Name',
                                  'Start_Date',
                                  'Finish_Date',
                                  'Comments',
                                  'Estimated_In-Service_Date',
                                  'Project_Energization',
                                  'Earliest_PC_Delivery',
                                  'RELAYSETTER',
                                  ))]

        outputdf['Start_Date'] = outputdf['Start_Date'].dropna().astype(str)
        outputdf['Finish_Date'] = outputdf['Finish_Date'].dropna().astype(str)
        outputdf['Project_Energization'] = outputdf['Project_Energization'].dropna().astype(str)
        outputdf['Earliest_PC_Delivery'] = outputdf['Earliest_PC_Delivery'].dropna().astype(str)
        outputdf['Estimated_In-Service_Date'] = outputdf['Estimated_In-Service_Date'].dropna().astype(str)




        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # Save the unformatted results
        outputdf.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
        outputdf.to_excel(writer, index=False, sheet_name=district)

        # Get workbook
        workbook = writer.book
        worksheet = writer.sheets[district]

        # There is a better way to so this but I am ready to move on
        #note that PETE ID is diffrent from the ID used to take you to a website page
        x=0
        for row in filterdf.iterrows():
            worksheet.write_url('A' + str(2+x),
                            'https://pete.corp.oncor.com/pete.web/project-details/' + str(filterdf['PROJECTID'].values[x]),
                            string=str('%05.0f' % filterdf['PETE_ID'].values[x]))  # Implicit format
            x=x+1



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
    Schedules_Filename = 'Metro West PETE Schedules.xlsx'
    """ Main entry point of the app """
    logger.info("Starting Pete Maintenance Helper")
    Change_Working_Path('./Data')
    try:
        Project_Data_df=Excel_to_Pandas(Project_Data_Filename)
    except:
        logger.error('Can not find Project Data file')
        raise

    try:
        Project_Schedules_df=Excel_to_Pandas(Schedules_Filename)
    except:
        logger.error('Can not find Schedule Data file')
        raise

    Project_Schedules_All_Data_df = pd.merge(Project_Schedules_df, Project_Data_df, on='PETE_ID', sort= False)

    #myprojectsdf.to_csv('myprojects.csv')
    Project_Schedules_All_Data_df.to_csv('scheduledf.csv')



    #Create_tasks_for_Precon_meetings(Project_Schedules_All_Data_df)
  #  Create_tasks_for_Waterfalls(myprojectsdf, scheduledf)
  #  Create_task_for_Final_Engineering_with_draft_schedules(myprojectsdf, scheduledf)
    Create_task_for_Released_projects_missing_Construnction_Ready_Date(Project_Schedules_All_Data_df)
    Create_task_for_ESID_before_Energiztion(Project_Schedules_All_Data_df)
    Create_task_for_Electrical_Prints_Start(Project_Schedules_All_Data_df)

    Create_task_for_Electrical_Prints(Project_Schedules_All_Data_df)
    Create_task_for_Relay_Settings(Project_Schedules_All_Data_df)

    Genrate_Relay_Settings_Report(Project_Schedules_All_Data_df)
    Genrate_Electrical_Prints_Report(Project_Schedules_All_Data_df)
    Genrate_Physical_Prints_Report(Project_Schedules_All_Data_df)

#

if __name__ == "__main__":
    """ This is executed when run from the command line """
    # Setup Logging
    logger = logging.getLogger('root')
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(logging.DEBUG)

    main()