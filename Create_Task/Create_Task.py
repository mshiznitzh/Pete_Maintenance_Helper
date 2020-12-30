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

import Reports.Reports
import Pete_Maintenace_Helper

def Create_tasks_no_TOA_inside_Construnction_Summary(schedule):
    description = None

    toadf = schedule.query('Schedule_Function' == 'TOA' and
                           'COMMENTS.str.contains("SUBMITTED")' and
                           'Program_Manager' == "Michael Howard")

    CSdf = schedule.query('Schedule_Function' == 'Construction' and
                           'PARENT' == 'Construction Summary' and
                           'Program_Manager' == "Michael Howard")

    toasdf = toadf.sort_vaulues('Start_Date', axis = 0, ascending = True, na_position = 'last')
    toasdf = toasdf.drop_duplicates(PETE_ID)
    toasdf = toasdf.rename(columns={"Start_Date": "TOA_Start_Date"})

    toafdf = toadf.sort_vaulues('Finish_Date', axis = 0, ascending = True, na_position = 'last')
    toafdf = toafdf.drop_duplicates(PETE_ID)
    toafdf = toafdf.rename(columns={"Finish_Date": "TOA_Finish_Date"})

    CSsdf = CSdf.sort_vaulues('Start_Date', axis=0, ascending=True, na_position='last')
    CSsdf = CSsdf.drop_duplicates(PETE_ID)
    CSsdf = CSsdf.rename(columns={"Start_Date": "CS_Start_Date"})

    CSfdf = CSdf.sort_vaulues('Finish_Date', axis=0, ascending=True, na_position='last')
    CSfdf = CSfdf.drop_duplicates(PETE_ID)
    CSfdf = CSfdf.rename(columns={"Finish_Date": "CS_Finish_Date"})

    toadf = pd.merge(toasdf,toafdf[['PETE_ID', 'TOA_Finish_Date']], how='inner' , on = 'PETE_ID')
    toadf = pd.merge(toadf, CSsdf[['PETE_ID', 'CS_Start_Date']], how='inner', on='PETE_ID')
    toadf = pd.merge(toadf, CSfdf[['PETE_ID', 'CS_Finish_Date']], how='inner', on='PETE_ID')

    toadf = toadf.query(TOA_Start_Date <''

                        )

    return description

def Create_tasks_for_Precon_meetings(myprojects, schedule):
    # This filters Pre construnction meeting in the future of Released projects
    precons_df = schedule[(schedule['Grandchild'] == 'Pre-Construction Meeting') &
                          (schedule['Schedule_Status'] == 'Active') &
                          (schedule['Percent_Complete'] <= 100) &
                          (schedule['Planned_Finish'] >= DT.datetime.now()) &
                          (schedule['Project_Status'] == 'Released')]

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

        Pete_Maintenace_Helper.Add_Task(description, project, duedate, priority, 'PMH')
        # p.start()
    # p.join()


def Create_tasks_for_Waterfalls(scheduledf, Create_Tasks=False):
    # This filters Waterfall schedules that are in draft of Released projects
    description = None
    PMO_DF = scheduledf[(scheduledf['Schedule_Function'] == 'PMO') &
                        (scheduledf['Program_Manager'] == 'Michael Howard')]

    All_projects_DF = scheduledf[(scheduledf['Program_Manager'] == 'Michael Howard')]

    All_projects_DF = All_projects_DF.drop_duplicates(subset=['PETE_ID'])
    PMO_DF = PMO_DF.drop_duplicates(subset=['PETE_ID'])

    outputdf = All_projects_DF.loc[~All_projects_DF['PETE_ID'].isin(PMO_DF['PETE_ID'])]

    outputdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(outputdf) >= 1:
        description = 'Waterfall needs to baselined'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate)

    Waterfall_Start_DF = scheduledf[(scheduledf['Schedule_Function'] == 'PMO') &
                                    (scheduledf['Program_Manager'] == 'Michael Howard') &
                                    (scheduledf['Grandchild'] == 'Waterfall Start')]

    Waterfall_Finish_DF = scheduledf[(scheduledf['Schedule_Function'] == 'PMO') &
                                     (scheduledf['Program_Manager'] == 'Michael Howard') &
                                     (scheduledf['Grandchild'] == 'Waterfall Finish')]

    Waterfall_Start_DF.reset_index(drop=True)
    Waterfall_Finish_DF.reset_index(drop=True)
    outputdf = Waterfall_Start_DF.loc[
        Waterfall_Start_DF['Start_Date'].values > Waterfall_Finish_DF['Start_Date'].values]

    if len(outputdf) >= 1:
        description = 'Waterfall Finish is before Waterfall Start'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate)

    outputdf = Waterfall_Finish_DF
    outputdf['ESID_SEASON'] = outputdf.loc[
        pd.to_datetime(outputdf['Estimated_In-Service_Date']).dt.quarter < 3, 'ESID_SEASON'] = pd.to_numeric(
        pd.to_datetime(outputdf['Estimated_In-Service_Date']).dt.year) + .5
    outputdf['ESID_SEASON'] = outputdf.loc[
        pd.to_datetime(outputdf['Estimated_In-Service_Date']).dt.quarter >= 3, 'ESID_SEASON'] = pd.to_numeric(
        pd.to_datetime(outputdf['Estimated_In-Service_Date']).dt.year)

    outputdf['WaterFall_SEASON'] = outputdf.loc[
        pd.to_datetime(outputdf['Start_Date']).dt.quarter < 3, 'WaterFall_SEASON'] = pd.to_numeric(
        pd.to_datetime(outputdf['Start_Date']).dt.year) + .5
    outputdf['WaterFall_SEASON'] = outputdf.loc[
        pd.to_datetime(outputdf['Start_Date']).dt.quarter >= 3, 'WaterFall_SEASON'] = pd.to_numeric(
        pd.to_datetime(outputdf['Start_Date']).dt.year)

    outputdf = outputdf.loc[(
            outputdf['WaterFall_SEASON'] != outputdf['ESID_SEASON'])]

    if len(outputdf) >= 1:
        description = 'Waterfall Finish not in same season as EISD'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate)
    return description


