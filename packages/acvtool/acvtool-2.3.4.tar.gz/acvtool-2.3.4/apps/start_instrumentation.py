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
    smiler.start_instrumenting(app.package)
    

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    main()
    