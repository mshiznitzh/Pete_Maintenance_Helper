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
    Worksheet, cell_number_tuple, cell_string_tuple, xl_rowcol_to_cell
)
import multiprocessing
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from subprocess import Popen, PIPE



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
def Excel_to_Pandas(filename,check_update=False):
    logger.info('importing file ' + filename)
    df=[]
    if check_update == True:
        timestamp = DT.datetime.fromtimestamp(Path(filename).stat().st_mtime)
        if DT.datetime.today().date() != timestamp.date():
            root = tk.Tk()
            root.withdraw()
            filename = filedialog.askopenfilename(title =' '.join(['Select file for', filename]))

    try:
        df = pd.read_excel(filename, sheet_name=None)
        df = pd.concat(df, axis=0, ignore_index=True)
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

    outputdf.sort_values(by=['Estimated_In_Service_Date'])
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

def Create_tasks_for_Waterfalls(scheduledf):
    # This filters Waterfall schedules that are in draft of Released projects
    PMO_DF=scheduledf[(scheduledf['Schedule_Function'] == 'PMO') &
                      (scheduledf['Program_Manager'] == 'Michael Howard')]

    All_projects_DF = scheduledf[(scheduledf['Program_Manager'] == 'Michael Howard')]

    All_projects_DF=All_projects_DF.drop_duplicates(subset=['PETE_ID'])
    PMO_DF=PMO_DF.drop_duplicates(subset=['PETE_ID'])



    outputdf = All_projects_DF.loc[~All_projects_DF['PETE_ID'].isin(PMO_DF['PETE_ID'])]

    outputdf.sort_values(by=['Estimated_In_Service_Date'])
    for index, row in outputdf.iterrows():

        description = 'Waterfall needs to baselined'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
        duedate = DT.datetime.today() + DT.timedelta(hours=1)

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')

    Waterfall_Start_DF = scheduledf[(scheduledf['Schedule_Function'] == 'PMO') &
                        (scheduledf['Program_Manager'] == 'Michael Howard') &
                        (scheduledf['Grandchild'] == 'Waterfall Start')]

    Waterfall_Finish_DF = scheduledf[(scheduledf['Schedule_Function'] == 'PMO') &
                                    (scheduledf['Program_Manager'] == 'Michael Howard') &
                                    (scheduledf['Grandchild'] == 'Waterfall Finish')]

    Waterfall_Start_DF.reset_index(drop=True)
    Waterfall_Finish_DF.reset_index(drop=True)
    outputdf = Waterfall_Start_DF.loc[Waterfall_Start_DF['Start_Date'].values > Waterfall_Finish_DF['Start_Date'].values]

    outputdf.sort_values(by=['Estimated_In_Service_Date'])
    for index, row in outputdf.iterrows():

        description = 'Waterfall Finish is before Waterfall Start'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
        duedate = DT.datetime.today() + DT.timedelta(hours=1)

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')

    outputdf=Waterfall_Finish_DF
    outputdf['ESID_SEASON']=outputdf.loc[pd.to_datetime(outputdf['Estimated_In-Service_Date']).dt.quarter < 3, 'ESID_SEASON'] = pd.to_numeric(pd.to_datetime(outputdf['Estimated_In-Service_Date']).dt.year)+.5
    outputdf['ESID_SEASON'] = outputdf.loc[pd.to_datetime(outputdf['Estimated_In-Service_Date']).dt.quarter >= 3, 'ESID_SEASON'] = pd.to_numeric(pd.to_datetime(outputdf['Estimated_In-Service_Date']).dt.year)

    outputdf['WaterFall_SEASON'] = outputdf.loc[pd.to_datetime(outputdf['Start_Date']).dt.quarter < 3, 'WaterFall_SEASON'] = pd.to_numeric(pd.to_datetime(outputdf['Start_Date']).dt.year)+.5
    outputdf['WaterFall_SEASON'] = outputdf.loc[pd.to_datetime(outputdf['Start_Date']).dt.quarter >= 3, 'WaterFall_SEASON'] = pd.to_numeric(pd.to_datetime(outputdf['Start_Date']).dt.year)

    outputdf = outputdf.loc[(
        outputdf['WaterFall_SEASON'] != outputdf['ESID_SEASON'])]

    outputdf.sort_values(by=['Estimated_In_Service_Date'])
    for index, row in outputdf.iterrows():

        description = 'Waterfall Finish not in same season as EISD'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
        duedate = DT.datetime.today() + DT.timedelta(hours=1)

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')



