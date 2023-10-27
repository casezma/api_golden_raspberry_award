import glob
import os
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from app.views import get_prize_interval_summary
from scripts.upload_csv_file_from_filesystem import (
    import_csv_from_filesystem, ImportCSVFromFileSystemException)
from texo.settings import PATH_CSV_FILES_FOLDER_TESTS
from infra.django_prize_repository import DjangoPrizeRepository
from app.models import Movie, Prize, Producer, Studios


def delete_all_items():
    Movie.objects.all().delete()
    Prize.objects.all().delete()
    Producer.objects.all().delete()
    Studios.objects.all().delete()


class TestScriptUploadCSVFileFromFileSystem(TestCase):

    def test_if_it_returns_the_right_exception_when_folder_is_empty(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/empty_folder/"
        self.assertEqual(
            glob.glob(f"{PATH_CSV_FILES_FOLDER_TESTS}/empty_folder/*.csv"), [])
        with self.assertRaises(ImportCSVFromFileSystemException) as ex:
            import_csv_from_filesystem(
                repository=DjangoPrizeRepository(), folder_path=folder_path)
        self.assertEqual(str(ex.exception),
                         "no csv file uploaded. folder is empty")
        delete_all_items()

    def test_if_it_returns_the_right_exception_when_year_element_is_empty(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/empty_year/"
        with self.assertRaises(ImportCSVFromFileSystemException) as ex:
            import_csv_from_filesystem(
                repository=DjangoPrizeRepository(), folder_path=folder_path)
        self.assertEqual(str(ex.exception), "Unexpected error on row 3")
        delete_all_items()

    def test_if_it_returns_the_right_exception_when_year_element_is_empty(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/year_is_text/"
        with self.assertRaises(ImportCSVFromFileSystemException) as ex:
            import_csv_from_filesystem(
                repository=DjangoPrizeRepository(), folder_path=folder_path)
        self.assertEqual(str(ex.exception), "Unexpected error on row 5")
        delete_all_items()

    def test_if_it_returns_the_right_exception_when_missing_data(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/missing_data/"
        with self.assertRaises(ImportCSVFromFileSystemException) as ex:
            import_csv_from_filesystem(
                repository=DjangoPrizeRepository(), folder_path=folder_path)
        self.assertEqual(str(ex.exception), "Unexpected error on row 2")
        delete_all_items()

    def test_if_it_returns_the_right_exception_when_changed_column_names(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/changed_column_names/"
        with self.assertRaises(ImportCSVFromFileSystemException) as ex:
            import_csv_from_filesystem(
                repository=DjangoPrizeRepository(), folder_path=folder_path)
        self.assertEqual(str(
            ex.exception), "not uploaded because 'ano' is an invalid column name. It must be 'year','title','studios','producers' or 'winner'")
        delete_all_items()

    def test_if_it_returns_the_right_exception_when_changed_column_names(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/first_row_only/"
        import_csv_from_filesystem(
            repository=DjangoPrizeRepository(), folder_path=folder_path)

    def test_if_it_do_not_raises_exceptions_when_changed_column_names(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/changed_column_positions/"
        import_csv_from_filesystem(
            repository=DjangoPrizeRepository(), folder_path=folder_path)

    def test_if_it_returns_the_right_exception_when_columns_are_missing(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/missing_columns/"
        with self.assertRaises(ImportCSVFromFileSystemException) as ex:
            import_csv_from_filesystem(
                repository=DjangoPrizeRepository(), folder_path=folder_path)
        self.assertEqual(str(
            ex.exception), "not uploaded because 'None' is an invalid column name. It must be 'year','title','studios','producers' or 'winner'")
        delete_all_items()

    def test_if_it_returns_the_right_exception_when_studio_name_is_empty(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/empty_studio_name/"
        with self.assertRaises(ImportCSVFromFileSystemException) as ex:
            import_csv_from_filesystem(
                repository=DjangoPrizeRepository(), folder_path=folder_path)
        self.assertEqual(
            str(ex.exception), "on row 6, Object not Created the fields Studios are invalid")
        delete_all_items()

    def test_if_it_returns_the_right_exception_when_the_extention_file_is_wrong(self):
        folder_path = os.path.join(
            PATH_CSV_FILES_FOLDER_TESTS, "wrong_extention_file")
        filename = os.path.join(folder_path, "wrong_extention_file.csv")
        with self.assertRaises(ImportCSVFromFileSystemException) as ex:
            import_csv_from_filesystem(
                repository=DjangoPrizeRepository(), folder_path=folder_path)
        self.assertEqual(str(ex.exception),
                         f"It was not possible to read the file {filename}")
        delete_all_items()

    def test_if_it_returns_the_right_exception_when_winner_is_not_yes_or_empty(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/winner_is_not_yes_or_empty/"
        with self.assertRaises(ImportCSVFromFileSystemException) as ex:
            import_csv_from_filesystem(
                repository=DjangoPrizeRepository(), folder_path=folder_path)
        self.assertEqual(str(
            ex.exception), "on row 3, Object not Created winner field is invalid. Must be 'yes' or ''")
        delete_all_items()

    def test_if_it_returns_it_does_not_throw_exception_with_multiple_files(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/multiple_files/"
        failed_count, producers_count, row_count, csv_files = import_csv_from_filesystem(
            repository=DjangoPrizeRepository(), folder_path=folder_path)
        self.assertEqual(len(csv_files), 5)
        self.assertEqual(failed_count, 0)
        delete_all_items()


class TestGetPrizeIntervalView(APITestCase):
    def test_if_it_returns_right_values_the_file_is_valid(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/default/"
        import_csv_from_filesystem(
            repository=DjangoPrizeRepository(), folder_path=folder_path)
        url = reverse('get_prize_interval_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        data = {
            "min": [
                {
                    "producer": "Bo Derek",
                    "interval": 6,
                    "previousWin": 1984,
                    "followingWin": 1990
                }
            ],
            "max": [
                {
                    "producer": "Matthew Vaughn",
                    "interval": 13,
                    "previousWin": 2002,
                    "followingWin": 2015
                }
            ]
        }
        self.assertEqual(data, response.data)

    def test_if_it_returns_right_values_when_prize_is_requested(self):
        folder_path = f"{PATH_CSV_FILES_FOLDER_TESTS}/empty_folder/"
        with self.assertRaises(ImportCSVFromFileSystemException) as ex:
            import_csv_from_filesystem(
                repository=DjangoPrizeRepository(), folder_path=folder_path)
        self.assertEqual(str(ex.exception),
                         "no csv file uploaded. folder is empty")
        url = reverse('get_prize_interval_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIsInstance(response.data, dict)
        data = {
            "error": "Database is empty. Your CSV file must be empty or with some issues, fix it and run the application later."
        }
        self.assertEqual(data, response.data)
