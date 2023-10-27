from django.apps import AppConfig
from django.core import management


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self) -> None:
        """As this method runs after the Django setup is ready, it will be responsible to:
        - makemigrations (if it was not done yet)
        - migrate the database (as this database is configured to be InMemory, this process will
        be repeated every time when the application initialize.)]
        - initialize the dependency injector container for the app and script packages
        - runs the 'import_csv_from_filesystem' script, that will import all the data from the CSV file
        inside the folder pointed on texo.settings.py file in the constant PATH_CSV_FILES_FOLDER_PRODUCTION 
        """
        management.call_command("makemigrations", "app")
        management.call_command("migrate")
        from texo.containers import application_container
        from scripts.upload_csv_file_from_filesystem import import_csv_from_filesystem
        application_container.wire(packages=['app', 'scripts'])
        failed_count, producers_count, row_count, _ = import_csv_from_filesystem()

        print("\n\n***Server listening, please follow the README.md instructions.***\n")
        print(f"{producers_count - failed_count} of {producers_count} producers data imported to database in {row_count} rows checked.\n\n")