def Create_task_for_Final_Engineering_with_draft_schedules(scheduledf):
    # This filters Waterfall schedules that are in draft of Released projects

    filterdf=scheduledf[(scheduledf['Grandchild'] == 'Final Engineering') &
                        (scheduledf['Schedule_Status'] == 'Draft') &
                        (scheduledf['Project_Status'] == 'Released')]

    outputdf = filterdf[filterdf.Project_ID.isin(list(myprojects.PETE_ID))]
    outputdf.sort_values(by=['Estimated_In_Service_Date'])
    for index, row in outputdf.iterrows():

        description = 'Check with Engineering on when a schedule will be finalized'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
        duedate = DT.datetime.today() + DT.timedelta(hours=2)

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

    filterdf = scheduledf[(pd.isnull(scheduledf['PLANNEDCONSTRUCTIONREADY'])) &
                          (scheduledf['Program_Manager'] == 'Michael Howard')]

    filterdf= filterdf.drop_duplicates(subset=['PETE_ID'])

    filterdf.sort_values(by=['Estimated_In_Service_Date'])
    for index, row in filterdf.iterrows():

        description = 'Check with Engineering on populating the construction ready date'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
        duedate = DT.datetime.today()+DT.timedelta(hours=3)

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
                          (scheduledf['Program_Manager'] == 'Michael Howard') &
                          (scheduledf['Estimated_In-Service_Date'] < scheduledf['Finish_Date']) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A')]

    filterdf.sort_values(by=['Estimated_In_Service_Date'])
    for index, row in filterdf.iterrows():

        description = 'Project Energization is after Estimated In-Service Date'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
        duedate = DT.datetime.today() + DT.timedelta(hours=4)

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')


