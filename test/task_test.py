import pytest
import os
import pandas as pd
import scr.create_task.Create_Task as ct



@pytest.fixture()
def setup_and_teardown():
    """This generators will setup or mock dataframe by reading from the Test_Data folder.

        Args:

        Yields:
            df: dataframe read from Test_Data folder
        """
    if 'Test_Data' not in os.getcwd():
        os.chdir('./test/Test_Data')
    df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
    df['Start_Date'] = pd.to_datetime(df['Start_Date'])
    df['Finish_Date'] = pd.to_datetime(df['Finish_Date'])
    df['COMMENTS'].fillna('', inplace=True)
    df['COMMENTS'] = df.COMMENTS.astype(str)
    df['Parent'].fillna('', inplace=True)
    df['Parent'] = df. Parent.astype(str)
    df['Child'].fillna('', inplace=True)
    df['Child'] = df.Parent.astype(str)

    yield df

class TestConstitutionalDesign:

    class TestPositive:
        def test_Create_task_for_Relay_Settings_Finish_date(self, setup_and_teardown):
            description = 'Check with Relay Setter on when settings are going to be issued'

            setup_and_teardown.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'A'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'

            assert ct.create_task_for_relay_settings(setup_and_teardown, False) == description

        def test_Create_task_for_Relay_Settings_start_date(self, setup_and_teardown):

            description = 'Check with Relay Setter on when settings are going to be started'

            setup_and_teardown.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'

            assert ct.create_task_for_relay_settings(setup_and_teardown, False) == description






