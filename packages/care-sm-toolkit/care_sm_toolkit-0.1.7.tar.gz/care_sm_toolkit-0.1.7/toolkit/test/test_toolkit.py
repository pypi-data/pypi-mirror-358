import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import os

from toolkit.main import Toolkit  # Adjust the import to your actual module path

class TestToolkit(unittest.TestCase):

    def setUp(self):
        self.toolkit = Toolkit()
        self.sample_df = pd.DataFrame({
            "model": ["Sex"],
            "pid": ["001"],
            "event_id": ["E001"],
            "value": ["M"],
            "age": [30],
            "value_datatype": ["xsd:string"],
            "valueIRI": ["http://example.org/sex/male"],
            "activity": [None],
            "unit": [None],
            "input": [None],
            "target": [None],
            "protocol_id": [None],
            "frequency_type": [None],
            "frequency_value": [None],
            "agent": [None],
            "startdate": ["2021-01-01"],
            "enddate": [None],
            "comments": [None]
        })

    @patch('os.listdir')
    def test_find_matching_files(self, mock_listdir):
        mock_listdir.return_value = ["Sex.csv", "Diagnosis.csv"]
        result = self.toolkit.toolkit._find_matching_files("/toolkit/data")
        self.assertEqual(result, [os.path.join("Diagnosis.csv", "Sex.csv")])

    # @patch("builtins.open", new_callable=mock_open, read_data="model,pid,event_id,value")
    # @patch("pandas.read_csv")
    # def test_import_your_data_from_csv_success(self, mock_read_csv, mock_file):
    #     mock_read_csv.return_value = self.sample_df
    #     df = self.toolkit.import_your_data_from_csv("somefile.csv")
    #     self.assertIsNotNone(df)

    # @patch("pandas.read_csv", side_effect=Exception("Error"))
    # def test_import_your_data_from_csv_fail(self, mock_read_csv):
    #     df = self.toolkit.import_your_data_from_csv("badfile.csv")
    #     self.assertIsNone(df)

    # def test_check_status_column_names_valid(self):
    #     df = self.sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    #     result = self.toolkit.check_status_column_names(df.copy())
    #     self.assertTrue(all(col in result.columns for col in Toolkit.columns))

    # def test_check_status_column_names_invalid(self):
    #     df = self.sample_df.copy()
    #     df["unexpected"] = "value"
    #     with self.assertRaises(ValueError):
    #         self.toolkit.check_status_column_names(df)

    # @patch("perseo.main.milisec", return_value="123456")
    # @patch("your_module_path.Template.template_model", {"Sex": {"additional": "data"}})
    # def test_add_columns_from_template(self, mock_template, mock_milisec):
    #     df = self.sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    #     enriched = self.toolkit.add_columns_from_template(df, "some.csv")
    #     self.assertIn("additional", enriched.columns)

    # def test_value_edition(self):
    #     df = self.sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    #     edited = self.toolkit.value_edition(df.copy())
    #     self.assertIn("value_string", edited.columns)
    #     self.assertEqual(edited.loc[0, "value_string"], "M")
    #     self.assertEqual(edited.loc[0, "attribute_type"], "http://example.org/sex/male")

    # def test_time_edition(self):
    #     df = self.sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    #     edited = self.toolkit.time_edition(df.copy())
    #     self.assertEqual(edited.loc[0, "enddate"], "2021-01-01")

    # def test_clean_empty_rows(self):
    #     df = self.sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    #     cleaned = self.toolkit.clean_empty_rows(df.copy(), "fake.csv")
    #     self.assertEqual(len(cleaned), 1)

    # def test_delete_extra_columns(self):
    #     df = self.sample_df.copy()
    #     df["extra"] = "something"
    #     deleted = self.toolkit.delete_extra_columns(df)
    #     for col in Toolkit.drop_columns:
    #         self.assertNotIn(col, deleted.columns)

    # @patch("perseo.main.milisec", return_value="123456789")
    # def test_unique_id_generation(self, mock_milisec):
    #     df = self.sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    #     result = self.toolkit.unique_id_generation(df.copy())
    #     self.assertIn("uniqid", result.columns)
    #     self.assertEqual(result.loc[0, "uniqid"], "123456789")

    # @patch.object(Toolkit, '_find_matching_files')
    # @patch.object(Toolkit, '_process_file')
    # @patch("pandas.DataFrame.to_csv")
    # def test_whole_method(self, mock_to_csv, mock_process_file, mock_find_files):
    #     mock_find_files.return_value = ["f1.csv"]
    #     mock_process_file.return_value = self.sample_df.reindex(columns=Toolkit.columns, fill_value=None)
    #     self.toolkit.whole_method("folder_path")
    #     mock_to_csv.assert_called_once()

if __name__ == "__main__":
    unittest.main()