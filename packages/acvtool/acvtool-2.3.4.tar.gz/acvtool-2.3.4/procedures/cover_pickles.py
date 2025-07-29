import os
import logging
from context import smiler
from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.operations import adb, coverage
from apps.app import CurrentApp


'''
Cumulatively applies ec coverage onto smalitrees.

Precondition: pull_coverage.py
'''

def main():
    app = CurrentApp()
    wd = WorkingDirectory(app.package, "wd")
    if not os.path.isdir(wd.covered_pickle_dir):
        os.makedirs(wd.covered_pickle_dir)
    smiler.grant_storage_permission(app.package)
    adb.send_broadcast("tool.acv.snap", wd.package)
    smiler.get_execution_results(wd.package, wd.ec_dir, wd.images)
    coverage.cover_pickles(wd)
    os.system("rm wd/ec_files/*")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    main()