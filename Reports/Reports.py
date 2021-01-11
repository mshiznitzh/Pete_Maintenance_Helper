
import pandas as pd
from typing import Optional
from xlsxwriter.worksheet import (
    Worksheet, cell_number_tuple, cell_string_tuple, xl_rowcol_to_cell
)





#from xlsxwriter.utility import xl_rowcol_to_cell
from dateutil.tz import tzutc
import numpy as np

def get_column_width(worksheet: Worksheet, column: int) -> Optional[int]:
    """Get the max column width in a `Worksheet` column."""
    strings = getattr(worksheet, '_ts_all_strings', None)
    if strings is None:
        strings = worksheet._ts_all_strings = sorted(
            worksheet.str_table.string_table,
            key=worksheet.str_table.string_table.__getitem__)
    lengths = set()
    for row_id, colums_dict in worksheet.table.items():  # type: int, dict
        data = colums_dict.get(column)
        if not data:
            continue
        if type(data) is cell_string_tuple:
            iter_length = len(strings[data.string])
            if not iter_length:
                continue
            lengths.add(iter_length)
            continue
        if type(data) is cell_number_tuple:
            iter_length = len(str(data.number))
            if not iter_length:
                continue
            lengths.add(iter_length)
    if not lengths:
        return None
    return max(lengths)

def set_column_autowidth(worksheet: Worksheet, column: int):
    """
    Set the width automatically on a column in the `Worksheet`.
    !!! Make sure you run this function AFTER having all cells filled in
    the worksheet!
    """
    maxwidth = get_column_width(worksheet=worksheet, column=column)
    if maxwidth is None:
        return
    worksheet.set_column(first_col=column, last_col=column, width=maxwidth)


def Genrate_Physical_Prints_Report(scheduledf):
    writer = pd.ExcelWriter('Metro West Physical Prints Report.xlsx', engine='xlsxwriter')

    scheduledf = scheduledf[scheduledf['Region_Name'] == 'METRO WEST']

    for district in np.sort(scheduledf.Work_Center_Name.dropna().unique()):

        Energization_df = scheduledf[(scheduledf['Grandchild'] == 'Project Energization') &

                                     (scheduledf['Work_Center_Name'] == district)]


        P_design = scheduledf[(scheduledf['Grandchild'] == 'Physical Design') &

                                           (scheduledf['Work_Center_Name'] == district)]

        Energization_df=Energization_df.assign(Project_Energization = Energization_df['Start_Date'])
        dates = Energization_df[['Project_Energization', 'PETE_ID']]
        P_design = pd.merge(dates, P_design, on=['PETE_ID'], suffixes=('', '_y'), how='right')



        P_design = P_design.assign(Physical_Design_Start=P_design['Start_Date'])
        P_design = P_design.assign(Physical_Design_Finish=P_design['Finish_Date'])

        P_design['Project_Name'] = P_design.Project_Name_x
        P_design['PETE_ID'] = P_design.PETE_ID

        P_design.sort_values(by=['Project_Energization', 'Estimated_In-Service_Date'], inplace=True)
        P_design.set_index('PETE_ID')
       # P_design['Estimated_In-Service_Date'] = P_design['Estimated_In-Service_Date'].dt.date
        P_design['Physical_Design_Start'] = P_design['Physical_Design_Start'].dt.date
        P_design['Physical_Design_Finish'] = P_design['Physical_Design_Finish'].dt.date
       # P_design['Planned_Finish'] = P_design['Planned_Finish'].dt.date
     #   P_design['Actual_Finish'] = P_design['Actual_Finish'].dt.date
        P_design['Project_Energization'] = P_design['Project_Energization'].dt.date


        P_design['Physical_Design_Start'] = P_design['Physical_Design_Start'].dropna().astype(str)
        P_design['Physical_Design_Finish'] = P_design['Physical_Design_Finish'].dropna().astype(str)
        P_design['Project_Energization'] = P_design['Project_Energization'].dropna().astype(str)
        P_design['Estimated_In-Service_Date'] = P_design['Estimated_In-Service_Date'].dropna().astype(str)

        P_design.loc[P_design['Start_Date_Planned\Actual'] == 'A', 'Physical_Design_Start'] = 'Started'
        P_design.loc[P_design['Finish_Date_Planned\Actual'] == 'A', 'Physical_Design_Finish'] = 'Finished'

        outputdf = P_design[list(('PETE_ID',
                                  'Project_Name',
                                  'Physical_Design_Start',
                                  'Physical_Design_Finish',
                                  'Comments',
                                  'Project_Energization',
                                  'Estimated_In-Service_Date',
                                  ))]

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # Save the unformatted results
        outputdf.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
        outputdf.to_excel(writer, index=False, sheet_name=district)

        # Get workbook
        workbook = writer.book
        worksheet = writer.sheets[district]

        # There is a better way to so this but I am ready to move on
        # note that PETE ID is diffrent from the ID used to take you to a website page
        x = 0
        for row in P_design.iterrows():
            worksheet.write_url('A' + str(2 + x),
                                'https://pete.corp.oncor.com/pete.web/project-details/' + str(
                                    P_design['PROJECTID'].values[x]),
                                string=str('%05.0f' % P_design['PETE_ID'].values[x]))  # Implicit format
            x = x + 1

        cell_format = workbook.add_format()
        cell_format.set_align('center')
        worksheet.set_column('A:I', None, cell_format)



        for x  in range(9):
            set_column_autowidth(worksheet, x)

    writer.save()
    writer.close()


