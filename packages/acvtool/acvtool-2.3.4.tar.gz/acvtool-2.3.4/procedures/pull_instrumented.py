import logging
from context import smiler
from procedures import cover_pickles
from smiler import smiler
from apps.app import CurrentApp
from smiler.entities.wd import WorkingDirectory
from smiler.operations import adb


def main():
    app = CurrentApp()

    wd = WorkingDirectory(app.package, "wd")
    #Utils.recreate_dir(wd.report)
    smiler.get_execution_results(wd.package, wd.ec_dir, wd.images)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    main()
    #cover_pickles.main()