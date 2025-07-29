import logging
import time
from context import smiler
from running import launcher
from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.operations import adb

'''this experiment to find out how does coverage chang over time on a single test'''


def main():
    package = "com.twitter.android"
    wd = WorkingDirectory(package, "wd")
    launcher.twi_reinstall_launch(wd.instrumented_apk_path, package, grant_permissions=False)
    smiler.grant_storage_permission(package)
    adb.create_app_sdcard_dir(package)
    j = 5
    while j > 0:
        logging.info("runnning: {}".format(j))
        i = 30 # 30 savings -> 300 seconds -> 5 minutes
        while i > 0:
            logging.info("saving coverage {}".format(i))
            adb.save_coverage(package)
            time.sleep(10)
            i -= 1
        logging.info("pulling")
        smiler.get_execution_results(package, wd.ec_dir, wd.images)
        j -= 1
    logging.info("done")



if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    main()