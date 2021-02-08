"""This module filters and creates task

This module is used to

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredtext formatting, including
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

import scr.log_decorator as log_decorator
import scr.log as log
import pandas as pd
from dateutil.relativedelta import relativedelta
import datetime as dt
import scr.Pete_Maintenace_Helper

list_my_BUDGETITEMS = ['3201', '3202', '3203', '3206', '3212', '3226']

logger_obj = log.get_logger(log_file_name='log', log_sub_dir='logs_dir')


@log_decorator.log_decorator()
def create_tasks_for_precon_meetings(myprojects, schedule, create_tasks=True,
                                     task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring
    description = None
    precons_df = schedule[(schedule['Grandchild'] == 'Pre-Construction Meeting') &
                          (schedule['Schedule_Status'] == 'Active') &
                          (schedule['Percent_Complete'] <= 100) &
                          (schedule['Planned_Finish'] >= dt.datetime.now()) &
                          (schedule['Project_Status'] == 'Released')]

    outputdf = precons_df[precons_df.Project_ID.isin(list(myprojects.PETE_ID))]
    if len(outputdf) >= 1:
        outputdf.sort_values(by=['Estimated_In_Service_Date'])
        description = task_yaml['create_tasks_for_precon_meetings']['description']
        duedate = dt.datetime.today() + dt.timedelta(hours=task_yaml['create_tasks_for_precon_meetings']['due'])
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate,
                                                    task_yaml['create_tasks_for_precon_meetings']['tag'])
    return description


@log_decorator.log_decorator()
def create_tasks_for_waterfalls(scheduledf, create_tasks=True,
                                task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring
    # This filters Waterfall schedules that are in draft of Released projects
    description = None
    pmo_df = scheduledf[(scheduledf['Grandchild'] == 'Waterfall Start') &
                        (scheduledf['Program_Manager'] == 'Michael Howard') |
                        (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    all_projects_df = scheduledf[(scheduledf['Program_Manager'] == 'Michael Howard') |
                                 (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    all_projects_df = all_projects_df.drop_duplicates(subset=['PETE_ID'])
    pmo_df = pmo_df.drop_duplicates(subset=['PETE_ID'])

    outputdf = all_projects_df.loc[~all_projects_df['PETE_ID'].isin(pmo_df['PETE_ID'])]

    outputdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(outputdf) >= 1:
        description = task_yaml['create_tasks_for_waterfalls']['baseline']['description']
        duedate = dt.datetime.today() + dt.timedelta(hours=task_yaml['create_tasks_for_waterfalls']['baseline']['due'])
        tag = task_yaml['create_tasks_for_waterfalls']['baseline']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate, tag)

    waterfall_start_df = scheduledf[(scheduledf['Schedule_Function'] == 'PMO') &
                                    (scheduledf['Program_Manager'] == 'Michael Howard') &
                                    (scheduledf['Grandchild'] == 'Waterfall Start')]

    waterfall_finish_df = scheduledf[(scheduledf['Schedule_Function'] == 'PMO') &
                                     (scheduledf['Program_Manager'] == 'Michael Howard') &
                                     (scheduledf['Grandchild'] == 'Waterfall Finish')]

    waterfall_start_df.reset_index(drop=True)
    waterfall_finish_df.reset_index(drop=True)
    outputdf = waterfall_start_df.loc[
        waterfall_start_df['Start_Date'].values > waterfall_finish_df['Start_Date'].values]

    if len(outputdf) >= 1:
        description = task_yaml['create_tasks_for_waterfalls']['Finish_b4_Start']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_waterfalls']['Finish_b4_Start']['due'])
        tag = task_yaml['create_tasks_for_waterfalls']['Finish_b4_Start']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate, tag)

    outputdf = waterfall_finish_df
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
        description = task_yaml['create_tasks_for_waterfalls']['wrong_ESID']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_waterfalls']['wrong_ESID']['due'])
        tag = task_yaml['create_tasks_for_waterfalls']['wrong_ESID']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate, tag)
    return description


@log_decorator.log_decorator()
def create_task_for_final_engineering_with_draft_schedules(scheduledf, create_tasks=True,
                                                           task_yaml=scr.Pete_Maintenace_Helper.read_yaml(
                                                               'tasks.yaml')):
    # TODO Create Docstring
    # This filters Waterfall schedules that are in draft of Released projects
    description = None


    released_df = scheduledf[(scheduledf['PROJECTSTATUS'] == 'Released') &
                             (scheduledf['Child'] == 'Construction Summary') &
                             (scheduledf['Start_Date'] <= pd.to_datetime(dt.datetime.today().date() + relativedelta(
                                months=+6))) &
                             ~(scheduledf['Project_Category'].isin(['ROW', 'RELO'])) &
                             (scheduledf['Region_Name'] == 'METRO WEST') |
                             (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    engschedule_df = scheduledf[(scheduledf['Schedule_Function'] == 'Transmission Engineering')]

    outputdf = released_df[~released_df['PETE_ID'].isin(engschedule_df['PETE_ID'])]
    outputdf = outputdf.drop_duplicates(subset='PETE_ID', keep="first")
    outputdf.sort_values(by=['Estimated_In_Service_Date'])
    if len(outputdf) >= 1:
        description = task_yaml['create_task_for_final_engineering_with_draft_schedules']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_task_for_final_engineering_with_draft_schedules']['due'])
        tag = task_yaml['create_task_for_final_engineering_with_draft_schedules']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate, tag)
    return description


@log_decorator.log_decorator()
def create_task_for_released_projects_missing_construnction_ready_date(scheduledf, create_tasks=True,
                                                                       task_yaml=scr.Pete_Maintenace_Helper.read_yaml(
                                                                           'tasks.yaml')):
    # TODO Create Docstring
    # This filters Waterfall schedules that are in draft of Released projects

    filterdf = scheduledf[(scheduledf['Estimated_In_Service_Date'] <= dt.datetime.today() + relativedelta(months=+6)) &
                          (scheduledf['Schedule_Function'] == 'Transmission Engineering') &
                          (pd.isnull(scheduledf['PLANNEDCONSTRUCTIONREADY'])) &
                          (scheduledf['Program_Manager'] == 'Michael Howard') |
                          (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    filterdf = filterdf.drop_duplicates(subset=['PETE_ID'])

    filterdf.sort_values(by=['Estimated_In_Service_Date'])
    if len(filterdf) >= 1:
        description = task_yaml['create_task_for_released_projects_missing_construnction_ready_date']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_task_for_released_projects_missing_construnction_ready_date']['due'])
        tag = task_yaml['create_task_for_released_projects_missing_construnction_ready_date']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)
    return create_tasks


@log_decorator.log_decorator()
def create_task_for_eisd_before_energiztion(scheduledf, create_tasks=True,
                                            task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring

    description = None
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Project Energization') &
                          (scheduledf['Program_Manager'] == 'Michael Howard') &
                          (scheduledf['Estimated_In-Service_Date'] < scheduledf['Finish_Date']) &
                          (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]

    filterdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(filterdf) >= 1:
        description = task_yaml['create_task_for_eisd_before_energiztion']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_task_for_eisd_before_energiztion']['due'])
        tag = task_yaml['create_task_for_eisd_before_energiztion']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)
    return description


@log_decorator.log_decorator()
def create_tasks_for_engineering_activities_start_dates(scheduledf, create_tasks=True,
                                                        task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring
    description = None
    # This code filters out the start dates for TE activities and creates tasks
    ed_df = scheduledf[(scheduledf['Grandchild'] == 'Electrical Design') &
                       (scheduledf['Start_Date'] + (
                              scheduledf['Finish_Date'] - scheduledf['Start_Date']) / 2 <= dt.datetime.today()) &
                       (scheduledf[r'Start_Date_Planned\Actual'] != 'A') &
                       (scheduledf['Finish_Date'] >= dt.datetime.today()) &
                       (scheduledf['Program_Manager'] == 'Michael Howard') |
                       (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    pd_df = scheduledf[(scheduledf['Grandchild'] == 'Physical Design') &
                       (scheduledf['Start_Date'] + (scheduledf['Finish_Date'] - scheduledf[
                          'Start_Date']) / 2 <= dt.datetime.today()) &
                       (scheduledf[r'Start_Date_Planned\Actual'] != 'A') &
                       (scheduledf['Finish_Date'] >= dt.datetime.today()) &
                       (scheduledf['Program_Manager'] == 'Michael Howard') |
                       (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    fd_df = scheduledf[(scheduledf['Grandchild'] == 'Foundation Design') &
                       (scheduledf['Start_Date'] + (scheduledf['Finish_Date'] - scheduledf[
                          'Start_Date']) / 2 <= dt.datetime.today()) &
                       (scheduledf[r'Start_Date_Planned\Actual'] != 'A') &
                       (scheduledf['Finish_Date'] >= dt.datetime.today()) &
                       (scheduledf['Program_Manager'] == 'Michael Howard') |
                       (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    filterdf = ed_df[~ed_df['PETE_ID'].isin(pd_df['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(fd_df['PETE_ID'])]

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_start_dates']['Electrical']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_start_dates']['Electrical']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_start_dates']['Electrical']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    filterdf = pd_df[~pd_df['PETE_ID'].isin(ed_df['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(fd_df['PETE_ID'])]

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_start_dates']['Physical']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_start_dates']['Physical']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_start_dates']['Physical']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    filterdf = fd_df[~fd_df['PETE_ID'].isin(ed_df['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(pd_df['PETE_ID'])]

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_start_dates']['Foundation']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_start_dates']['Foundation']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_start_dates']['Foundation']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    filterdf = fd_df[fd_df['PETE_ID'].isin(ed_df['PETE_ID'])]
    # filterdf = pd.merge(pd_df[pd_df['PETE_ID'].isin(ed_df['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_start_dates']['TE']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_start_dates']['TE']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_start_dates']['TE']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    filterdf = ed_df[ed_df['PETE_ID'].isin(pd_df['PETE_ID'])]
    # filterdf = pd.merge(pd_df[pd_df['PETE_ID'].isin(ed_df['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_start_dates']['TE']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_start_dates']['TE']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_start_dates']['TE']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    filterdf = fd_df[fd_df['PETE_ID'].isin(pd_df['PETE_ID'])]
    # filterdf = pd.merge(pd_df[pd_df['PETE_ID'].isin(ed_df['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_start_dates']['TE']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_start_dates']['TE']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_start_dates']['TE']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    return description


@log_decorator.log_decorator()
def create_tasks_for_engineering_activities_finish_dates(scheduledf, create_tasks=True,
                                                         task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring
    # This code filters out the finish dates for TE activities and creates tasks
    description = None
    ed_df = scheduledf[(scheduledf['Grandchild'] == 'Electrical Design') &
                       (scheduledf['Finish_Date'] <= dt.datetime.today() - dt.timedelta(days=5)) &
                       (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]

    pd_df = scheduledf[(scheduledf['Grandchild'] == 'Physical Design') &
                       (scheduledf['Finish_Date'] <= dt.datetime.today() - dt.timedelta(days=5)) &
                       (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]

    fd_df = scheduledf[(scheduledf['Grandchild'] == 'Foundation Design') &
                       (scheduledf['Finish_Date'] <= dt.datetime.today() - dt.timedelta(days=5)) &
                       (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]

    filterdf = ed_df[~ed_df['PETE_ID'].isin(pd_df['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(fd_df['PETE_ID'])]
    # Electrical
    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_finish_dates']['Electrical']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_finish_dates']['Electrical']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_finish_dates']['Electrical']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    filterdf = pd_df[~pd_df['PETE_ID'].isin(ed_df['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(fd_df['PETE_ID'])]
    # Physical
    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_finish_dates']['Physical']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_finish_dates']['Physical']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_finish_dates']['Physical']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    filterdf = fd_df[~fd_df['PETE_ID'].isin(ed_df['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(pd_df['PETE_ID'])]
    # Foundation
    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_finish_dates']['Foundation']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_finish_dates']['Foundation']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_finish_dates']['Foundation']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    filterdf = fd_df[fd_df['PETE_ID'].isin(ed_df['PETE_ID'])]
    # filterdf = pd.merge(pd_df[pd_df['PETE_ID'].isin(ed_df['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_finish_dates']['TE']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_finish_dates']['TE']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_finish_dates']['TE']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    filterdf = fd_df[fd_df['PETE_ID'].isin(pd_df['PETE_ID'])]
    # filterdf = pd.merge(pd_df[pd_df['PETE_ID'].isin(ed_df['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_finish_dates']['TE']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_finish_dates']['TE']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_finish_dates']['TE']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    filterdf = ed_df[ed_df['PETE_ID'].isin(pd_df['PETE_ID'])]
    # filterdf = pd.merge(pd_df[pd_df['PETE_ID'].isin(ed_df['PETE_ID'])], filterdf, how='right')

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_engineering_activities_finish_dates']['TE']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_engineering_activities_finish_dates']['TE']['due'])
        tag = task_yaml['create_tasks_for_engineering_activities_finish_dates']['TE']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    return description


@log_decorator.log_decorator()
def create_tasks_for_construncction_task_request_approval(scheduledf, create_tasks=True,
                                                          task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring
    description = None
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Construction Task Request Approval') &
                          (scheduledf['Finish_Date'] <= dt.datetime.today() - dt.timedelta(days=5)) &
                          (scheduledf[r'Finish_Date_Planned\Actual'] != 'A') &
                          (scheduledf['Program_Manager'] == 'Michael Howard')]

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_construncction_task_request_approval']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_construncction_task_request_approval']['due'])
        tag = task_yaml['create_tasks_for_construncction_task_request_approval']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)
    return description


@log_decorator.log_decorator()
def create_tasks_for_design_book_issued(scheduledf, create_tasks=True,
                                        task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring
    description = None
    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Complete Design Book Issued') &
                          (scheduledf['Finish_Date'] <= dt.datetime.today() - dt.timedelta(days=5)) &
                          (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]
    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_for_design_book_issued']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_for_design_book_issued']['due'])
        tag = task_yaml['create_tasks_for_design_book_issued']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)
    return description


@log_decorator.log_decorator()
def create_tasks_for_wa(scheduledf, create_tasks=True,
                        task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring
    filterdf = scheduledf[(pd.isnull(scheduledf['FIMSTATUS'])) &
                          (scheduledf['PLANNEDCONSTRUCTIONREADY'] <= dt.datetime.today() - dt.timedelta(days=5)) &
                          (scheduledf[r'Finish_Date_Planned\Actual'] != 'A') &
                          (scheduledf['Program_Manager'] == 'Michael Howard') |
                          (scheduledf['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    description = task_yaml['create_tasks_for_wa']['description']
    duedate = dt.datetime.today() + dt.timedelta(
        hours=task_yaml['create_tasks_for_wa']['due'])
    tag = task_yaml['create_tasks_for_wa']['tag']
    if create_tasks:
        scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)
    return description


@log_decorator.log_decorator()
def create_task_for_relay_settings(scheduledf, create_tasks=True,
                                   task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring
    # This filters Prints with finished dates past 5 days past today without an actual finish
    # TODO Convert Filter to Query
    description = None

    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Create Relay Settings') &
                          (scheduledf['Finish_Date'] <= dt.datetime.today() - dt.timedelta(days=5)) &
                          (scheduledf[r'Finish_Date_Planned\Actual'] != 'A')]

    filterdf = filterdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(filterdf) >= 1:
        description = task_yaml['create_task_for_relay_settings']['finish']['description']
        duedate = dt.datetime.today() + dt.timedelta(hours=task_yaml['create_task_for_relay_settings']['finish']['due'])
        tag = task_yaml['create_task_for_relay_settings']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    filterdf = scheduledf[(scheduledf['Grandchild'] == 'Create Relay Settings') &
                          (scheduledf['Start_Date'] + (scheduledf['Finish_Date'] - scheduledf[
                              'Start_Date']) / 2 <= dt.datetime.today()) &
                          (scheduledf[r'Start_Date_Planned\Actual'] != 'A') &
                          (scheduledf['Finish_Date'] >= dt.datetime.today())]
    filterdf = filterdf.sort_values(by=['Estimated_In_Service_Date'])

    if len(filterdf) >= 1:
        description = task_yaml['create_task_for_relay_settings']['start']['description']
        duedate = dt.datetime.today() + dt.timedelta(hours=task_yaml['create_task_for_relay_settings']['start']['due'])
        tag = task_yaml['create_task_for_relay_settings']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)

    return description


@log_decorator.log_decorator()
def create_task_for_add_wa_to_schedule(scheduledf, myprojectbudgetitmes, create_tasks=True,
                                       task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring
    # This filters Prints with finished dates past 5 days past today without an actual finish
    # TODO Convert Filter to Query
    description = None
    filterdf = scheduledf[(pd.isnull(scheduledf['Schedule_Function'])) &
                          (scheduledf['PROJECTSTATUS'] == 'Released') &
                          (scheduledf['BUDGETITEMNUMBER'].isin(myprojectbudgetitmes))]
    outputdf = filterdf
    outputdf = outputdf.sort_values(by=['Estimated_In_Service_Date'])
    if len(outputdf) >= 1:
        description = task_yaml['create_task_for_add_wa_to_schedule']['description']
        duedate = dt.datetime.today() + dt.timedelta(hours=task_yaml['create_task_for_add_wa_to_schedule']['due'])
        tag = task_yaml['create_task_for_add_wa_to_schedule']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate, tag)
    return description


# def Complete_Task():
@log_decorator.log_decorator()
def create_task_for_missing_tiers(df, create_tasks=True,
                                  task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring
    # TODO Convert Filter to Query
    description = None
    filterdf = df[(pd.isnull(df['Project_Tier'])) &
                  (df['Program_Manager'] == 'Michael Howard')]

    outputdf = filterdf.drop_duplicates(subset=['PETE_ID'])
    outputdf = outputdf.sort_values(by=['Estimated_In_Service_Date'])
    if len(outputdf) >= 1:
        description = task_yaml['create_task_for_missing_tiers']['description']
        duedate = dt.datetime.today() + dt.timedelta(hours=task_yaml['create_task_for_missing_tiers']['due'])
        tag = task_yaml['create_task_for_missing_tiers']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(outputdf, description, duedate, tag)
    return description


@log_decorator.log_decorator()
def create_tasks_toa_outside_waterfalls(df, create_tasks=True,
                                        task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
    # TODO Create Docstring
    description = None
    duedate = None
    tag = None
    # TODO Convert Filter to Query
    active_outage_df = df[(df['Schedule_Function'] == 'TOA') &
                          (df['Program_Manager'] == 'Michael Howard') &
                          (df['COMMENTS'].str.contains('Oncor Status: SUBMITTED')) |
                          (df['COMMENTS'].str.contains('Oncor Status: APPROVED')) |
                          (df['COMMENTS'].str.contains('Oncor Status: ACTIVE')) |
                          (df['COMMENTS'].str.contains('Oncor Status: COMPLETED'))]

    water_start_df = df[(df['Grandchild'] == 'Waterfall Start') &
                        (df['Program_Manager'] == 'Michael Howard') |
                        (df['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    water_finish_df = df[(df['Grandchild'] == 'Waterfall Finish') &
                         (df['Program_Manager'] == 'Michael Howard') |
                         (df['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))]

    water_start_df = water_start_df.rename(columns={"Finish_Date": "WaterFall_Start"})
    water_finish_df = water_finish_df.rename(columns={"Finish_Date": "WaterFall_Finish"})

    active_outage_df = active_outage_df.sort_values(by=['Start_Date'])

    filterdf = pd.merge(active_outage_df, water_start_df[['PETE_ID', 'WaterFall_Start']], on='PETE_ID', how='left')
    filterdf = pd.merge(filterdf, water_finish_df[['PETE_ID', 'WaterFall_Finish']], on='PETE_ID', how='left')

    filterdfs = filterdf[filterdf['Start_Date'].le(filterdf['WaterFall_Start'])]
    filterdff = filterdf[filterdf['Finish_Date'].ge(filterdf['WaterFall_Finish'])]

    filterdf = pd.concat([filterdfs, filterdff], ignore_index=True)
    filterdf = filterdf.drop_duplicates(subset=['PETE_ID'], keep='first')

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_toa_outside_waterfalls']['description']
        duedate = dt.datetime.today() + dt.timedelta(hours=task_yaml['create_tasks_toa_outside_waterfalls']['due'])
        tag = task_yaml['create_tasks_toa_outside_waterfalls']['tag']
    if create_tasks:
        scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)
    return description


@log_decorator.log_decorator()
def create_tasks_toa_no_active(df, create_tasks=True,
                               task_yaml=scr.Pete_Maintenace_Helper.read_yaml('tasks.yaml')):
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
                        (df['Finish_Date'].le(
                            pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=120)))) &
                        (df['Program_Manager'] == 'Michael Howard') |
                        (df['BUDGETITEMNUMBER'].isin(list_my_BUDGETITEMS))
                        ]

    no_toa_needed_df = df[(df['Grandchild'] == 'No TOA Request Needed')]

    filterdf = my_projects_df[~my_projects_df['PETE_ID'].isin(active_outage_df['PETE_ID'])]
    filterdf = filterdf[~filterdf['PETE_ID'].isin(no_toa_needed_df['PETE_ID'])]

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_toa_no_active']['description']
        duedate = dt.datetime.today() + dt.timedelta(hours=task_yaml['create_tasks_toa_no_active']['due'])
        tag = task_yaml['create_tasks_toa_no_active']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)
    return description


@log_decorator.log_decorator()
def create_tasks_construnction_summary_before_construnction_ready(df, create_tasks=True,
                                                                  task_yaml=scr.Pete_Maintenace_Helper.read_yaml(
                                                                      'tasks.yaml')):
    # TODO Create Docstring
    description = None
    # TODO Convert Filter to Query
    cs_df = df[(df['Parent'] == 'Construction Summary') &
               (df['Region_Name'] == 'METRO WEST') &
               (df['Start_Date'].le(pd.to_datetime(df['PLANNEDCONSTRUCTIONREADY']))) &
               (df[r'Start_Date_Planned\Actual'] == 'P')]

    cs_df = cs_df.sort_values(by=['Start_Date'], ascending=True)
    filterdf = cs_df.drop_duplicates(subset=['PETE_ID'], keep='first')

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_construnction_summary_before_construnction_ready']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_construnction_summary_before_construnction_ready']['due'])
        tag = task_yaml['create_tasks_construnction_summary_before_construnction_ready']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)
    return description


@log_decorator.log_decorator()
def create_tasks_station_design_finish_after_construction_ready_date(df, create_tasks=True,
                                                                     task_yaml=scr.Pete_Maintenace_Helper.read_yaml(
                                                                         'tasks.yaml')):
    # TODO Create Docstring
    description = None
    # TODO Convert Filter to Query
    cs_df = df[(df['Grandchild'] == 'Electrical Design') &
               (df['Region_Name'] == 'METRO WEST') &
               (df['Finish_Date'].lt(pd.to_datetime(df['PLANNEDCONSTRUCTIONREADY']))) &
               (df[r'Finish_Date_Planned\Actual'] == 'P')]

    cs1_df = df[(df['Grandchild'] == 'Physical Design') &
                (df['Region_Name'] == 'METRO WEST') &
                (df['Finish_Date'].lt(pd.to_datetime(df['PLANNEDCONSTRUCTIONREADY']))) &
                (df[r'Finish_Date_Planned\Actual'] == 'P')
                ]

    cs_df = pd.concat([cs_df, cs1_df])

    cs_df = cs_df.sort_values(by=['Start_Date'], ascending=True)
    filterdf = cs_df.drop_duplicates(subset=['PETE_ID'], keep='first')

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_station_design_finish_after_construction_ready_date']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_station_design_finish_after_construction_ready_date']['due'])
        tag = task_yaml['create_tasks_station_design_finish_after_construction_ready_date']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)
    return description


@log_decorator.log_decorator()
def create_tasks_line_design_finish_after_construction_ready_date(df, create_tasks=True,
                                                                  task_yaml=scr.Pete_Maintenace_Helper.read_yaml(
                                                                      'tasks.yaml')):
    # TODO Create Docstring
    description = None
    # TODO Convert Filter to Query
    cs_df = df[(df['Grandchild'] == 'Complete Design Books Issued') &
               # (df['Grandchild'] == 'Project WA Approved') &
               (df['Region_Name'] == 'METRO WEST') &
               (df['Finish_Date'].lt(pd.to_datetime(df['PLANNEDCONSTRUCTIONREADY']))) &
               (df[r'Finish_Date_Planned\Actual'] == 'P')
               ]

    cs1_df = df[(df['Grandchild'] == 'Project WA Approved') &
                (df['Region_Name'] == 'METRO WEST') &
                (df['Finish_Date'].lt(pd.to_datetime(df['PLANNEDCONSTRUCTIONREADY']))) &
                (df[r'Finish_Date_Planned\Actual'] == 'P')
                ]

    cs_df = pd.concat([cs_df, cs1_df])

    cs_df = cs_df.sort_values(by=['Start_Date'], ascending=True)
    filterdf = cs_df.drop_duplicates(subset=['PETE_ID'], keep='first')

    if len(filterdf) >= 1:
        description = task_yaml['create_tasks_line_design_finish_after_construction_ready_date']['description']
        duedate = dt.datetime.today() + dt.timedelta(
            hours=task_yaml['create_tasks_line_design_finish_after_construction_ready_date']['due'])
        tag = task_yaml['create_tasks_line_design_finish_after_construction_ready_date']['tag']
        if create_tasks:
            scr.Pete_Maintenace_Helper.create_tasks(filterdf, description, duedate, tag)
    return description
