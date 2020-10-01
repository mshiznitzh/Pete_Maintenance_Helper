import unittest
import pandas as pd
import os
import Pete_Maintenace_Helper

class TaskCreationTest(unittest.TestCase):
    def test_Create_task_for_Relay_Settings_Finish_date(self):


        description = 'Check with Relay Setter on when settings are going to be issued'
        os.chdir("./Test_Data/")
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
        df.at[0, 'Start_Date_Planned\Actual'] = 'A'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Pete_Maintenace_Helper.Create_task_for_Relay_Settings(df, False), description)

    def test_Create_task_for_Relay_Settings_start_date(self):

        description = 'Check with Relay Setter on when settings are going to be started'
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Pete_Maintenace_Helper.Create_task_for_Relay_Settings(df, False), description)

    def test_Create_tasks_for_Engineering_Activities_Start_Dates_ED(self):

        description = 'Check with Engineering on if Electrical Designs were started'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Electrical Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Start_Dates(df,False), description)

    def test_Create_tasks_for_Engineering_Activities_Start_Dates_PD(self):

        description = 'Check with Engineering on if Physical Designs were started'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Physical Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Start_Dates(df,False), description)

    def test_Create_tasks_for_Engineering_Activities_Start_Dates_FD(self):

        description = 'Check with Engineering on if Foundation Designs were started'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Foundation Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Start_Dates(df,False), description)

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


        self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Start_Dates(df,False), description)

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

            self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Start_Dates(df, False),
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

            self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Start_Dates(df, False),
                             description)

    def test_Create_tasks_for_Engineering_Activities_Finish_Dates_ED(self):

        description = 'Check with Engineering on if Electrical Designs were issued'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Electrical Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
        df.at[0, 'Start_Date_Planned\Actual'] = 'A'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Finish_Dates(df,False), description)

    def test_Create_tasks_for_Engineering_Activities_Finish_Dates_PD(self):

        description = 'Check with Engineering on if Physical Designs were issued'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Physical Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
        df.at[0, 'Start_Date_Planned\Actual'] = 'A'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Finish_Dates(df,False), description)

    def test_Create_tasks_for_Engineering_Activities_Finish_Dates_FD(self):

        description = 'Check with Engineering on if Foundation Designs were issued'

        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Foundation Design'
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
        df.at[0, 'Start_Date_Planned\Actual'] = 'A'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Finish_Dates(df,False), description)

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


        self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Finish_Dates(df,False), description)

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

            self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Start_Dates(df, False),
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

            self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Engineering_Activities_Start_Dates(df, False),
                             description)

    def test_Create_tasks_for_Construncction_Task_Request_Approval(self):

        description = 'Ask Engineering for update on Construction Task Request Approval'
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0, 'Grandchild'] = 'Construction Task Request Approval'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'
        df.at[0, 'Program_Manager'] = 'Michael Howard'

        self.assertEqual(Pete_Maintenace_Helper.Create_tasks_for_Construncction_Task_Request_Approval(df, False), description)

if __name__ == '__main__':
    unittest.main()