def Genrate_Electrical_Prints_Report(scheduledf):
    writer = pd.ExcelWriter('Metro West Electrical Prints Report.xlsx', engine='xlsxwriter')

    scheduledf = scheduledf[scheduledf['Region_Name'] == 'METRO WEST']

    for district in np.sort(scheduledf.Work_Center_Name.dropna().unique()):
        Energization_df = scheduledf[(scheduledf['Grandchild'] == 'Project Energization') &
                                     #(scheduledf['Schedule_Status'] == 'Active') &
                                  #   (scheduledf['Project_Status'] == 'Released') &
                                     (scheduledf['Work_Center_Name'] == district)]

        E_design = scheduledf[(scheduledf['Grandchild'] == 'Electrical Design') &
                                           #(scheduledf['Schedule_Status'] == 'Active') &
                                           #(scheduledf['Project_Status'] == 'Released') &
                                           (scheduledf['Work_Center_Name'] == district)]

        E_design = E_design.assign(Electrical_Design_Start=E_design['Start_Date'])
        E_design = E_design.assign(Electrical_Design_Finish=E_design['Finish_Date'])

        Energization_df=Energization_df.assign(Project_Energization = Energization_df['Start_Date'])
        dates = Energization_df[['Project_Energization', 'PETE_ID']]
        E_design = pd.merge(dates, E_design, on=['PETE_ID'], suffixes=('', '_y'), how='right')

        E_design['Project_Name'] = E_design.Project_Name_x
        E_design['PETE_ID'] = E_design.PETE_ID



        E_design.sort_values(by=['Project_Energization', 'Estimated_In-Service_Date'], inplace=True)
        E_design.set_index('PETE_ID')
        E_design['Estimated_In-Service_Date'] = E_design['Estimated_In-Service_Date'].dt.date
        E_design['Electrical_Design_Start'] = E_design['Electrical_Design_Start'].dt.date
        E_design['Electrical_Design_Finish'] = E_design['Electrical_Design_Finish'].dt.date
        E_design['Planned_Finish'] = E_design['Finish_Date'].dt.date
       # E_design['Actual_Finish'] = E_design['Actual_Finish'].dt.date
        E_design['Project_Energization'] = E_design['Project_Energization'].dt.date


        E_design['Electrical_Design_Start'] = E_design['Electrical_Design_Start'].dropna().astype(str)
        E_design['Electrical_Design_Finish'] = E_design['Electrical_Design_Finish'].dropna().astype(str)
        E_design['Project_Energization'] = E_design['Project_Energization'].dropna().astype(str)
        E_design['Estimated_In-Service_Date'] = E_design['Estimated_In-Service_Date'].dropna().astype(str)

        E_design.loc[E_design['Start_Date_Planned\Actual'] == 'A', 'Electrical_Design_Start'] = 'Started'
        E_design.loc[E_design['Finish_Date_Planned\Actual'] == 'A', 'Electrical_Design_Finish'] = 'Finished'

        Outputdf = E_design[list(('PETE_ID',
                                  'Project_Name',
                                  'Electrical_Design_Start',
                                  'Electrical_Design_Finish',
                                  'Comments',
                                  'Project_Energization',
                                  'Estimated_In-Service_Date',
                                  ))]

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        # Save the unformatted results
        Outputdf.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
        Outputdf.to_excel(writer, index=False, sheet_name=district)

        # Get workbook
        workbook = writer.book
        worksheet = writer.sheets[district]

        # There is a better way to so this but I am ready to move on
        # note that PETE ID is diffrent from the ID used to take you to a website page
        x = 0
        for row in E_design.iterrows():
            worksheet.write_url('A' + str(2 + x),
                                'https://pete.corp.oncor.com/pete.web/project-details/' + str(
                                    E_design['PROJECTID'].values[x]),
                                string=str('%05.0f' % E_design['PETE_ID'].values[x]))  # Implicit format
            x = x + 1

        cell_format = workbook.add_format()
        cell_format.set_align('center')
        worksheet.set_column('A:I', None, cell_format)



        for x  in range(9):
            set_column_autowidth(worksheet, x)

    writer.save()
    writer.close()

