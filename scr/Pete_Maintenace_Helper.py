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


import scr.log_decorator as log_decorator
import scr.log as log
import logging
from logzero import logger
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


import multiprocessing
import concurrent.futures
import functools
import yaml

@log_decorator.log_decorator()
def read_yaml(filename, path='./configs'):
    old_path = Change_Working_Path(path)
    with open(filename) as file:
        yaml_content = yaml.safe_load(file)
    Change_Working_Path(old_path)
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
            #return file
    logger.debug(file)
    return file

@log_decorator.log_decorator()
def Change_Working_Path(path):
    # TODO Create Docstring
    # Check if New path exists
    logger.info('Current path is ' + str(os.getcwd()))
    old_path=os.getcwd()
    if os.path.exists(path):
        # Change the current working Directory
        try:
            os.chdir(path)  # Change the working directory
        except OSError:
            logger.error("Can't change the Current Working Directory", exc_info = True)
    else:
        print("Can't change the Current Working Directory because this path doesn't exits")
    return old_path

#Pandas Functions
@log_decorator.log_decorator()
def Excel_to_Pandas(filename,check_update=False):
    # TODO Create Docstring

    df=[]
    if check_update == True:
        timestamp = dt.datetime.fromtimestamp(Path(filename).stat().st_mtime)
        if dt.datetime.today().date() != timestamp.date():
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

@log_decorator.log_decorator()
def Cleanup_Dataframe(df):
    # TODO Create Docstring

    logger.debug(df.info(verbose=True))
    # Remove whitespace on both ends of column headers
    df.columns = df.columns.str.strip()

    # Replace whitespace in column header with _
    df.columns = df.columns.str.replace(' ', '_')

    return df

@log_decorator.log_decorator()
def create_tasks(df, description, duedate, tag='PMH'):
    # TODO Create Docstring
    df = df.sort_values(by=['Estimated_In_Service_Date'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()-1) as executor:

        for index, row in df.iterrows():

            logger.info(str(row['PETE_ID']))

            project = str(row['PETE_ID']) + ':' + str(row['Project_Name_y'])


            if row['Project_Tier'] == 1.0:
                priority = 'H'

            elif row['Project_Tier'] == 2.0:
                priority = 'M'

            elif row['Project_Tier'] == 3.0:
                priority = 'L'

            else:
                priority = None

        #Add_Task(description, project, duedate, priority, tag)

        # with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            patrial_Add_Task = functools.partial(Add_Task, description, project, duedate, priority)

            executor.submit(patrial_Add_Task, [tag])
        #     executor.map(patrial_Add_Task, [tag])
        #t = threading.Thread(target=Add_Task, args=(description, project, duedate, priority, tag,))
       # t.start()
      #  t.join()

#def Project_Start_60_Days_Out_No_Outages
#def Check_Estimated_In_Service_Date():
#def Construction_Ready_Date():
#def Check_Program_Manager_Resource():
#def Check_Construction_Manager_Resource():
#def Check_WaterFall_Draft_State():
#def Check_Start_Date_Relay_Settings():

@log_decorator.log_decorator()
def Check_for_Task(description, project):
    # TODO Create Docstring

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

@log_decorator.log_decorator()
def Add_Task(description, project, duedate, priority=None, tag=None):
    # TODO Create Docstring


    ID = 0
    ID = Check_for_Task(description, project)
    logger.info(ID)
    if ID == 0 :
        tw = TaskWarrior()
        task=tw.task_add(description=description, priority=priority, project=project, due=duedate)
        ID = task['id']

    elif ID > 0:
        #Task exist update
        Update_Task(ID, 'due', duedate)

    if priority is not None:
        Update_Task(ID, 'priority', priority)

    if tag is not None:
        Update_Task(ID, 'tags', tag)

@log_decorator.log_decorator
def Update_Task(ID, attribute, value):
    # TODO Create Docstring

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






@log_decorator.log_decorator()
def main():
    # TODO Create Docstring
    file_yaml = read_yaml('files.yaml', './configs')
    Project_Data_Filename = file_yaml['Project_Data_Spreadsheet']['filename']

    #Project_Data_Filename='All Project Data Report Metro West or Mike.xlsx'
    Schedules_Filename = file_yaml['Schedules_Spreadsheet']['filename']
    Budget_Item_Filename = file_yaml['Budget_Item_Spreadsheet']['filename']
    Relay_Setters_Filename = file_yaml['Relay_Setters_Spreadsheet']['filename']
    Material_Data_Filename = file_yaml['Material_Data_Spreadsheet']['filename']

    myprojectbudgetitmes=['00003212', '00003201', '00003203', '00003206', '00003226']

    """ Main entry point of the app """
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

        #Create_tasks_for_Precon_meetings(Project_Schedules_All_Data_df)
    ct.Create_task_for_Final_Engineering_with_draft_schedules(Project_Schedules_All_Data_df)
    ct.Create_task_for_Released_projects_missing_Construnction_Ready_Date(Project_Schedules_All_Data_df)
    ct.Create_task_for_Relay_Settings(Project_Schedules_All_Data_df)
    ct.Create_tasks_for_Engineering_Activities_Start_Dates(Project_Schedules_All_Data_df)
    ct.Create_tasks_for_Engineering_Activities_Finish_Dates(Project_Schedules_All_Data_df)
    ct.Create_task_for_Relay_Settings(Project_Schedules_All_Data_df)

    ct.Create_task_for_ESID_before_Energiztion(Project_Schedules_All_Data_df),
    ct.Create_task_for_add_WA_to_schedule(Project_Schedules_All_Data_df, myprojectbudgetitmes),
    ct.Create_tasks_for_Waterfalls(Project_Schedules_All_Data_df),
    ct.Create_task_for_missing_tiers(Project_Schedules_All_Data_df),
    ct.Create_tasks_TOA_outside_Waterfalls(Project_Schedules_All_Data_df),
    ct.Create_tasks_TOA_no_active(Project_Schedules_All_Data_df),
    ct.Create_tasks_Construnction_Summary_before_Construnction_Ready(Project_Schedules_All_Data_df)

    res = Popen('task sync', shell=True, stdin=PIPE)
    res.wait()
    res.stdin.close()

    if dt.date.today().weekday() == 4:
        Reports.Genrate_Relay_Settings_Report(Project_Schedules_All_Data_df, Relay_Setters_df)
        Reports.Genrate_Electrical_Prints_Report(Project_Schedules_All_Data_df)
        Reports.Genrate_Physical_Prints_Report(Project_Schedules_All_Data_df)

    if dt.date.today().weekday() == 4:
        try:
            Material_Data_df = Excel_to_Pandas(Material_Data_Filename)
        except:
            logger.error('Can not find Project Data file')
            raise
        Reports.Genrate_Matrial_Report(Material_Data_df, Project_Schedules_All_Data_df)
    #Reports.Genrate_Resource_Plan(Project_Schedules_All_Data_df, budget_item_df)



if __name__ == "__main__":
    """ This is executed when run from the command line """
    # Setup Logging
  #  logger = logging.getLogger('root')
   # FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
  #  logging.basicConfig(format=FORMAT)


 #   logger.setLevel(logging.DEBUG)

    main()