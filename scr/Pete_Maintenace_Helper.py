#!/usr/bin/env python3
"""The core module of the Pete Helper Project

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

# TODO: update Docstring

__author__ = "MiKe Howard"
__version__ = "0.1.0"
__license__ = "MIT"

import time
import scr.log_decorator as log_decorator
import scr.log as log
from taskw import TaskWarrior
import pandas as pd
import glob
import os
import datetime as dt
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from subprocess import Popen, PIPE
import scr.create_task.Create_Task as ct
import scr.Reports.Reports as Reports
import inspect

import multiprocessing
import concurrent.futures
import functools
import yaml

logger_obj = log.get_logger(log_file_name='log', log_sub_dir='logs_dir')


@log_decorator.log_decorator()
def read_yaml(filename, path='./configs'):
    old_path = change_working_path(path)
    with open(filename) as file:
        yaml_content = yaml.safe_load(file)
    change_working_path(old_path)
    return yaml_content


# OS Functions


@log_decorator.log_decorator()
def filesearch(word=""):
    # TODO Create Docstring
    """Returns a list with all files with the word/extension in it"""

    file = []
    for f in glob.glob("*"):
        if word[0] == ".":
            if f.endswith(word):
                file.append(f)

        elif word in f:
            file.append(f)
    logger_obj.debug(file)
    return file


@log_decorator.log_decorator()
def change_working_path(path):
    # TODO Create Docstring
    # Check if New path exists
    logger_obj.debug('Current path is ' + str(os.getcwd()))
    old_path = os.getcwd()
    if os.path.exists(path):
        # Change the current working Directory
        try:
            os.chdir(path)  # Change the working directory
        except OSError:
            logger_obj.error("Can't change the Current Working Directory", exc_info=True)
    else:
        logger_obj.error("Can't change the Current Working Directory because this path doesn't exits")
    return old_path


# Pandas Functions


@log_decorator.log_decorator()
def excel_to_pandas(filename, check_update=False):
    # TODO Create Docstring

    df = []
    if check_update:
        timestamp = dt.datetime.fromtimestamp(Path(filename).stat().st_mtime)
        if dt.datetime.today().date() != timestamp.date():
            root = tk.Tk()
            root.withdraw()
            filename = filedialog.askopenfilename(title=' '.join(['Select file for', filename]))

    try:
        df = pd.read_excel(filename, sheet_name=None)
        df = pd.concat(df, axis=0, ignore_index=True)
    except:
        logger_obj.error("Error importing file " + filename, exc_info=True)

    df = cleanup_dataframe(df)
    logger_obj.debug(df.info(verbose=True))
    return df


@log_decorator.log_decorator()
def cleanup_dataframe(df):
    # TODO Create Docstring

    logger_obj.debug(df.info(verbose=True))
    # Remove whitespace on both ends of column headers
    df.columns = df.columns.str.strip()

    # Replace whitespace in column header with _
    df.columns = df.columns.str.replace(' ', '_')

    return df


@log_decorator.log_decorator()
def create_tasks(df, description, duedate, tag='PMH'):
    # TODO Create Docstring
    df = df.sort_values(by=['Estimated_In_Service_Date'])
    with concurrent.futures.ThreadPoolExecutor() as executor:
    #with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        for index, row in df.iterrows():

            logger_obj.info(str(row['PETE_ID']))

            project = str(row['PETE_ID']) + ':' + str(row['Project_Name_y'])

            if row['Project_Tier'] == 1.0:
                priority = 'H'

            elif row['Project_Tier'] == 2.0:
                priority = 'M'

            elif row['Project_Tier'] == 3.0:
                priority = 'L'

            else:
                priority = None

            # add_task(description, project, duedate, priority, tag)

            # with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            patrial_add_task = functools.partial(add_task, description, project, duedate, priority)
            executor.submit(patrial_add_task, [tag])
        #     executor.map(patrial_Add_Task, [tag])
        # t = threading.Thread(target=add_task, args=(description, project, duedate, priority, tag,))
        # t.start()
        #  t.join()


@log_decorator.log_decorator()
def check_for_task(description, project):
    # TODO Create Docstring

    description = str(description)
    project = str(project)
    logger_obj.debug(description)
    logger_obj.debug(project)
    tw = TaskWarrior()
    tasks = tw.load_tasks()
    df_pending = pd.DataFrame(tasks['pending'])
    df_completed = pd.DataFrame(tasks['completed'])
    # if (description in df_pending.to_numpy()) and (project in df_pending.to_numpy()):
    try:
        return df_pending[(df_pending['description'] == description) & (df_pending['project'].apply(str) == project)][
            'id'].item()
    except:
        logger_obj.info('Not found in pending')
    # elif (description in df_completed.values) and project in df_completed.values:
    try:
        return df_completed[
            (df_completed['description'] == description) & (df_completed['project'].apply(str) == str(project))][
            'id'].item()
    except:
        logger_obj.info('Not found in completed')

    return 0


@log_decorator.log_decorator()
def add_task(description, project, duedate, priority=None, tag=None):
    # TODO Create Docstring
    logger_obj.debug(tag)
    task_id = check_for_task(description, project)
    if task_id == 0:
        tw = TaskWarrior()
        task = tw.task_add(description=description, tags=tag, priority=priority, project=project, due=duedate)
        logger_obj.debug('I have created task ' + str(task))
        task_id = task['id']

    elif task_id > 0:
        # Task exist update
        update_task(task_id, 'due', duedate)

    if priority is not None:
        update_task(task_id, 'priority', priority)

    if tag is not None:
        update_task(task_id, 'tags', tag)


@log_decorator.log_decorator()
def update_task(task_id, attribute, value):
    # TODO Create Docstring

    logger_obj.info(task_id)
    logger_obj.info("attribute = " + attribute)
    logger_obj.info(value)
    tw = TaskWarrior()
    task_id, task = tw.get_task(id=task_id)
    logger_obj.info(task)



    for attempt in range(9):
        try:
            if attribute not in task or task[attribute] != value:
                task[attribute] = value
                logger_obj.debug("Setting " + attribute + " to " + str(value))
                tw.task_update(task)
        except:
            logger_obj.exception('Retry update - ' + str(attempt))
        else:
            break
    else:
        logger_obj.debug('Failed to Update task')

    # try:
    #     if task[attribute] != value:
    #         task[attribute] = value
    #         logger_obj.debug("Setting " + attribute + " to " + value)
    #         tw.task_update(task)
    # except KeyError:
    #     logger_obj.info("Attribute has not been set so we are adding it")
    #     task[attribute] = value
    #     tw.task_update(task)

    logger_obj.info(task)


@log_decorator.log_decorator()
def main():
    # TODO Create Docstring
    file_yaml = read_yaml('files.yaml', './configs')
    project_data_filename = file_yaml['Project_Data_Spreadsheet']['filename']

    # project_data_filename='All Project Data Report Metro West or Mike.xlsx'
    schedules_filename = file_yaml['Schedules_Spreadsheet']['filename']
    budget_item_filename = file_yaml['Budget_Item_Spreadsheet']['filename']
    relay_setters_filename = file_yaml['Relay_Setters_Spreadsheet']['filename']
    material_data_filename = file_yaml['Material_Data_Spreadsheet']['filename']

    myprojectbudgetitmes = ['00003212', '00003201', '00003203', '00003206', '00003226']

    """ Main entry point of the app """
    change_working_path('./Data')
    try:
        project_data_df = excel_to_pandas(project_data_filename, True)
    except:
        logger_obj.error('Can not find Project Data file')
        raise

    try:
        project_schedules_df = excel_to_pandas(schedules_filename, True)
    except:
        logger_obj.error('Can not find Schedule Data file')
        raise

    # try:
    #    budget_item_df = excel_to_pandas(budget_item_filename)
    # except:
#   logger_obj.error('Can not find Budget Item Data file')

    try:
        relay_setters_df = excel_to_pandas(relay_setters_filename)
    except:
        logger_obj.error('Can not find Relay Setters Data file')

    project_schedules_all_data_df = pd.merge(project_schedules_df, project_data_df, on='PETE_ID', sort=False,
                                             how='outer')

    # myprojectsdf.to_csv('myprojects.csv')
    project_schedules_all_data_df.to_csv('scheduledf.csv')

    # res = Popen('tasks=$(task tag=PMH _ids) && task delete $tasks', shell=True, stdin=PIPE)
    # res.stdin.write(b'a\n')
    # res.stdin.flush()
    # res.stdin.close()
    # res = Popen('task sync', shell=True, stdin=PIPE)
    # res.wait()
    # res.stdin.close()

    # Return the day of the week as an integer, where Monday is 0 and Sunday is 6
    # if dt.date.today().weekday() == 3:
    #     res = Popen('tasks=$(task tag=PMH_E _ids) && task delete $tasks', shell=True, stdin=PIPE)
    #     res.stdin.write(b'a\n')
    #     res.stdin.flush()
    #     res.wait()
    #     res.stdin.close()
    #     res = Popen('task sync', shell=True, stdin=PIPE)
    #     res.stdin.flush()
    #     res.wait()
    #     res.stdin.close()

    # Create_tasks_for_Precon_meetings(project_schedules_all_data_df)
    ct.create_task_for_final_engineering_with_draft_schedules(project_schedules_all_data_df)
    ct.create_task_for_released_projects_missing_construnction_ready_date(project_schedules_all_data_df)
    ct.create_task_for_relay_settings(project_schedules_all_data_df)
    ct.create_tasks_for_engineering_activities_start_dates(project_schedules_all_data_df)
    ct.create_tasks_for_engineering_activities_finish_dates(project_schedules_all_data_df)
    ct.create_task_for_relay_settings(project_schedules_all_data_df)

    ct.create_task_for_eisd_before_energiztion(project_schedules_all_data_df)
    ct.create_task_for_add_wa_to_schedule(project_schedules_all_data_df, myprojectbudgetitmes)
    ct.create_tasks_for_waterfalls(project_schedules_all_data_df)
    ct.create_task_for_missing_tiers(project_schedules_all_data_df)
    ct.create_tasks_toa_outside_waterfalls(project_schedules_all_data_df)
    ct.create_tasks_toa_no_active(project_schedules_all_data_df)
    ct.create_tasks_construnction_summary_before_construnction_ready(project_schedules_all_data_df)
    ct.create_tasks_line_design_finish_after_construction_ready_date(project_schedules_all_data_df)
    ct.create_tasks_station_activities_conflict(project_schedules_all_data_df)

    res = Popen('task sync', shell=True, stdin=PIPE)
    res.wait()
    res.stdin.close()

    if dt.date.today().weekday() == 4:
        Reports.Genrate_Relay_Settings_Report(project_schedules_all_data_df, relay_setters_df)
        Reports.Genrate_Electrical_Prints_Report(project_schedules_all_data_df)
        Reports.Genrate_Physical_Prints_Report(project_schedules_all_data_df)

    if dt.date.today().weekday() == 4:
        try:
            material_data_df = excel_to_pandas(material_data_filename)
        except:
            logger_obj.error('Can not find Project Data file')
            raise
        Reports.Genrate_Matrial_Report(material_data_df, project_schedules_all_data_df)
    # Reports.Genrate_Resource_Plan(project_schedules_all_data_df, budget_item_df)


if __name__ == "__main__":
    main()