def Create_tasks_for_Engineering_Activities_Start_Dates(scheduledf, Create_Tasks=True):
    description=None
    #This code filters out the start dates for TE activities and creates tasks
    EDdf = scheduledf[(scheduledf['Grandchild'] == 'Electrical Design') &
                      (scheduledf['Start_Date'] + (
                                  scheduledf['Finish_Date'] - scheduledf['Start_Date']) / 2 <= DT.datetime.today()) &
                      (scheduledf['Start_Date_Planned\Actual'] != 'A') &
                      (scheduledf['Finish_Date'] >= DT.datetime.today()) &
                      (scheduledf['Program_Manager'] != 'Michael Howard')]

    PDdf = scheduledf[(scheduledf['Grandchild'] == 'Physical Design') &
                          (scheduledf['Start_Date'] + (scheduledf['Finish_Date'] - scheduledf[
                              'Start_Date']) / 2 <= DT.datetime.today()) &
                          (scheduledf['Start_Date_Planned\Actual'] != 'A') &
                          (scheduledf['Finish_Date'] >= DT.datetime.today()) &
                          (scheduledf['Program_Manager'] != 'Michael Howard')]

    FDdf = scheduledf[(scheduledf['Grandchild'] == 'Foundation Design') &
                            (scheduledf['Start_Date'] + (scheduledf['Finish_Date'] - scheduledf[
                                'Start_Date']) / 2 <= DT.datetime.today()) &
                            (scheduledf['Start_Date_Planned\Actual'] != 'A') &
                            (scheduledf['Finish_Date'] >= DT.datetime.today()) &
                            (scheduledf['Program_Manager'] != 'Michael Howard')]

    filterdf=EDdf[~EDdf['PETE_ID'].isin(PDdf['PETE_ID'])]
    filterdf=filterdf[~filterdf['PETE_ID'].isin(FDdf['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'Check with Engineering on if Electrical Designs were started'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            create_tasks(filterdf, description, duedate)

    filterdf = PDdf[~PDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(FDdf['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'Check with Engineering on if Physical Designs were started'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            create_tasks(filterdf, description, duedate)

    filterdf = FDdf[~FDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(PDdf['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'Check with Engineering on if Foundation Designs were started'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            create_tasks(filterdf, description, duedate)

    filterdf = FDdf[FDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = pd.merge(PDdf[PDdf['PETE_ID'].isin(EDdf['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = 'Ask Engineering to update the TE schedule'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            create_tasks(filterdf, description, duedate)
    return description

def Create_tasks_for_Engineering_Activities_Finish_Dates(scheduledf, Create_Tasks=True):
    # This code filters out the finish dates for TE activities and creates tasks

    EDdf = scheduledf[(scheduledf['Grandchild'] == 'Electrical Design') &
                      (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A')]

    PDdf = scheduledf[(scheduledf['Grandchild'] == 'Physical Design') &
                      (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A')]

    FDdf = scheduledf[(scheduledf['Grandchild'] == 'Foundation Design') &
                      (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                      (scheduledf['Finish_Date_Planned\Actual'] != 'A')]

    filterdf = EDdf[~EDdf['PETE_ID'].isin(PDdf['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(FDdf['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'Check with Engineering on if Electrical Designs were issued'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            create_tasks(filterdf, description, duedate)

    filterdf = PDdf[~PDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(FDdf['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'Check with Engineering on if Physical Designs were issued'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            create_tasks(filterdf, description, duedate)


    filterdf = FDdf[~FDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(PDdf['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'Check with Engineering on if Foundation Designs were issued'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            create_tasks(filterdf, description, duedate)

    filterdf = FDdf[FDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = pd.merge(PDdf[PDdf['PETE_ID'].isin(EDdf['PETE_ID'])], filterdf, how='right')

    duedate = DT.datetime.today() + DT.timedelta(hours=5)
    if len(filterdf) >= 1:
        description = 'Ask Engineering to update the TE schedule (Finish Date)'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            create_tasks(filterdf, description, duedate)

    return description

def Create_tasks_for_Construncction_Task_Request_Approval(scheduledf):
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Construction Task Request Approval') &
                      (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                      (scheduledf['Finish_Date_Planned\Actual'] != 'A') &
                      (scheduledf['Program_Manager'] == 'Michael Howard')]

    description = 'Ask Engineering for update on Construction Task Request Approval'
    duedate = DT.datetime.today() + DT.timedelta(hours=5)
    create_tasks(filterdf, description, duedate)

def Create_tasks_for_Design_Book_Issued(scheduledf):
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Complete Design Book Issued') &
                          (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A')]

    description = 'Ask Engineering for update on Design Book Issued'
    duedate = DT.datetime.today() + DT.timedelta(hours=5)
    create_tasks(filterdf, description, duedate)

def Create_tasks_for_WA(scheduledf):
    filterdf = scheduledf[(pd.isnull(scheduledf['FIMSTATUS'])) &
                         (scheduledf['PLANNEDCONSTRUCTIONREADY'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                         (scheduledf['Finish_Date_Planned\Actual'] != 'A') &
                         (scheduledf['Program_Manager'] == 'Michael Howard')]

    description = 'Ask Engineering about the WA'
    duedate = DT.datetime.today() + DT.timedelta(hours=5)
    create_tasks(filterdf, description, duedate)
    return description

def create_tasks(df, description, duedate, tag='PMH'):
    df = df.sort_values(by=['Estimated_In_Service_Date'])
    for index, row in df.iterrows():

        logger.info("Starting Function")
        logger.info(str(row['PETE_ID']))

        project = str(row['PETE_ID']) + ':' + row['Project_Name_y']


        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, tag)


def Create_task_for_Relay_Settings(scheduledf, Create_Tasks=True):
    # This filters Prints with finished dates past 5 days past today without an actual finish
    description=None

    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Create Relay Settings') &
                          (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A')]

    filterdf=filterdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(filterdf) >= 1:
        description = 'Check with Relay Setter on when settings are going to be issued'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            create_tasks(filterdf, description, duedate)

    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Create Relay Settings') &
                              (scheduledf['Start_Date'] + (scheduledf['Finish_Date'] - scheduledf[
                                  'Start_Date']) / 2 <= DT.datetime.today()) &
                              (scheduledf['Start_Date_Planned\Actual'] != 'A') &
                              (scheduledf['Finish_Date'] >= DT.datetime.today())]
    filterdf = filterdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(filterdf) >= 1:
        description = 'Check with Relay Setter on when settings are going to be started'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            create_tasks(filterdf, description, duedate)

    return description

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

def Genrate_Relay_Settings_Report(scheduledf, Relay_Setters_df):
    writer = pd.ExcelWriter('Metro West Relay Settings Report.xlsx', engine='xlsxwriter')

    scheduledf = scheduledf[scheduledf['Region_Name'] == 'METRO WEST']
    scheduledf = pd.merge(scheduledf, Relay_Setters_df[['PETE_ID', 'Relay_Setter_Engineer']], on='PETE_ID' )

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
                                  'Relay_Setter_Engineer',
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

def Genrate_Resource_Plan(scheduledf, Budget_item_df):

    #scheduledf = scheduledf[scheduledf['Region_Name'] == 'METRO WEST']
    scheduledf.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
    scheduledf = scheduledf[scheduledf.PROJECTTYPE != 'ROW']
    scheduledf.rename(columns={'BUDGETITEMNUMBER': 'Budget_Item_Number'}, inplace=True)
    new_header=Budget_item_df.iloc[0]
    Budget_item_df = Budget_item_df[1:]
    Budget_item_df.columns = new_header

    Budget_item_df.rename(columns={'Budget Item Number': 'Budget_Item_Number'}, inplace=True)
    Budget_item_df.rename(columns={'Description': 'Budget_Item'}, inplace=True)

    scheduledf = pd.merge(scheduledf, Budget_item_df, on='Budget_Item_Number')


    for district in np.sort(scheduledf.Work_Center_Name.dropna().unique()):
        writer = pd.ExcelWriter(district + ' Spring District Resource Plan.xlsx', engine='xlsxwriter')
        for type in np.sort(scheduledf.PROJECTTYPE.dropna().unique()):
            filtereddf = scheduledf[(scheduledf['Estimated_In_Service_Date'] >= pd.to_datetime('2021-01-01')) &
                                     (scheduledf['Estimated_In_Service_Date'] <= pd.to_datetime('2021-12-31')) &
                                     (scheduledf['PROJECTTYPE'] == type) &
                                     (scheduledf['Work_Center_Name'] == district)]

            outputdf = filtereddf.sort_values(by=['PLANNEDCONSTRUCTIONREADY'], ascending=True)
            outputdf = filtereddf[list(('PETE_ID',
                                      'WA',
                                      'Project_Name_x',
                                      'Description',
                                      'PLANNEDCONSTRUCTIONREADY',
                                      'Estimated_In-Service_Date',
                                      'Budget_Item',
                                      ))]

            if type == 'Station':
                Work= [ 'P&C Work',
                        'Set Steel',
                        'Weld Bus',
                        'Set Switches',
                        'Install Jumpers',
                        'Dress Transformer',
                        'Above Grade Demo',
                        'Set Breakers',
                        'Remove Old Breakers'
                      ]
            else:
                Work = ['Build Lattice',
                        'FCC',
                        'Install Insulators',
                        'Set Switches',
                        'Replace Arms'
                        ]

            Work.sort()

            for item in Work:
                outputdf[item] = np.nan

            outputdf['Comments'] = np.nan

            outputdf['PLANNEDCONSTRUCTIONREADY'] = outputdf['PLANNEDCONSTRUCTIONREADY'].dt.date
            outputdf['Estimated_In-Service_Date'] = outputdf['Estimated_In-Service_Date'].dt.date

            outputdf['PLANNEDCONSTRUCTIONREADY'] = outputdf['PLANNEDCONSTRUCTIONREADY'].dropna().astype(str)
            outputdf['Estimated_In-Service_Date'] = outputdf['Estimated_In-Service_Date'].dropna().astype(str)
            outputdf['WA'] = outputdf['WA'].dropna().astype(str)
            #outputdf['Earliest_PC_Delivery'] = outputdf['Earliest_PC_Delivery'].dropna().astype(str)
            #outputdf['Estimated_In-Service_Date'] = outputdf['Estimated_In-Service_Date'].dropna().astype(str)

            outputdf.rename(columns={'PLANNEDCONSTRUCTIONREADY': 'Construction Ready'}, inplace= True)
            outputdf.rename(columns={'Project_Name_x': 'Project Name'}, inplace= True)


            # Create a Pandas Excel writer using XlsxWriter as the engine.
            # Save the unformatted results

            if len(outputdf) >= 1:
                outputdf.to_excel(writer, index=False, sheet_name=district + ' ' + type)

                # Get workbook
                workbook = writer.book
                worksheet = writer.sheets[district + ' ' + type]

                # There is a better way to so this but I am ready to move on
                # note that PETE ID is diffrent from the ID used to take you to a website page
                x = 0
                for row in filtereddf.iterrows():
                    worksheet.write_url('A' + str(2 + x),
                                        'https://pete.corp.oncor.com/pete.web/project-details/' + str(
                                            filtereddf['PROJECTID'].values[x]),
                                        string=str('%05.0f' % filtereddf['PETE_ID'].values[x]))  # Implicit format
                    x = x + 1




                for column in outputdf.columns:
                    index = outputdf.columns.get_loc(column)
                    if column == 'P&C Work':
                        worksheet.data_validation(
                            xl_rowcol_to_cell(1,index)+':'+xl_rowcol_to_cell(outputdf.shape[0], index),
                                          {'validate': 'list', 'source': [
                                              'Commissioning Group',
                                              'District',
                                              'N/A',
                                              'Outside District'
                                             ],})

                    elif column in Work:
                        worksheet.data_validation(
                            xl_rowcol_to_cell(1, index) + ':' + xl_rowcol_to_cell(outputdf.shape[0], index),
                            {'validate': 'list', 'source': [
                                'District will do all',
                                'District will do some, see comments',
                                'N/A',
                                'Outside District'

                            ], })
            cell_format = workbook.add_format()





            cell_format = workbook.add_format()
            cell_format.set_align('center')
            cell_format.set_align('vcenter')
            worksheet.set_column('A:' + chr(ord('@') + len(outputdf.columns)), None, cell_format)

            for x in range(len(outputdf.columns)):
                set_column_autowidth(worksheet, x)

            wrap_format = workbook.add_format()
            wrap_format.set_text_wrap()
            wrap_format.set_align('vcenter')
            worksheet.set_column('C:D', None, wrap_format)
            worksheet.set_column('C:D', 100)


        writer.save()
        writer.close()


def Genrate_Matrial_Report(Material_df, scheduledf):
    for district in np.sort(scheduledf.Work_Center_Name.dropna().unique()):
        writer = pd.ExcelWriter(' '.join([district,'Material Report.xlsx']), engine='xlsxwriter')
        workbook = writer.book
        summarysheet = workbook.add_worksheet('Summary')
        filtereddf = scheduledf[(scheduledf['Work_Center_Name'] == district)]
        row=0
        for project in np.sort(filtereddf.WA_Number.dropna().unique()):

            project_material_df = Material_df[Material_df['PROJECT'] == project]
            if len(project_material_df) >= 1:

                summarysheet.write_url(row, 0, f"internal:'{project}'!A1", string=project)
                summarysheet.write(row, 1, str(scheduledf[(scheduledf['WA_Number']==project)]['Project_Name_x'].values[0]))
                row = row + 1
                project_material_df.to_excel(writer, index=False, sheet_name=project)
                # Get workbook

                worksheet = writer.sheets[project]

                cell_format = workbook.add_format()
                cell_format.set_align('center')
                cell_format.set_align('vcenter')
                worksheet.set_column('A:' + chr(ord('@') + len(project_material_df.columns)), None, cell_format)

                for x in range(len(project_material_df.columns)):
                    set_column_autowidth(worksheet, x)

                wrap_format = workbook.add_format()
                wrap_format.set_text_wrap()
                wrap_format.set_align('vcenter')
                worksheet.set_column('C:C', None, wrap_format)
                worksheet.set_column('C:C', 100)


        writer.save()
        writer.close()

def Create_task_for_add_WA_to_schedule(scheduledf, myprojectbudgetitmes):
    # This filters Prints with finished dates past 5 days past today without an actual finish

    filterdf = scheduledf[(pd.isnull(scheduledf['Schedule_Function'])) &
                          (scheduledf['PROJECTSTATUS'] == 'Released') &
                          (scheduledf['BUDGETITEMNUMBER'].isin(myprojectbudgetitmes))]
    outputdf = filterdf
    outputdf = outputdf.sort_values(by=['Estimated_In_Service_Date'])
    for index, row in outputdf.iterrows():

        description = 'Add PETE ID to query for Schedules'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_y']
        duedate = DT.datetime.today() + DT.timedelta(hours=6)

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')

#def Complete_Task():

def Create_task_for_missing_tiers(df):
    filterdf = df[(pd.isnull(df['Project_Tier'])) &
                          (df['Program_Manager'] == 'Michael Howard')]

    outputdf = filterdf.drop_duplicates(subset=['PETE_ID'])
    outputdf = outputdf.sort_values(by=['Estimated_In_Service_Date'])
    for index, row in outputdf.iterrows():

        description = 'Project Tier Missing'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_y']
        duedate = DT.datetime.today() + DT.timedelta(hours=6)

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Add_Task(description, project, duedate, priority, 'PMH')

def main():
    Project_Data_Filename='All Project Data Report Metro West or Mike.xlsx'
    Schedules_Filename = 'Metro West PETE Schedules.xlsx'
    Budget_Item_Filename = 'Budget Item.xlsx'
    Relay_Setters_Filename = 'Relay Setter Report.xlsx'
    Material_Data_Filename = 'Material Status Report All Metro West.xlsx'

    myprojectbudgetitmes=['00003212', '00003201', '00003203', '00003206', '00003226']

    """ Main entry point of the app """
    logger.info("Starting Pete Maintenance Helper")
    Change_Working_Path('./Data')
    try:
        Project_Data_df=Excel_to_Pandas(Project_Data_Filename, True)
    except:
        logger.error('Can not find Project Data file')
        raise



    try:
        Project_Schedules_df=Excel_to_Pandas(Schedules_Filename, True)
    except:
        logger.error('Can not find Schedule Data file')
        raise

    try:
        budget_item_df=Excel_to_Pandas(Budget_Item_Filename)
    except:
        logger.error('Can not find Budget Item Data file')

    try:
        Relay_Setters_df=Excel_to_Pandas(Relay_Setters_Filename)
    except:
        logger.error('Can not find Relay Setters Data file')


    Project_Schedules_All_Data_df = pd.merge(Project_Schedules_df, Project_Data_df, on='PETE_ID', sort= False, how='outer')

    #myprojectsdf.to_csv('myprojects.csv')
    Project_Schedules_All_Data_df.to_csv('scheduledf.csv')


#Return the day of the week as an integer, where Monday is 0 and Sunday is 6
    if DT.date.today().weekday() == 0:

        res = Popen('tasks=$(task tag=PMH _ids) && task delete $tasks', shell=True, stdin=PIPE)
        res.stdin.write(b'a\n')
        res.stdin.flush()
        res.stdin.close()
        res = Popen('task sync', shell=True, stdin=PIPE)
        res.stdin.close()


        #Create_tasks_for_Precon_meetings(Project_Schedules_All_Data_df)
        #Create_task_for_Final_Engineering_with_draft_schedules(myprojectsdf, scheduledf)
        #Create_task_for_Released_projects_missing_Construnction_Ready_Date(Project_Schedules_All_Data_df)
        Create_task_for_Relay_Settings(Project_Schedules_All_Data_df)
        Create_task_for_ESID_before_Energiztion(Project_Schedules_All_Data_df)
        Create_tasks_for_Engineering_Activities_Start_Dates(Project_Schedules_All_Data_df)
        Create_tasks_for_Engineering_Activities_Finish_Dates(Project_Schedules_All_Data_df)
        Create_task_for_Relay_Settings(Project_Schedules_All_Data_df)
        Create_task_for_add_WA_to_schedule(Project_Schedules_All_Data_df, myprojectbudgetitmes)
        Create_tasks_for_Waterfalls(Project_Schedules_All_Data_df)
        Create_task_for_missing_tiers(Project_Schedules_All_Data_df)

        res = Popen('task sync', shell=True, stdin=PIPE)
        res.stdin.close()

    if DT.date.today().weekday() == 4:
        Genrate_Relay_Settings_Report(Project_Schedules_All_Data_df, Relay_Setters_df)
        Genrate_Electrical_Prints_Report(Project_Schedules_All_Data_df)
        Genrate_Physical_Prints_Report(Project_Schedules_All_Data_df)

    if DT.date.today().weekday() == 2:
        try:
            Material_Data_df = Excel_to_Pandas(Material_Data_Filename)
        except:
            logger.error('Can not find Project Data file')
            raise
        Genrate_Matrial_Report(Material_Data_df, Project_Schedules_All_Data_df)
    Genrate_Resource_Plan(Project_Schedules_All_Data_df, budget_item_df)



if __name__ == "__main__":
    """ This is executed when run from the command line """
    # Setup Logging
    logger = logging.getLogger('root')
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(logging.DEBUG)

    main()