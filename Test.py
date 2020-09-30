import unittest
import pandas as pd
import os
from Pete_Maintenace_Helper import Create_task_for_Relay_Settings
import sys

class TaskCreationTest(unittest.TestCase):
    def test_Create_task_for_Relay_Settings_Finish_date(self):


        description = 'Check with Relay Setter on when settings are going to be issued'
        os.chdir("./Test_Data/")
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=10)
        df.at[0, 'Start_Date_Planned\Actual'] = 'A'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() - pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_task_for_Relay_Settings(df), description)

    def test_Create_task_for_Relay_Settings_start_date(self):

        description = 'Check with Relay Setter on when settings are going to be started'
        df = pd.read_csv('Create_task_for_Relay_Settings_Test_Data.csv')
        df.at[0,'Start_Date'] = pd.to_datetime("today").date() -  pd.DateOffset(days=5)
        df.at[0, 'Start_Date_Planned\Actual'] = 'P'
        df.at[0, 'Finish_Date'] = pd.to_datetime("today").date() + pd.DateOffset(days=5)
        df.at[0, 'Finish_Date_Planned\Actual'] = 'P'

        self.assertEqual(Create_task_for_Relay_Settings(df), description)




if __name__ == '__main__':
    unittest.main()