class TestTOA:
    class TestNegtive:
        def test_Create_tasks_no_active_TOA_inside_Waterfall_neg(self, setup_and_teardown):

            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Waterfall Start'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'No TOA Request Needed'
            setup_and_teardown.at[1, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())
            assert ct.create_tasks_toa_no_active(setup_and_teardown, False) == None

        def test_Create_tasks_TOA_equal_Waterfall_Start(self, setup_and_teardown):
            description = None
            # setup_and_teardown['COMMENTS'] = setup_and_teardown['COMMENTS'].astype(str)
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Schedule_Function'] = 'TOA'
            setup_and_teardown.at[0, 'COMMENTS'] = str('Oncor Status: SUBMITTED ERCOT Status:')
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date() + pd.DateOffset(days=1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Waterfall Start'
            setup_and_teardown.at[1, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[2, 'PETE_ID'] = 1
            setup_and_teardown.at[2, 'Grandchild'] = 'Waterfall Finish'
            setup_and_teardown.at[2, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[2, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=6))

            assert ct.create_tasks_toa_outside_waterfalls(setup_and_teardown, False) == description

        def test_Create_tasks_TOA_equal_Waterfall_Finish(self, setup_and_teardown):
            description = None
            # setup_and_teardown['COMMENTS'] = setup_and_teardown['COMMENTS'].astype(str)
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Schedule_Function'] = 'TOA'
            setup_and_teardown.at[0, 'COMMENTS'] = str('Oncor Status: SUBMITTED ERCOT Status:')
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=6))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Waterfall Start'
            setup_and_teardown.at[1, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[2, 'PETE_ID'] = 1
            setup_and_teardown.at[2, 'Grandchild'] = 'Waterfall Finish'
            setup_and_teardown.at[2, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[2, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=6))

            assert ct.create_tasks_toa_outside_waterfalls(setup_and_teardown, False) == description

    class TestPositive:
        def test_Create_tasks_TOA_before_Waterfall(self, setup_and_teardown):
            description = 'TOA request outside Waterfall dates'
            # setup_and_teardown['COMMENTS'] = setup_and_teardown['COMMENTS'].astype(str)
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Schedule_Function'] = 'TOA'
            setup_and_teardown.at[0, 'COMMENTS'] = str('Oncor Status: SUBMITTED ERCOT Status:')
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() - pd.DateOffset(days=1))
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Waterfall Start'
            setup_and_teardown.at[1, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[2, 'PETE_ID'] = 1
            setup_and_teardown.at[2, 'Grandchild'] = 'Waterfall Finish'
            setup_and_teardown.at[2, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[2, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=6))

            assert ct.create_tasks_toa_outside_waterfalls(setup_and_teardown, False) == description

        def test_Create_tasks_TOA_after_Waterfall(self, setup_and_teardown):
            description = 'TOA request outside Waterfall dates'
            # setup_and_teardown['COMMENTS'] = setup_and_teardown['COMMENTS'].astype(str)
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Schedule_Function'] = 'TOA'
            setup_and_teardown.at[0, 'COMMENTS'] = str('Oncor Status: SUBMITTED ERCOT Status:')
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=7))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Waterfall Start'
            setup_and_teardown.at[1, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[2, 'PETE_ID'] = 1
            setup_and_teardown.at[2, 'Grandchild'] = 'Waterfall Finish'
            setup_and_teardown.at[2, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[2, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=6))

            assert ct.create_tasks_toa_outside_waterfalls(setup_and_teardown, False) == description


class TestPMO:
    class TestPMOSchedulePostive:
        def test_create_tasks_for_waterfalls_Baseline(self, setup_and_teardown):
            description = 'Waterfall needs to be baselined'
            setup_and_teardown.at[0, 'Grandchild'] = 'TEST'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            assert ct.create_tasks_for_waterfalls(setup_and_teardown, False) == description

        def test_Create_tasks_no_active_TOA_inside_Waterfall(self, setup_and_teardown):
            description = 'No Active TOA for project'

            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Waterfall Start'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_toa_no_active(setup_and_teardown, False) == description

class TestTE:
    class TestPositive:
        def test_create_task_for_final_engineering_with_draft_schedules(self, setup_and_teardown):
            description = 'Check with Engineering on when a schedule will be finalized'
            setup_and_teardown.at[0, 'PROJECTSTATUS'] = 'Released'
            setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
            setup_and_teardown.at[0, 'Child'] = 'Construction Summary'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date()
            assert ct.create_task_for_final_engineering_with_draft_schedules(setup_and_teardown, False) == description

        def test_create_tasks_for_construncction_task_request_approval(self, setup_and_teardown):
            description = 'Ask Engineering for update on Construction Task Request Approval'

            setup_and_teardown.at[0, 'Grandchild'] = 'Construction Task Request Approval'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'

            assert ct.create_tasks_for_construncction_task_request_approval(setup_and_teardown, False) == description

        def test_create_tasks_for_engineering_activities_finish_dates_FD_PD(self, setup_and_teardown):
            description = 'Ask Engineering to update the TE schedule (Finish Date)'

            setup_and_teardown = pd.concat([setup_and_teardown] * 2, ignore_index=True)

            setup_and_teardown.at[0, 'Grandchild'] = 'Foundation Design'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=10)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'A'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'

            setup_and_teardown.at[1, 'Grandchild'] = 'Physical Design'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=10)
            setup_and_teardown.at[1, r'Start_Date_Planned\Actual'] = 'A'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'P'

            assert ct.create_tasks_for_engineering_activities_finish_dates(setup_and_teardown, False) == description

        def test_create_tasks_line_design_finish_after_construction_ready_date(self, setup_and_teardown):
            description = 'Design Finish after Construction Ready Date (Line)'
            # setup_and_teardown['COMMENTS'] = setup_and_teardown['COMMENTS'].astype(str)
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Complete Design Books Issued'
            setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'A'
            setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Complete Design Books Issued'
            setup_and_teardown.at[1, 'Region_Name'] = 'METRO WEST'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() - pd.DateOffset(days=1))
            setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'A'
            setup_and_teardown.at[1, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_line_design_finish_after_construction_ready_date(setup_and_teardown,
                                                                                    False) == None

            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Complete Design Books Issued'
            setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Complete Design Books Issued'
            setup_and_teardown.at[1, 'Region_Name'] = 'METRO WEST'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() - pd.DateOffset(days=1))
            setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[1, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_line_design_finish_after_construction_ready_date(setup_and_teardown,
                                                                                    False) == description

            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Project WA Approved'
            setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Project WA Approved'
            setup_and_teardown.at[1, 'Region_Name'] = 'METRO WEST'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() - pd.DateOffset(days=1))
            setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[1, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_line_design_finish_after_construction_ready_date(setup_and_teardown,
                                                                                    False) == description

        def test_create_tasks_for_engineering_activities_start_dates_ED_PD(self, setup_and_teardown):
            description = 'Ask Engineering to update the TE schedule'

            setup_and_teardown = pd.concat([setup_and_teardown] * 2, ignore_index=True)

            setup_and_teardown.at[0, 'Grandchild'] = 'Electrical Design'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'

            setup_and_teardown.at[1, 'Grandchild'] = 'Physical Design'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[1, r'Start_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[1, 'Program_Manager'] = 'Michael Howard'

            assert ct.create_tasks_for_engineering_activities_start_dates(setup_and_teardown, False) == description

        def test_create_tasks_for_engineering_activities_finish_dates_ED(self, setup_and_teardown):
            description = 'Check with Engineering on if Electrical Designs were issued'

            setup_and_teardown.at[0, 'Grandchild'] = 'Electrical Design'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=10)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'A'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'

            assert ct.create_tasks_for_engineering_activities_finish_dates(setup_and_teardown, False) == description

        def test_create_tasks_for_engineering_activities_finish_dates_PD(self, setup_and_teardown):
            description = 'Check with Engineering on if Physical Designs were issued'

            setup_and_teardown.at[0, 'Grandchild'] = 'Physical Design'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=10)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'A'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'

            assert ct.create_tasks_for_engineering_activities_finish_dates(setup_and_teardown, False) == description

        def test_create_tasks_for_engineering_activities_finish_dates_FD(self, setup_and_teardown):
            description = 'Check with Engineering on if Foundation Designs were issued'

            setup_and_teardown.at[0, 'Grandchild'] = 'Foundation Design'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=10)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'A'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'

            assert ct.create_tasks_for_engineering_activities_finish_dates(setup_and_teardown, False) == description

        def test_create_tasks_for_engineering_activities_finish_dates_FD_ED(self, setup_and_teardown):
            description = 'Ask Engineering to update the TE schedule (Finish Date)'

            setup_and_teardown = pd.concat([setup_and_teardown] * 2, ignore_index=True)

            setup_and_teardown.at[0, 'Grandchild'] = 'Foundation Design'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=10)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'A'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'

            setup_and_teardown.at[1, 'Grandchild'] = 'Electrical Design'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=10)
            setup_and_teardown.at[1, r'Start_Date_Planned\Actual'] = 'A'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'P'

            assert ct.create_tasks_for_engineering_activities_finish_dates(setup_and_teardown, False) == description

        def test_create_tasks_station_design_finish_after_construction_ready_date(self, setup_and_teardown):
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

            assert ct.create_tasks_station_design_finish_after_construction_ready_date(setup_and_teardown, False) == None

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

            assert ct.create_tasks_station_design_finish_after_construction_ready_date(setup_and_teardown,
                                                                                       False) == description

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

            assert ct.create_tasks_station_design_finish_after_construction_ready_date(setup_and_teardown,
                                                                                       False) == description

        def test_create_tasks_construnction_summary_before_construnction_ready(self, setup_and_teardown):
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

            assert ct.create_tasks_construnction_summary_before_construnction_ready(setup_and_teardown,
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

            assert ct.create_tasks_construnction_summary_before_construnction_ready(setup_and_teardown,
                                                                                    False) == description

        def test_create_tasks_for_engineering_activities_start_dates_ED(self, setup_and_teardown):
            description = 'Check with Engineering on if Electrical Designs were started'

            setup_and_teardown.at[0, 'Grandchild'] = 'Electrical Design'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            assert ct.create_tasks_for_engineering_activities_start_dates(setup_and_teardown, False) == description

        def test_create_tasks_for_engineering_activities_start_dates_PD(self, setup_and_teardown):
            description = 'Check with Engineering on if Physical Designs were started'

            setup_and_teardown.at[0, 'Grandchild'] = 'Physical Design'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'

            assert ct.create_tasks_for_engineering_activities_start_dates(setup_and_teardown, False) == description

        def test_create_tasks_for_engineering_activities_start_dates_FD(self, setup_and_teardown):
            description = 'Check with Engineering on if Foundation Designs were started'

            setup_and_teardown.at[0, 'Grandchild'] = 'Foundation Design'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'

            assert ct.create_tasks_for_engineering_activities_start_dates(setup_and_teardown, False) == description

        def test_create_tasks_for_engineering_activities_start_dates_FD_ED(self, setup_and_teardown):
            description = 'Ask Engineering to update the TE schedule'

            setup_and_teardown = pd.concat([setup_and_teardown] * 2, ignore_index=True)

            setup_and_teardown.at[0, 'Grandchild'] = 'Foundation Design'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'

            setup_and_teardown.at[1, 'Grandchild'] = 'Electrical Design'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[1, r'Start_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[1, 'Program_Manager'] = 'Michael Howard'

            assert ct.create_tasks_for_engineering_activities_start_dates(setup_and_teardown, False) == description

        def test_create_tasks_for_engineering_activities_start_dates_FD_PD(self, setup_and_teardown):
            description = 'Ask Engineering to update the TE schedule'

            setup_and_teardown = pd.concat([setup_and_teardown] * 2, ignore_index=True)

            setup_and_teardown.at[0, 'Grandchild'] = 'Foundation Design'
            setup_and_teardown.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Start_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'

            setup_and_teardown.at[1, 'Grandchild'] = 'Physical Design'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            setup_and_teardown.at[1, r'Start_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[1, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            setup_and_teardown.at[1, r'Finish_Date_Planned\Actual'] = 'P'
            setup_and_teardown.at[1, 'Program_Manager'] = 'Michael Howard'

            assert ct.create_tasks_for_engineering_activities_start_dates(setup_and_teardown, False) == description

        def test_create_tasks_line_activities_conflict(self, setup_and_teardown):
            description = 'TE date conflicts with construction/distict summary'
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Complete Design Books Issued'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=-1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Parent'] = 'Construction Summary'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_line_activities_conflict(setup_and_teardown, False) == description

        def test_create_tasks_station_activities_conflict_1(self, setup_and_teardown):
            description = 'TE date conflicts with construction/distict summary'
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Electrical Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Electrical Job Planning'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) == description + " " + 'Electrical Design'

        def test_create_tasks_station_activities_conflict_2(self, setup_and_teardown):
            description = 'TE date conflicts with construction/distict summary'
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Electrical Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Electrical Construction'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) == description + " " +'Electrical Design'

        def test_create_tasks_station_activities_conflict_3(self, setup_and_teardown):
            description = 'TE date conflicts with construction/distict summary'
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Foundation Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Foundation Job Planning'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) == description + " " +'Foundation Design'

        def test_create_tasks_station_activities_conflict_4(self, setup_and_teardown):
            description = 'TE date conflicts with construction/distict summary'
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Foundation Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Foundations'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) == description + " " +'Foundation Design'

        def test_create_tasks_station_activities_conflict_5(self, setup_and_teardown):
            description = 'TE date conflicts with construction/distict summary'
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Physical Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Physical Job Planning'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) == description + " " +'Physical Design'

        def test_create_tasks_station_activities_conflict_6(self, setup_and_teardown):
            description = 'TE date conflicts with construction/distict summary'
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Physical Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Physical'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) == description + " " +'Physical Design'

        def test_create_tasks_station_activities_conflict_7(self, setup_and_teardown):
            description = 'TE date conflicts with construction/distict summary'
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Grading Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Grading Job Planning'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) == description + " " +'Grading Design'

        def test_create_tasks_station_activities_conflict_8(self, setup_and_teardown):
            description = 'TE date conflicts with construction/distict summary'
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Grading Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Grading'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) ==description + " " + 'Grading Design'



    class TestNegtive:
        def test_create_tasks_line_design_finish_after_construction_ready_date(self, setup_and_teardown):
            description = None
            # setup_and_teardown['COMMENTS'] = setup_and_teardown['COMMENTS'].astype(str)
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Complete Design Books Issued'
            setup_and_teardown.at[0, 'Region_Name'] = 'METRO WEST'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=1))
            setup_and_teardown.at[0, r'Finish_Date_Planned\Actual'] = 'A'
            setup_and_teardown.at[0, 'PLANNEDCONSTRUCTIONREADY'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Schedule_Function'] = 'Construction'

            assert ct.create_tasks_line_design_finish_after_construction_ready_date(setup_and_teardown,
                                                                                    False) == description

        def test_create_tasks_station_activities_conflict_1(self, setup_and_teardown):
            description = None
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Electrical Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=-1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Electrical Job Planning'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[2, 'PETE_ID'] = 1
            setup_and_teardown.at[2, 'Grandchild'] = 'Electrical Construction'
            setup_and_teardown.at[2, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())
            setup_and_teardown.at[2, r'Finish_Date_Planned\Actual'] = 'A'

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) == description

        def test_create_tasks_station_activities_conflict_2(self, setup_and_teardown):
            description = None
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Foundation Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=-1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Foundation Job Planning'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[2, 'PETE_ID'] = 1
            setup_and_teardown.at[2, 'Grandchild'] = 'Foundations'
            setup_and_teardown.at[2, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())
            setup_and_teardown.at[2, r'Finish_Date_Planned\Actual'] = 'A'

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) == description

        def test_create_tasks_station_activities_conflict_3(self, setup_and_teardown):
            description = None
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Physical Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=-1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Physical Job Planning'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[2, 'PETE_ID'] = 1
            setup_and_teardown.at[2, 'Grandchild'] = 'Physical'
            setup_and_teardown.at[2, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())
            setup_and_teardown.at[2, r'Finish_Date_Planned\Actual'] = 'A'

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) == description

        def test_create_tasks_station_activities_conflict_4(self, setup_and_teardown):
            description = None
            setup_and_teardown.at[0, 'PETE_ID'] = 1
            setup_and_teardown.at[0, 'Grandchild'] = 'Grading Design'
            setup_and_teardown.at[0, 'Program_Manager'] = 'Michael Howard'
            setup_and_teardown.at[0, 'Finish_Date'] = pd.to_datetime(
                pd.to_datetime("today").date() + pd.DateOffset(days=-1))

            setup_and_teardown.at[1, 'PETE_ID'] = 1
            setup_and_teardown.at[1, 'Grandchild'] = 'Grading Job Planning'
            setup_and_teardown.at[1, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())

            setup_and_teardown.at[2, 'PETE_ID'] = 1
            setup_and_teardown.at[2, 'Grandchild'] = 'Grading'
            setup_and_teardown.at[2, 'Start_Date'] = pd.to_datetime(pd.to_datetime("today").date())
            setup_and_teardown.at[2, r'Finish_Date_Planned\Actual'] = 'A'

            assert ct.create_tasks_station_activities_conflict(setup_and_teardown, False) == description