def Genrate_Relay_Settings_Report(scheduledf, Relay_Setters_df):
        writer = pd.ExcelWriter('Metro West Relay Settings Report.xlsx', engine='xlsxwriter')

        scheduledf = scheduledf[scheduledf['Region_Name'] == 'METRO WEST']
        scheduledf = pd.merge(scheduledf, Relay_Setters_df[['PETE_ID', 'Relay_Setter_Engineer']], on='PETE_ID')

        for district in np.sort(scheduledf.Work_Center_Name.dropna().unique()):

            filterdf = scheduledf[(scheduledf['Grandchild'] == 'Create Relay Settings') &
                                  # (pd.notnull(scheduledf['Start_Date'])) &
                                  (scheduledf['Work_Center_Name'] == district)]

            Protection_Control_df = scheduledf[((scheduledf['Schedule_Function'].str.match('Material Delivery')) &
                                                (scheduledf['Grandchild'].str.contains('Relay'))) |
                                               ((scheduledf['PARENT'].str.match('Protection and Control')) &
                                                (scheduledf['Grandchild'].str.contains('CONTROL CENTER'))) &
                                               (scheduledf['Work_Center_Name'] == district)]

            Energization_df = scheduledf[(scheduledf['Grandchild'] == 'Project Energization') &
                                         # (scheduledf['Schedule_Status'] == 'Active') &
                                         # (scheduledf['Project_Status'] == 'Released') &
                                         (scheduledf['Work_Center_Name'] == district)]

            Protection_Control_df = Protection_Control_df.sort_values(by=['Start_Date'])
            Protection_Control_df.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
            Protection_Control_df['Earliest_PC_Delivery'] = Protection_Control_df['Start_Date']
            dates = Protection_Control_df[['Earliest_PC_Delivery', 'PETE_ID']]
            filterdf = pd.merge(dates, filterdf, on=['PETE_ID'], suffixes=('', '_y'), how='right')

            Energization_df['Project_Energization'] = Energization_df['Start_Date']
            dates = Energization_df[['Project_Energization', 'PETE_ID']]
            filterdf = pd.merge(dates, filterdf, on=['PETE_ID'], suffixes=('', '_y'), how='right')

            filterdf.sort_values(by=['Project_Energization', 'Estimated_In-Service_Date'], inplace=True)
            filterdf.set_index('PETE_ID')
            filterdf['Estimated_In-Service_Date'] = filterdf['Estimated_In-Service_Date'].dt.date
            filterdf['Start_Date'] = filterdf['Start_Date'].dt.date
            filterdf['Finish_Date'] = filterdf['Finish_Date'].dt.date
            filterdf['Earliest_PC_Delivery'] = filterdf['Earliest_PC_Delivery'].dt.date
            filterdf['Project_Energization'] = filterdf['Project_Energization'].dt.date

            filterdf['Project_Name'] = filterdf.Project_Name_x

            filterdf.loc[filterdf['Start_Date_Planned\Actual'] == 'A', 'Start_Date'] = 'Started'
            filterdf.loc[filterdf['Finish_Date_Planned\Actual'] == 'A', 'Finish_Date'] = 'Finished'

            outputdf = filterdf[list(('PETE_ID',
                                      'Project_Name',
                                      'Start_Date',
                                      'Finish_Date',
                                      'Comments',
                                      'Estimated_In-Service_Date',
                                      'Project_Energization',
                                      'Earliest_PC_Delivery',
                                      'Relay_Setter_Engineer',
                                      ))]

            outputdf['Start_Date'] = outputdf['Start_Date'].dropna().astype(str)
            outputdf['Finish_Date'] = outputdf['Finish_Date'].dropna().astype(str)
            outputdf['Project_Energization'] = outputdf['Project_Energization'].dropna().astype(str)
            outputdf['Earliest_PC_Delivery'] = outputdf['Earliest_PC_Delivery'].dropna().astype(str)
            outputdf['Estimated_In-Service_Date'] = outputdf['Estimated_In-Service_Date'].dropna().astype(str)

            # Create a Pandas Excel writer using XlsxWriter as the engine.
            # Save the unformatted results
            outputdf.drop_duplicates(subset='PETE_ID', keep='last', inplace=True)
            outputdf.to_excel(writer, index=False, sheet_name=district)

            # Get workbook
            workbook = writer.book
            worksheet = writer.sheets[district]

            # There is a better way to so this but I am ready to move on
            # note that PETE ID is diffrent from the ID used to take you to a website page
            x = 0
            for row in filterdf.iterrows():
                worksheet.write_url('A' + str(2 + x),
                                    'https://pete.corp.oncor.com/pete.web/project-details/' + str(
                                        filterdf['PROJECTID'].values[x]),
                                    string=str('%05.0f' % filterdf['PETE_ID'].values[x]))  # Implicit format
                x = x + 1

            cell_format = workbook.add_format()
            cell_format.set_align('center')
            worksheet.set_column('A:I', None, cell_format)

            for x in range(9):
                set_column_autowidth(worksheet, x)

        writer.save()
        writer.close()

