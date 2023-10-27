from ast import In
import csv
from glob import glob
import time
from typing import Tuple
from dependency_injector.wiring import inject, Provide
from usecases.usecases import DeleteAllDataUseCase, PopulatePrizeData
from texo.containers import ApplicationContainer
from texo.settings import PATH_CSV_FILES_FOLDER_PRODUCTION


class ImportCSVFromFileSystemException(Exception):
    ...


@inject
def import_csv_from_filesystem(
        repository=Provide[ApplicationContainer.prize_repository],
        folder_path=PATH_CSV_FILES_FOLDER_PRODUCTION) -> Tuple[int, int, int, int, list]:
    """This method is the Script that will be resposible to load all the CSV file
    to database.

    It has support to import multiple CSV files from the specified folder at texo.settings
    constant PATH_CSV_FILES_FOLDER_PRODUCTION. It will only get .csv files, event if the folder
    has different extensions.

    Firstly, it creates variables to control the quantity of failures, producers included and rows checked.

    If the folder is empty, it will raise a ImportCSVFromFileSystemException.

    for each csv file, it will create a generator, to avoid to load all the file in memory
    in case the it have a large size.

    It has support in case the user change the column position. So it has a column_map dict that is
    responsible to make the map of the specs sequence and the File Sequence. 

    If the column name is not in the specs, it will raise a ImportCSVFromFileSystemException.

    As the specification requires to separate the Producers, the only delimenter considered in this
    script is 'and' and ','.

    For each producer, it will be populated the database tables using the PopulatePrizeData usecase.

    If the usecase returns a status different of OK, it will raise a ImportCSVFromFileSystemException.

    In the case of the file has the correct extension, but not a valid content. For example, a jpg image with 
    the csv extension, it will throw ImportCSVFromFileSystemException from UnicodeDecodeError.

    Finally, it will return a tuple for control:
    (global_producers_failed_count, global_producers_count, global_row_count, csv_files)

    """
    global_producers_failed_count = 0
    global_producers_count = 0
    global_row_count = 0

    csv_files = glob(f"{folder_path}/*.csv")
    uploaded_files = len(csv_files)
    if uploaded_files == 0:
        raise ImportCSVFromFileSystemException(
            "no csv file uploaded. folder is empty")

    for csv_file_name in csv_files:
        try:
            producers_count = -1
            producers_failed_count = 0
            row_count = 0
            with open(csv_file_name, "r") as csv_file:
                generator = (x for x in csv.DictReader(
                    csv_file,
                    delimiter=";",
                    fieldnames=['year', 'title', 'studios', 'producers', 'winner']))

                column_map = {}
                for row in generator:

                    if producers_count == -1:
                        for k, v in row.items():
                            if k != v:
                                if v in row:
                                    column_map[v] = k
                                    continue
                                raise ImportCSVFromFileSystemException(
                                    f"not uploaded because '{v}' is an invalid column name. It must be 'year','title','studios','producers' or 'winner'")
                            column_map[k] = v
                        producers_count += 1
                        row_count += 1
                        continue

                    try:
                        row_count += 1
                        producers = row[column_map['producers']].strip()
                        producers.replace(" and ", ",")
                        splitted_producers = producers.split(",")

                        for producer in splitted_producers:
                            producers_count += 1
                            year = int(row[column_map['year']])
                            title = row[column_map['title']].strip()
                            studios = row[column_map['studios']].strip()
                            winner = row[column_map['winner']].strip()
                            producer = producer.strip()

                            output = PopulatePrizeData(
                                repo=repository,
                                producer_name=producer,
                                movie_name=title,
                                studios_name=studios,
                                year=year,
                                winner=winner).execute()

                            if output.status != "OK":
                                producers_failed_count += 1
                                DeleteAllDataUseCase(repo=repository)
                                raise ImportCSVFromFileSystemException(
                                    f"on row {row_count}, {output.msg}")

                    except ImportCSVFromFileSystemException as import_csv_error:
                        raise ImportCSVFromFileSystemException(
                            str(import_csv_error)) from import_csv_error
                    except Exception as ex:
                        producers_failed_count += 1
                        DeleteAllDataUseCase(repo=repository)
                        raise ImportCSVFromFileSystemException(
                            f"Unexpected error on row {row_count}") from ex

                    global_producers_failed_count += producers_failed_count
                    global_producers_count += producers_count
                    global_row_count += row_count

        except UnicodeDecodeError as unicode_error:
            raise ImportCSVFromFileSystemException(
                f"It was not possible to read the file {csv_file_name}") from unicode_error

    return global_producers_failed_count, global_producers_count, global_row_count, csv_files
