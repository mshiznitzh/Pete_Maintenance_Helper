import unittest
import pandas as pd
import os
import Pete_Maintenace_Helper
import Create_Task.Create_Task

class TaskCreationTest(unittest.TestCase):
    def test_Create_task_for_Relay_Settings_Finish_date(self):


        description = 'Check with Relay Setter on when settings are going to be issued'
        os.chdir("./Test_Data/")
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
        df.at[0, 'Start_Date_Planned\Actual'] = 'A'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_Task.Create_Task.Create_task_for_Relay_Settings(df, False), description)

    def test_Create_task_for_Relay_Settings_start_date(self):

        description = 'Check with Relay Setter on when settings are going to be started'
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_Task.Create_Task.Create_task_for_Relay_Settings(df, False), description)

    def test_Create_tasks_for_Engineering_Activities_Start_Dates_ED(self):

        description = 'Check with Engineering on if Electrical Designs were started'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Electrical Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Start_Dates(df,False), description)

    def test_Create_tasks_for_Engineering_Activities_Start_Dates_PD(self):

        description = 'Check with Engineering on if Physical Designs were started'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Physical Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Start_Dates(df,False), description)

    def test_Create_tasks_for_Engineering_Activities_Start_Dates_FD(self):

        description = 'Check with Engineering on if Foundation Designs were started'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Foundation Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Start_Dates(df,False), description)

    def test_Create_tasks_for_Engineering_Activities_Start_Dates_FD_ED(self):

        description = 'Ask Engineering to update the TE schedule'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df= pd.concat([df]*2, ignore_index=True)

        df.at[0, 'Grandchild'] = 'Foundation Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        df.at[1, 'Grandchild'] = 'Electrical Design'
        df.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[1, 'Start_Date_Planned\Actual'] = 'P'
        df.at[1, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[1, 'Finish_Date_Planned\Actual'] = 'P'


        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Start_Dates(df,False), description)

    def test_Create_tasks_for_Engineering_Activities_Start_Dates_FD_PD(self):
        description = 'Ask Engineering to update the TE schedule'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df = pd.concat([df] * 2, ignore_index=True)

        df.at[0, 'Grandchild'] = 'Foundation Design'
        df.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        df.at[1, 'Grandchild'] = 'Physical Design'
        df.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[1, 'Start_Date_Planned\Actual'] = 'P'
        df.at[1, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[1, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Start_Dates(df, False),
                         description)

    def test_Create_tasks_for_Engineering_Activities_Start_Dates_ED_PD(self):
        description = 'Ask Engineering to update the TE schedule'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df = pd.concat([df] * 2, ignore_index=True)

        df.at[0, 'Grandchild'] = 'Electrical Design'
        df.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        df.at[1, 'Grandchild'] = 'Physical Design'
        df.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[1, 'Start_Date_Planned\Actual'] = 'P'
        df.at[1, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[1, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Start_Dates(df, False),
                         description)

    def test_Create_tasks_for_Engineering_Activities_Finish_Dates_ED(self):

        description = 'Check with Engineering on if Electrical Designs were issued'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Electrical Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
        df.at[0, 'Start_Date_Planned\Actual'] = 'A'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Finish_Dates(df,False), description)

    def test_Create_tasks_for_Engineering_Activities_Finish_Dates_PD(self):

        description = 'Check with Engineering on if Physical Designs were issued'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Physical Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
        df.at[0, 'Start_Date_Planned\Actual'] = 'A'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Finish_Dates(df,False), description)

    def test_Create_tasks_for_Engineering_Activities_Finish_Dates_FD(self):

        description = 'Check with Engineering on if Foundation Designs were issued'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Foundation Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
        df.at[0, 'Start_Date_Planned\Actual'] = 'A'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Finish_Dates(df,False), description)

    def test_Create_tasks_for_Engineering_Activities_Finish_Dates_FD_ED(self):

        description = 'Ask Engineering to update the TE schedule (Finish Date)'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df= pd.concat([df]*2, ignore_index=True)

        df.at[0, 'Grandchild'] = 'Foundation Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
        df.at[0, 'Start_Date_Planned\Actual'] = 'A'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        df.at[1, 'Grandchild'] = 'Electrical Design'
        df.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=10)
        df.at[1, 'Start_Date_Planned\Actual'] = 'A'
        df.at[1, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[1, 'Finish_Date_Planned\Actual'] = 'P'


        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Finish_Dates(df,False), description)

        def test_Create_tasks_for_Engineering_Activities_Start_Dates_FD_PD(self):
            description = 'Ask Engineering to update the TE schedule (Finish Date)'

            df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
            df = pd.concat([df] * 2, ignore_index=True)

            df.at[0, 'Grandchild'] = 'Foundation Design'
            df.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            df.at[0, 'Start_Date_Planned\Actual'] = 'P'
            df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

            df.at[1, 'Grandchild'] = 'Physical Design'
            df.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            df.at[1, 'Start_Date_Planned\Actual'] = 'P'
            df.at[1, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            df.at[1, 'Finish_Date_Planned\Actual'] = 'P'

            self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Start_Dates(df, False),
                             description)

        def test_Create_tasks_for_Engineering_Activities_Start_Dates_ED_PD(self):
            description = 'Ask Engineering to update the TE schedule (Finish Date)'

            df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
            df = pd.concat([df] * 2, ignore_index=True)

            df.at[0, 'Grandchild'] = 'Electrical Design'
            df.at[0, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            df.at[0, 'Start_Date_Planned\Actual'] = 'P'
            df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

            df.at[1, 'Grandchild'] = 'Physical Design'
            df.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
            df.at[1, 'Start_Date_Planned\Actual'] = 'P'
            df.at[1, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
            df.at[1, 'Finish_Date_Planned\Actual'] = 'P'

            self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Engineering_Activities_Start_Dates(df, False),
                             description)

    def test_Create_tasks_for_Construncction_Task_Request_Approval(self):

        description = 'Ask Engineering for update on Construction Task Request Approval'
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Construction Task Request Approval'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'
        df.at[0, 'Program_Manager'] = 'Michael Howard'

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Construncction_Task_Request_Approval(df, False), description)

    def test_Create_tasks_for_Waterfalls_Baseline(self):

        description = 'Waterfall needs to baselined'
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Schedule_Function'] = 'TEST'
        df.at[0, 'Program_Manager'] = 'Michael Howard'

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Waterfalls(df, False), description)

    def test_Create_tasks_for_Waterfalls_Baseline(self):

        description = 'Waterfall Finish is before Waterfall Start'
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df = pd.concat([df] * 2, ignore_index=True)

        df.at[0, 'Schedule_Function'] = 'PMO'
        df.at[0, 'Grandchild'] = 'Waterfall Start'
        df.at[0, 'Program_Manager'] = 'Michael Howard'
        df.at[0, 'Start_Date'] = pd.to_datetime("today").date()
        df.at[0, 'Estimated_In-Service_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=1)

        df.at[1, 'Schedule_Function'] = 'PMO'
        df.at[1, 'Grandchild'] = 'Waterfall Finish'
        df.at[1, 'Program_Manager'] = 'Michael Howard'
        df.at[1, 'Start_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=1)
        df.at[1, 'Estimated_In-Service_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=1)

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Waterfalls(df, False), description)

    def test_Create_tasks_for_Waterfalls_EISD(self):
        description = 'Waterfall Finish not in same season as EISD'
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')

        df.at[0, 'Schedule_Function'] = 'PMO'
        df.at[0, 'Grandchild'] = 'Waterfall Finish'
        df.at[0, 'Program_Manager'] = 'Michael Howard'
        df.at[0, 'Start_Date'] = pd.to_datetime("today").date()
        df.at[0, 'Estimated_In-Service_Date'] = pd.to_datetime("today").date() + pd.DateOffset(months=6)

        self.assertEqual(Create_Task.Create_Task.Create_tasks_for_Waterfalls(df, False), description)

    def test_Create_tasks_for_Waterfalls_EISD(self):
        description = 'Project Energization is after Estimated In-Service Date'
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')

        df.at[0, 'Grandchild'] = 'Project Energization'
        df.at[0, 'Program_Manager'] = 'Michael Howard'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date()
        df.at[0, 'Estimated_In-Service_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=1)

        self.assertEqual(Create_Task.Create_Task.Create_task_for_ESID_before_Energiztion(df, False), description)

    def test_Create_tasks_no_TOA_inside_Construnction_Summary(self):
        description = 'Outages in Construction Summary Window'
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')

        df.at[0, 'Schedule_Function'] = 'TOA'
        df.at[0, 'COMMENTS'] = 'Oncor Status: SUBMITTED ERCOT Status:   Requested By: MENDOZA,ADRIAN ALBERT Date Submitted: 2020-09-21 15:45:16.0 ERCOT Received Date:   Emergency Restore Time: 6 HOURS Line Device: EULESS BKR 4225, SWT 4224, SWT 4226 Associated Projects: 16T62055'
        df.at[0, 'Program_Manager'] = 'Michael Howard'
        df.at[0, 'Start_Date'] = pd.to_datetime("today").date()
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=7)

        df.at[1, 'Schedule_Function'] = 'Construction'
        df.at[1, 'PARENT'] = 'Construction Summary'
        df.at[1, 'Program_Manager'] = 'Michael Howard'
        df.at[1, 'Start_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=1)
        df.at[1, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=6)

        self.assertEqual(Create_Task.Create_Task.Create_tasks_no_TOA_inside_Construnction_Summary(df, False), description)

    def test_Create_tasks_Worng_Tier_Level(self):
        description = 'Tier Level is wrong for estimate'
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')

        df.at[0, 'Schedule_Function'] = 'TOA'
        df.at[0, 'COMMENTS'] = 'Oncor Status: SUBMITTED ERCOT Status:   Requested By: MENDOZA,ADRIAN ALBERT Date Submitted: 2020-09-21 15:45:16.0 ERCOT Received Date:   Emergency Restore Time: 6 HOURS Line Device: EULESS BKR 4225, SWT 4224, SWT 4226 Associated Projects: 16T62055'
        df.at[0, 'Program_Manager'] = 'Michael Howard'
        df.at[0, 'Start_Date'] = pd.to_datetime("today").date()
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=7)

        df.at[1, 'Schedule_Function'] = 'Construction'
        df.at[1, 'PARENT'] = 'Construction Summary'
        df.at[1, 'Program_Manager'] = 'Michael Howard'
        df.at[1, 'Start_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=1)
        df.at[1, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=6)

        self.assertEqual(Create_Task.Create_Task.Create_tasks_no_TOA_inside_Construnction_Summary(df, False), description)

if __name__ == '__main__':
    unittest.main()
