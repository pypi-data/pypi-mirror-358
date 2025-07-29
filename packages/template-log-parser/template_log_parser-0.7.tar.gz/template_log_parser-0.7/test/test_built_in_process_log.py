import unittest
import pandas as pd
import pandas.api.types as ptypes
from typing import get_type_hints

from template_log_parser.built_ins import built_in_process_log
from template_log_parser.log_type_classes import built_in_log_file_types

class TestBuiltInProcessLog(unittest.TestCase):
    """Defines a class to test built in process log"""
    def test_built_process_log_types(self):
        """Assert built_in_process_log returns the expected types"""
        for built_in in built_in_log_file_types:
            print("Testing built_in_process_log: ", built_in.name)
            print('Testing DF format')
            df = built_in_process_log(built_in.name, built_in.sample_log_file, dict_format=False)
            self.assertIsInstance(df, pd.DataFrame)

            if built_in.datetime_columns:
                for datetime_column in built_in.datetime_columns:
                    if datetime_column in df.columns:
                        self.assertTrue(ptypes.is_datetime64_any_dtype(df[datetime_column]))
                        print(datetime_column, "is a proper datetime column")

            if built_in.column_functions:
                print("Testing column functions")
                for original_column, (func, new_column) in built_in.column_functions.items():
                    self.assertTrue(original_column not in df.columns)
                    print("Column has been correctly removed: ", original_column)

                    if type(new_column) is str:
                        self.assertTrue(new_column in df.columns)
                        print("Column has been correctly added:", new_column)

                    elif type(new_column) is list:
                        for column in new_column:
                            print("Column has been correctly added:", column)
                            self.assertTrue(column in df.columns)

            print('Testing dictionary format')
            df_dict = built_in_process_log(built_in.name, built_in.sample_log_file, dict_format=True)
            self.assertIsInstance(df_dict, dict)

            for event, df in df_dict.items():
                print("Event:", event)
                if built_in.datetime_columns:
                    for datetime_column in built_in.datetime_columns:
                        if datetime_column in df.columns:
                            self.assertTrue(ptypes.is_datetime64_any_dtype(df[datetime_column]))
                            print(datetime_column, "is a proper datetime column")

            print(built_in.name, "Ok")
