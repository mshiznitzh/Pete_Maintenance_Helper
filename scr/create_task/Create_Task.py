"""This module filters and creates task

This module is used to

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python Pete_Maintenance_Helper.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""



import pandas as pd
from dateutil.relativedelta import relativedelta
import datetime as DT
import Pete_Maintenace_Helper

list_my_BUDGETITEMS = ['3201','3202','3203','3206', '3212', '3226']


def Create_tasks_for_Precon_meetings(myprojects, schedule):
    # TODO Create Docstring
    precons_df = schedule[(schedule['Grandchild'] == 'Pre-Construction Meeting') &
                          (schedule['Schedule_Status'] == 'Active') &
                          (schedule['Percent_Complete'] <= 100) &
                          (schedule['Planned_Finish'] >= DT.datetime.now()) &
                          (schedule['Project_Status'] == 'Released')]

    outputdf = precons_df[precons_df.Project_ID.isin(list(myprojects.PETE_ID))]

    outputdf.sort_values(by=['Estimated_In_Service_Date'])
    description = 'Check if I have an invite to ' + row['Grandchild']
    duedate = row['Planned_Finish'] - DT.timedelta(days=7)
    Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate)


def Create_tasks_for_Waterfalls(scheduledf, Create_Tasks=True):
    # TODO Create Docstring
    # This filters Waterfall schedules that are in draft of Released projects
    description = None
    PMO_DF = scheduledf[(scheduledf['Grandchild'] == 'Waterfall Start') &
                        (scheduledf['Program_Manager'] == 'Michael Howard') |
                            (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    All_projects_DF = scheduledf[(scheduledf['Program_Manager'] == 'Michael Howard')  |
                            (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    All_projects_DF = All_projects_DF.drop_duplicates(subset=['PETE_ID'])
    PMO_DF = PMO_DF.drop_duplicates(subset=['PETE_ID'])

    outputdf = All_projects_DF.loc[~All_projects_DF['PETE_ID'].isin(PMO_DF['PETE_ID'])]

    outputdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(outputdf) >= 1:
        description = 'Waterfall needs to be baselined'
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
    # TODO Create Docstring
    # This filters Waterfall schedules that are in draft of Released projects

    Releaseddf = scheduledf[(scheduledf['PROJECTSTATUS'] == 'Released') &
                            (scheduledf['Estimated_In_Service_Date'] <= DT.datetime.today() + relativedelta(months=+6)) &
                            ~(scheduledf['Project_Category'].isin(['ROW', 'RELO'])) &
                            (scheduledf['Region_Name'] == 'METRO WEST') |
                            (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS ))]

    Engscheduledf = scheduledf[(scheduledf['Schedule_Function'] == 'Transmission Engineering')]

    outputdf = Releaseddf[~Releaseddf['PETE_ID'].isin(Engscheduledf['PETE_ID'])]
    outputdf = outputdf.drop_duplicates(subset='PETE_ID', keep="first")
    outputdf.sort_values(by=['Estimated_In_Service_Date'])
    description = 'Check with Engineering on when a schedule will be finalized'
    duedate = DT.datetime.today() + DT.timedelta(hours=2)

    Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate)


def Create_task_for_Released_projects_missing_Construnction_Ready_Date(scheduledf):
    # TODO Create Docstring
    # This filters Waterfall schedules that are in draft of Released projects

    filterdf = scheduledf[(scheduledf['Schedule_Function'] == 'Transmission Engineering') &
                          (pd.isnull(scheduledf['PLANNEDCONSTRUCTIONREADY'])) &
                          (scheduledf['Program_Manager'] == 'Michael Howard') |
                            (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    filterdf = filterdf.drop_duplicates(subset=['PETE_ID'])

    filterdf.sort_values(by=['Estimated_In_Service_Date'])


    description = 'Check with Engineering on populating the construction ready date'

    duedate = DT.datetime.today() + DT.timedelta(hours=3)
    Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate)


def Create_task_for_ESID_before_Energiztion(scheduledf, Create_Tasks=True):
    # TODO Create Docstring

    description = None
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Project Energization') &
                          (scheduledf['Program_Manager'] == 'Michael Howard') &
                          (scheduledf['Estimated_In-Service_Date'] < scheduledf['Finish_Date']) &
                          (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]

    filterdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(filterdf) >= 1:
        description = 'Project Energization is after Estimated In-Service Date'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate)
    return description


def Create_tasks_for_Engineering_Activities_Start_Dates(scheduledf, Create_Tasks=True):
    # TODO Create Docstring
    description = None
    # This code filters out the start dates for TE activities and creates tasks
    EDdf = scheduledf[(scheduledf['Grandchild'] == 'Electrical Design') &
                      (scheduledf['Start_Date'] + (
                              scheduledf['Finish_Date'] - scheduledf['Start_Date']) / 2 <= DT.datetime.today()) &
                      (scheduledf[r'Start_Date_Planned\Actual'] != 'A') &
                      (scheduledf['Finish_Date'] >= DT.datetime.today()) &
                      (scheduledf['Program_Manager'] == 'Michael Howard') |
                            (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    PDdf = scheduledf[(scheduledf['Grandchild'] == 'Physical Design') &
                      (scheduledf['Start_Date'] + (scheduledf['Finish_Date'] - scheduledf[
                          'Start_Date']) / 2 <= DT.datetime.today()) &
                      (scheduledf[r'Start_Date_Planned\Actual'] != 'A') &
                      (scheduledf['Finish_Date'] >= DT.datetime.today()) &
                      (scheduledf['Program_Manager'] == 'Michael Howard') |
                            (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    FDdf = scheduledf[(scheduledf['Grandchild'] == 'Foundation Design') &
                      (scheduledf['Start_Date'] + (scheduledf['Finish_Date'] - scheduledf[
                          'Start_Date']) / 2 <= DT.datetime.today()) &
                      (scheduledf[r'Start_Date_Planned\Actual'] != 'A') &
                      (scheduledf['Finish_Date'] >= DT.datetime.today()) &
                      (scheduledf['Program_Manager'] == 'Michael Howard') |
                            (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

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
    #filterdf = pd.merge(PDdf[PDdf['PETE_ID'].isin(EDdf['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = 'Ask Engineering to update the TE schedule'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    filterdf = EDdf[EDdf['PETE_ID'].isin(PDdf['PETE_ID'])]
    #filterdf = pd.merge(PDdf[PDdf['PETE_ID'].isin(EDdf['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = 'Ask Engineering to update the TE schedule'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    filterdf = FDdf[FDdf['PETE_ID'].isin(PDdf['PETE_ID'])]
    #filterdf = pd.merge(PDdf[PDdf['PETE_ID'].isin(EDdf['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = 'Ask Engineering to update the TE schedule'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    return description


def Create_tasks_for_Engineering_Activities_Finish_Dates(scheduledf, Create_Tasks=True):
    # TODO Create Docstring
    # This code filters out the finish dates for TE activities and creates tasks
    description = None
    EDdf = scheduledf[(scheduledf['Grandchild'] == 'Electrical Design') &
                      (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                      (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]

    PDdf = scheduledf[(scheduledf['Grandchild'] == 'Physical Design') &
                      (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                      (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]

    FDdf = scheduledf[(scheduledf['Grandchild'] == 'Foundation Design') &
                      (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                      (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]

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
    #filterdf = pd.merge(PDdf[PDdf['PETE_ID'].isin(EDdf['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = 'Ask Engineering to update the TE schedule (Finish Date)'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    filterdf = FDdf[FDdf['PETE_ID'].isin(PDdf['PETE_ID'])]
    #filterdf = pd.merge(PDdf[PDdf['PETE_ID'].isin(EDdf['PETE_ID'])], filterdf, how='right')


    if len(filterdf) >= 1:
        description = 'Ask Engineering to update the TE schedule (Finish Date)'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    filterdf = EDdf[EDdf['PETE_ID'].isin(PDdf['PETE_ID'])]
    #filterdf = pd.merge(PDdf[PDdf['PETE_ID'].isin(EDdf['PETE_ID'])], filterdf, how='right')


    if len(filterdf) >= 1:
        description = 'Ask Engineering to update the TE schedule (Finish Date)'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    return description


def Create_tasks_for_Construncction_Task_Request_Approval(scheduledf, Create_Tasks=True):
    # TODO Create Docstring
    description = None
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Construction Task Request Approval') &
                          (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf[r'Finish_Date_Planned\Actual'] != 'A') &
                          (scheduledf['Program_Manager'] == 'Michael Howard')]

    if len(filterdf) >= 1:
        description = 'Ask Engineering for update on Construction Task Request Approval'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')
    return description


def Create_tasks_for_Design_Book_Issued(scheduledf):
    # TODO Create Docstring
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Complete Design Book Issued') &
                          (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]

    description = 'Ask Engineering for update on Design Book Issued'
    duedate = DT.datetime.today() + DT.timedelta(hours=5)
    Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')


def Create_tasks_for_WA(scheduledf):
    # TODO Create Docstring
    filterdf = scheduledf[(pd.isnull(scheduledf['FIMSTATUS'])) &
                          (scheduledf['PLANNEDCONSTRUCTIONREADY'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf[r'Finish_Date_Planned\Actual'] != 'A') &
                          (scheduledf['Program_Manager'] == 'Michael Howard') |
                            (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    description = 'Ask Engineering about the WA'
    duedate = DT.datetime.today() + DT.timedelta(hours=5)
    Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')
    return description


def Create_task_for_Relay_Settings(scheduledf, Create_Tasks=True):
    # TODO Create Docstring
    # This filters Prints with finished dates past 5 days past today without an actual finish
    # TODO Convert Filter to Query
    description=None

    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Create Relay Settings') &
                          (scheduledf['Finish_Date'] <= DT.datetime.today() - DT.timedelta(days=5)) &
                          (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]

    filterdf=filterdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(filterdf) >= 1:
        description = 'Check with Relay Setter on when settings are going to be issued'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Create Relay Settings') &
                              (scheduledf['Start_Date'] + (scheduledf['Finish_Date'] - scheduledf[
                                  'Start_Date']) / 2 <= DT.datetime.today()) &
                              (scheduledf[r'Start_Date_Planned\Actual'] != 'A') &
                              (scheduledf['Finish_Date'] >= DT.datetime.today())]
    filterdf = filterdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(filterdf) >= 1:
        description = 'Check with Relay Setter on when settings are going to be started'
        duedate = DT.datetime.today() + DT.timedelta(hours=8)
        if Create_Tasks:
            Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')

    return description

def Create_task_for_add_WA_to_schedule(scheduledf, myprojectbudgetitmes):
    # TODO Create Docstring
    # This filters Prints with finished dates past 5 days past today without an actual finish
    # TODO Convert Filter to Query
    filterdf = scheduledf[(pd.isnull(scheduledf['Schedule_Function'])) &
                          (scheduledf['PROJECTSTATUS'] == 'Released') &
                          (scheduledf['BUDGETITEMNUMBER'].isin(myprojectbudgetitmes))]
    outputdf = filterdf
    outputdf = outputdf.sort_values(by=['Estimated_In_Service_Date'])
    description = 'Add PETE ID to query for Schedules'
    duedate = DT.datetime.today() + DT.timedelta(hours=6)

    Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate)

#def Complete_Task():

def Create_task_for_missing_tiers(df):
    # TODO Create Docstring
    # TODO Convert Filter to Query
    filterdf = df[(pd.isnull(df['Project_Tier'])) &
                          (df['Program_Manager'] == 'Michael Howard')]

    outputdf = filterdf.drop_duplicates(subset=['PETE_ID'])
    outputdf = outputdf.sort_values(by=['Estimated_In_Service_Date'])
    description = 'Project Tier Missing'
    duedate = DT.datetime.today() + DT.timedelta(hours=6)
    Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate)

def Create_tasks_TOA_outside_Waterfalls(df, Create_Tasks=True):
    # TODO Create Docstring
    description = None
#TODO Convert Filter to Query
    active_outage_df = df[(df['Schedule_Function'] == 'TOA') &
                  (df['Program_Manager'] == 'Michael Howard') &
                  (df['COMMENTS'].str.contains('Oncor Status: SUBMITTED')) |
                  (df['COMMENTS'].str.contains('Oncor Status: APPROVED')) |
                  (df['COMMENTS'].str.contains('Oncor Status: ACTIVE')) |
                  (df['COMMENTS'].str.contains('Oncor Status: COMPLETED'))]

    Water_Start_DF = df[(df['Grandchild'] == 'Waterfall Start') &
                        (df['Program_Manager'] == 'Michael Howard') |
                        (df['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    Water_Finish_DF = df[(df['Grandchild'] == 'Waterfall Finish') &
                        (df['Program_Manager'] == 'Michael Howard') |
                        (df['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    Water_Start_DF = Water_Start_DF.rename(columns={"Finish_Date": "WaterFall_Start"})
    Water_Finish_DF = Water_Finish_DF.rename(columns={"Finish_Date": "WaterFall_Finish"})

    active_outage_df = active_outage_df.sort_values(by=['Start_Date'])

    filterdf = pd.merge(active_outage_df, Water_Start_DF[['PETE_ID', 'WaterFall_Start']], on='PETE_ID', how='left')
    filterdf = pd.merge(filterdf, Water_Finish_DF[['PETE_ID', 'WaterFall_Finish']], on='PETE_ID', how='left')

    filterdfs = filterdf[filterdf['Start_Date'].lt(filterdf['WaterFall_Start'])]
    filterdff = filterdf[filterdf['Finish_Date'].gt(filterdf['WaterFall_Finish'])]


    filterdf = pd.concat([filterdfs, filterdff], ignore_index=True)
    filterdf = filterdf.drop_duplicates(subset=['PETE_ID'], keep='first')

    if len(filterdf) >= 1:
        description = 'TOA request outside Waterfall dates'
    duedate = DT.datetime.today() + DT.timedelta(hours=8)
    if Create_Tasks:
        Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')
    return description

def Create_tasks_TOA_no_active(df, Create_Tasks=True):
    # TODO Create Docstring
    description = None
    # TODO Convert Filter to Query
    active_outage_df = df[(df['Schedule_Function'] == 'TOA') &
                          (df['Program_Manager'] == 'Michael Howard') |
                          (df['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS)) &
                          (df['COMMENTS'].str.contains('Oncor Status: SUBMITTED')) |
                          (df['COMMENTS'].str.contains('Oncor Status: APPROVED')) |
                          (df['COMMENTS'].str.contains('Oncor Status: ACTIVE')) |
                          (df['COMMENTS'].str.contains('Oncor Status: COMPLETED'))]

    my_projects_df = df[(df['Grandchild'] == 'Waterfall Start') &
                        (df['Finish_Date'].le(pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=120)))) &
                        (df['Program_Manager'] == 'Michael Howard') |
                        (df['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))
                        ]
    filterdf = my_projects_df[~my_projects_df['PETE_ID'].isin(active_outage_df['PETE_ID'])]

    if len(filterdf) >= 1:
        description = 'No Active TOA for project'
    duedate = DT.datetime.today() + DT.timedelta(hours=8)
    if Create_Tasks:
        Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')
    return description

def Create_tasks_Construnction_Summary_before_Construnction_Ready(df, Create_Tasks=True):
    # TODO Create Docstring
    description = None
#TODO Convert Filter to Query
    CS_df = df[(df['Parent'] == 'Construction Summary') &
                  (df['Region_Name'] == 'METRO WEST') &
                  (df['Start_Date'].le(pd.to_datetime(df['PLANNEDCONSTRUCTIONREADY'])))&
                  (df[r'Start_Date_Planned\Actual'] == 'P')]

    CS_df = CS_df.sort_values(by=['Start_Date'], ascending=True)
    filterdf = CS_df.drop_duplicates(subset=['PETE_ID'], keep='first')

    if len(filterdf) >= 1:
        description = 'Construction Summary before Construction Ready'
    duedate = DT.datetime.today() + DT.timedelta(hours=8)
    if Create_Tasks:
        Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')
    return description

def Create_tasks_Station_Design_Finish_after_Construction_Ready_Date(df, Create_Tasks=True):
    # TODO Create Docstring
    description = None
    # TODO Convert Filter to Query
    CS_df = df[(df['Grandchild'] == 'Electrical Design') &
               (df['Region_Name'] == 'METRO WEST') &
               (df['Finish_Date'].lt(pd.to_datetime(df['PLANNEDCONSTRUCTIONREADY']))) &
                (df[r'Finish_Date_Planned\Actual'] == 'P')]

    CS1_df = df[(df['Grandchild'] == 'Physical Design') &
               (df['Region_Name'] == 'METRO WEST') &
               (df['Finish_Date'].lt(pd.to_datetime(df['PLANNEDCONSTRUCTIONREADY']))) &
                (df[r'Finish_Date_Planned\Actual'] == 'P')
    ]

    CS_df = pd.concat([CS_df, CS1_df])

    CS_df = CS_df.sort_values(by=['Start_Date'], ascending=True)
    filterdf = CS_df.drop_duplicates(subset=['PETE_ID'], keep='first')

    if len(filterdf) >= 1:
        description = 'Design Finish after Construction Ready Date'
    duedate = DT.datetime.today() + DT.timedelta(hours=8)
    if Create_Tasks:
        Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')
    return description

def Create_tasks_Line_Design_Finish_after_Construction_Ready_Date(df, Create_Tasks=True):
    # TODO Create Docstring
    description = None
    # TODO Convert Filter to Query
    CS_df = df[(df['Grandchild'] == 'Complete Design Books Issued') &
               #(df['Grandchild'] == 'Project WA Approved') &
               (df['Region_Name'] == 'METRO WEST') &
               (df['Finish_Date'].lt(pd.to_datetime(df['PLANNEDCONSTRUCTIONREADY']))) &
               (df[r'Finish_Date_Planned\Actual'] == 'P')
    ]

    CS1_df = df[(df['Grandchild'] == 'Project WA Approved') &
               (df['Region_Name'] == 'METRO WEST') &
               (df['Finish_Date'].lt(pd.to_datetime(df['PLANNEDCONSTRUCTIONREADY']))) &
               (df[r'Finish_Date_Planned\Actual'] == 'P')
               ]

    CS_df = pd.concat([CS_df,CS1_df ])

    CS_df = CS_df.sort_values(by=['Start_Date'], ascending=True)
    filterdf = CS_df.drop_duplicates(subset=['PETE_ID'], keep='first')

    if len(filterdf) >= 1:
        description = 'Design Finish after Construction Ready Date (Line)'
    duedate = DT.datetime.today() + DT.timedelta(hours=8)
    if Create_Tasks:
        Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, 'PMH_E')
    return description