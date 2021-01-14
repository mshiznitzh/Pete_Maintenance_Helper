import pytest
import os
import Create_Task.Create_Task
import pandas as pd


@pytest.fixture()
def setup_and_teardown():
        if 'Test_Data' not in os.getcwd():
            os.chdir("./Test_Data/")
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df['Start_Date'] = pd.to_datetime(df['Start_Date'])
        df['Finish_Date'] = pd.to_datetime(df['Finish_Date'])
        df['COMMENTS'].fillna('', inplace=True)
        df['COMMENTS'] = df.COMMENTS.astype(str)
        df['Parent'].fillna('', inplace=True)
        df['Parent'] = df. Parent.astype(str)

        yield df

def test_Create_task_for_Relay_Settings_Finish_date(setup_and_teardown):
    description = 'Check with Relay Setter on when settings are going to be issued'

    setup_and_teardown.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
    setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'A'
    setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
    setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'

    assert Create_Task.Create_Task.Create_task_for_Relay_Settings(setup_and_teardown, False) == description

def test_Create_task_for_Relay_Settings_start_date(setup_and_teardown):

    description = 'Check with Relay Setter on when settings are going to be started'

    setup_and_teardown.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
    setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'P'
    setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
    setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'

    assert Create_Task.Create_Task.Create_task_for_Relay_Settings(setup_and_teardown, False) == description

def test_Create_tasks_TOA_after_Waterfall(setup_and_teardown):
    description = 'TOA request outside Waterfall dates'
    # setup_and_teardown['COMMENTS'] = setup_and_teardown['COMMENTS'].astype(str)
    setup_and_teardown.at[0, 'PETE_ID'] = 1
    setup_and_teardown.at[0, 'Schedule_Function'] = 'TOA'
    setup_and_teardown.at[0, 'COMMENTS'] = str('Oncor Status: SUBMITTED ERCOT Status:')
    setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
    setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())
    setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=7))

    setup_and_teardown.at[1, 'PETE_ID'] = 1
    setup_and_teardown.at[1, 'Grandchild'] = 'Waterfall Start'
    setup_and_teardown.at[1, 'Program_Manager'] = 'Michael Howard'
    setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())

    setup_and_teardown.at[2, 'PETE_ID'] = 1
    setup_and_teardown.at[2, 'Grandchild'] = 'Waterfall Finish'
    setup_and_teardown.at[2, 'Program_Manager'] = 'Michael Howard'
    setup_and_teardown.at[2, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=6))

    assert Create_Task.Create_Task.Create_tasks_TOA_outside_Waterfalls(setup_and_teardown, False) == description

def test_Create_tasks_TOA_before_Waterfall(setup_and_teardown):
    description = 'TOA request outside Waterfall dates'
    # setup_and_teardown['COMMENTS'] = setup_and_teardown['COMMENTS'].astype(str)
    setup_and_teardown.at[0, 'PETE_ID'] = 1
    setup_and_teardown.at[0, 'Schedule_Function'] = 'TOA'
    setup_and_teardown.at[0, 'COMMENTS'] = str('Oncor Status: SUBMITTED ERCOT Status:')
    setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
    setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date() - pd.DateOffset(days=1))
    setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())

    setup_and_teardown.at[1, 'PETE_ID'] = 1
    setup_and_teardown.at[1, 'Grandchild'] = 'Waterfall Start'
    setup_and_teardown.at[1, 'Program_Manager'] = 'Michael Howard'
    setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())

    setup_and_teardown.at[2, 'PETE_ID'] = 1
    setup_and_teardown.at[2, 'Grandchild'] = 'Waterfall Finish'
    setup_and_teardown.at[2, 'Program_Manager'] = 'Michael Howard'
    setup_and_teardown.at[2, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=6))

    assert Create_Task.Create_Task.Create_tasks_TOA_outside_Waterfalls(setup_and_teardown, False) == description

def test_Create_tasks_no_active_TOA_inside_Waterfall(setup_and_teardown):
    description = 'No Active TOA for project'

    setup_and_teardown.at[0, 'PETE_ID'] = 1
    setup_and_teardown.at[0, 'Grandchild'] = 'Waterfall Start'
    setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
    setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())

    assert Create_Task.Create_Task.Create_tasks_TOA_no_active(setup_and_teardown, False) == description