def Genrate_Matrial_Report(Material_df, scheduledf):
    for district in np.sort(scheduledf.Work_Center_Name.dropna().unique()):
        writer = pd.ExcelWriter(' '.join([district,'Material Report.xlsx']), engine='xlsxwriter')
        workbook = writer.book
        summarysheet = workbook.add_worksheet('Summary')
        filtereddf = scheduledf[(scheduledf['Work_Center_Name'] == district)]
        row=0
        for project in np.sort(filtereddf.WA_Number.dropna().unique()):

            project_material_df = Material_df[Material_df['PROJECT'] == project]
            if len(project_material_df) >= 1:

                summarysheet.write_url(row, 0, f"internal:'{project}'!A1", string=project)
                summarysheet.write(row, 1, str(scheduledf[(scheduledf['WA_Number']==project)]['Project_Name_x'].values[0]))
                row = row + 1
                project_material_df.to_excel(writer, index=False, sheet_name=project)
                # Get workbook

                worksheet = writer.sheets[project]

                cell_format = workbook.add_format()
                cell_format.set_align('center')
                cell_format.set_align('vcenter')
                worksheet.set_column('A:' + chr(ord('@') + len(project_material_df.columns)), None, cell_format)

                for x in range(len(project_material_df.columns)):
                    set_column_autowidth(worksheet, x)

                wrap_format = workbook.add_format()
                wrap_format.set_text_wrap()
                wrap_format.set_align('vcenter')
                worksheet.set_column('C:C', None, wrap_format)
                worksheet.set_column('C:C', 100)


        writer.save()
        writer.close()