def Create_task_for_Final_Engineering_with_draft_schedules(scheduledf):
    # This filters Waterfall schedules that are in draft of Released projects

    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Final Engineering') &
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

        Pete_Maintenace_Helper.Add_Task(description, project, duedate, priority, 'PMH')


def Create_task_for_Released_projects_missing_Construnction_Ready_Date(scheduledf):
    # This filters Waterfall schedules that are in draft of Released projects

    filterdf = scheduledf[(scheduledf['Schedule_Function'] == 'Transmission Engineering') &
                          (pd.isnull(scheduledf['PLANNEDCONSTRUCTIONREADY'])) &
                          (scheduledf['Program_Manager'] == 'Michael Howard')]

    filterdf = filterdf.drop_duplicates(subset=['PETE_ID'])

    filterdf.sort_values(by=['Estimated_In_Service_Date'])
    for index, row in filterdf.iterrows():

        description = 'Check with Engineering on populating the construction ready date'
        project = str(row['PETE_ID']) + ':' + row['Project_Name_x']
        duedate = DT.datetime.today() + DT.timedelta(hours=3)

        if row['Project_Tier'] == 1.0:
            priority = 'H'

        elif row['Project_Tier'] == 2.0:
            priority = 'M'

        elif row['Project_Tier'] == 3.0:
            priority = 'L'

        else:
            priority = None

        Pete_Maintenace_Helper.Add_Task(description, project, duedate, priority, 'PMH')
        # p.start()
    # p.join()


def Create_task_for_ESID_before_Energiztion(scheduledf, Create_Tasks=True):
    #
    description = None
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Project Energization') &
                          (scheduledf['Program_Manager'] == 'Michael Howard') &
                          (scheduledf['Estimated_In-Service_Date'] < scheduledf['Finish_Date']) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A')]

    filterdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(filterdf) >= 1:
        description = 'Project Energization is after Estimated In-Service Date'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate)
    return description


def Create_tasks_for_Engineering_Activities_Start_Dates(scheduledf, Create_Tasks=True):
    description = None
    # This code filters out the start dates for TE activities and creates tasks
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

    filterdf = EDdf[~EDdf['PETE_ID'].isin(PDdf['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(FDdf['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'Check with Engineering on if Electrical Designs were started'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    filterdf = PDdf[~PDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(FDdf['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'Check with Engineering on if Physical Designs were started'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    filterdf = FDdf[~FDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(PDdf['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'Check with Engineering on if Foundation Designs were started'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    filterdf = FDdf[FDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = pd.merge(PDdf[PDdf['PETE_ID'].isin(EDdf['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = 'Ask Engineering to update the TE schedule'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')
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
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    filterdf = PDdf[~PDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(FDdf['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'Check with Engineering on if Physical Designs were issued'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    filterdf = FDdf[~FDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(PDdf['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'Check with Engineering on if Foundation Designs were issued'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    filterdf = FDdf[FDdf['PETE_ID'].isin(EDdf['PETE_ID'])]
    filterdf = pd.merge(PDdf[PDdf['PETE_ID'].isin(EDdf['PETE_ID'])], filterdf, how='right')

    duedate = DT.datetime.today() + DT.timedelta(hours=5)
    if len(filterdf) >= 1:
        description = 'Ask Engineering to update the TE schedule (Finish Date)'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    return description


def Create_tasks_for_Construncction_Task_Request_Approval(scheduledf, Create_Tasks=True):
    description = None
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Construction Task Request Approval') &
                          (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A') &
                          (scheduledf['Program_Manager'] == 'Michael Howard')]

    if len(filterdf) >= 1:
        description = 'Ask Engineering for update on Construction Task Request Approval'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')
    return description


def Create_tasks_for_Design_Book_Issued(scheduledf):
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Complete Design Book Issued') &
                          (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A')]

    description = 'Ask Engineering for update on Design Book Issued'
    duedate = DT.datetime.today() + DT.timedelta(hours=5)
    Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')


def Create_tasks_for_WA(scheduledf):
    filterdf = scheduledf[(pd.isnull(scheduledf['FIMSTATUS'])) &
                          (scheduledf['PLANNEDCONSTRUCTIONREADY'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf['Finish_Date_Planned\Actual'] != 'A') &
                          (scheduledf['Program_Manager'] == 'Michael Howard')]

    description = 'Ask Engineering about the WA'
    duedate = DT.datetime.today() + DT.timedelta(hours=5)
    Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')
    return description


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
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

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
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    return description

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

        Pete_Maintenace_Helper.Add_Task(description, project, duedate, priority, 'PMH')

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

        Pete_Maintenace_Helper.Add_Task(description, project, duedate, priority, 'PMH')