def test_Create_tasks_Construnction_Summary_before_Construnction_Ready(setup_and_teardown):
    description = 'Construction Summary before Construction Ready'
    # setup_and_teardown['COMMENTS'] = setup_and_teardown['COMMENTS'].astype(str)

    setup_and_teardown.at[0, 'PETE_ID'] = 1
    setup_and_teardown.at[0, 'Parent'] = 'Construction Summary'
    setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=1))
    setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'A'
    setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    setup_and_teardown.at[1, 'PETE_ID'] = 1
    setup_and_teardown.at[1, 'Parent'] = 'Construction Summary'
    setup_and_teardown.at[1, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date() - pd.DateOffset(days=1))
    setup_and_teardown.at[1, r'Start_Date_Planned\Actual'] = 'A'
    setup_and_teardown.at[1, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    assert Create_Task.Create_Task.Create_tasks_Construnction_Summary_before_Construnction_Ready(setup_and_teardown,
                                                                                                 False) == None


    setup_and_teardown.at[0, 'PETE_ID'] = 1
    setup_and_teardown.at[0, 'Parent'] = 'Construction Summary'
    setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=1))
    setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'P'
    setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    setup_and_teardown.at[1, 'PETE_ID'] = 1
    setup_and_teardown.at[1, 'Parent'] = 'Construction Summary'
    setup_and_teardown.at[1, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date() - pd.DateOffset(days=1))
    setup_and_teardown.at[1, r'Start_Date_Planned\Actual'] = 'P'
    setup_and_teardown.at[1, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    assert Create_Task.Create_Task.Create_tasks_Construnction_Summary_before_Construnction_Ready(setup_and_teardown, False) == description


def test_Create_tasks_Station_Design_Finish_after_Construction_Ready_Date(setup_and_teardown):
    description = 'Design Finish after Construction Ready Date'
    # setup_and_teardown['COMMENTS'] = setup_and_teardown['COMMENTS'].astype(str)

    setup_and_teardown.at[0, 'PETE_ID'] = 1
    setup_and_teardown.at[0, 'Grandchild'] = 'Electrical Design'
    setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=1))
    setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'A'
    setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    setup_and_teardown.at[1, 'PETE_ID'] = 1
    setup_and_teardown.at[1, 'Grandchild'] = 'Electrical Design'
    setup_and_teardown.at[1, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() - pd.DateOffset(days=1))
    setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'A'
    setup_and_teardown.at[1, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    assert Create_Task.Create_Task.Create_tasks_Station_Design_Finish_after_Construction_Ready_Date(setup_and_teardown,
                                                                                                    False) == None


    setup_and_teardown.at[0, 'PETE_ID'] = 1
    setup_and_teardown.at[0, 'Grandchild'] = 'Electrical Design'
    setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=1))
    setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
    setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    setup_and_teardown.at[1, 'PETE_ID'] = 1
    setup_and_teardown.at[1, 'Grandchild'] = 'Electrical Design'
    setup_and_teardown.at[1, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() - pd.DateOffset(days=1))
    setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'P'
    setup_and_teardown.at[1, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    assert Create_Task.Create_Task.Create_tasks_Station_Design_Finish_after_Construction_Ready_Date(setup_and_teardown, False) == description

    setup_and_teardown.at[0, 'PETE_ID'] = 1
    setup_and_teardown.at[0, 'Grandchild'] = 'Physical Design'
    setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=1))
    setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
    setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    setup_and_teardown.at[1, 'PETE_ID'] = 1
    setup_and_teardown.at[1, 'Grandchild'] = 'Physical Design'
    setup_and_teardown.at[1, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() - pd.DateOffset(days=1))
    setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'P'
    setup_and_teardown.at[1, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    assert Create_Task.Create_Task.Create_tasks_Station_Design_Finish_after_Construction_Ready_Date(setup_and_teardown, False) == description

def test_Create_tasks_Line_Design_Finish_after_Construction_Ready_Date(setup_and_teardown):
    description = 'Design Finish after Construction Ready Date (Line)'
    # setup_and_teardown['COMMENTS'] = setup_and_teardown['COMMENTS'].astype(str)
    setup_and_teardown.at[0, 'PETE_ID'] = 1
    setup_and_teardown.at[0, 'Grandchild'] = 'Complete Design Books Issued'
    setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=1))
    setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'A'
    setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    setup_and_teardown.at[1, 'PETE_ID'] = 1
    setup_and_teardown.at[1, 'Grandchild'] = 'Complete Design Books Issued'
    setup_and_teardown.at[1, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() - pd.DateOffset(days=1))
    setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'A'
    setup_and_teardown.at[1, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    assert Create_Task.Create_Task.Create_tasks_Line_Design_Finish_after_Construction_Ready_Date(setup_and_teardown,
                                                                                                 False) == None

    setup_and_teardown.at[0, 'PETE_ID'] = 1
    setup_and_teardown.at[0, 'Grandchild'] = 'Complete Design Books Issued'
    setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=1))
    setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
    setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    setup_and_teardown.at[1, 'PETE_ID'] = 1
    setup_and_teardown.at[1, 'Grandchild'] = 'Complete Design Books Issued'
    setup_and_teardown.at[1, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() - pd.DateOffset(days=1))
    setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'P'
    setup_and_teardown.at[1, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    assert Create_Task.Create_Task.Create_tasks_Line_Design_Finish_after_Construction_Ready_Date(setup_and_teardown, False) == description

    setup_and_teardown.at[0, 'PETE_ID'] = 1
    setup_and_teardown.at[0, 'Grandchild'] = 'Project WA Approved'
    setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=1))
    setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
    setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())


    setup_and_teardown.at[1, 'PETE_ID'] = 1
    setup_and_teardown.at[1, 'Grandchild'] = 'Project WA Approved'
    setup_and_teardown.at[1, 'Region_Name'] = 'METRO WEST'
    setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() - pd.DateOffset(days=1))
    setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'P'
    setup_and_teardown.at[1, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

    assert Create_Task.Create_Task.Create_tasks_Line_Design_Finish_after_Construction_Ready_Date(setup_and_teardown, False) == description
