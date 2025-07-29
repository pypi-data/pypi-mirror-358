import os
import logging
import time
from running import launcher
from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting.utils import Utils
from smiler.operations import adb, coverage
from smiler.reporting.reporter import Reporter

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

package = "com.twitter.android"
wd = WorkingDirectory(package, os.path.join("wd"))

adb.delete_app_sdcard_dir(package)
#launcher.test_instrumented_detached(wd.instrumented_apk_path, package, wd)
launcher.twi_reinstall_launch(wd.instrumented_apk_path, package, grant_permissions=False)
raw_input("Test the app and press Enter to continue...")
time.sleep(1)
Utils.recreate_dir(wd.report)
Utils.recreate_dir(wd.ec_dir)
adb.create_app_sdcard_dir(package)
smiler.grant_storage_permission(package)
adb.save_coverage(package)
smiler.get_execution_results(package, wd.ec_dir, wd.images)
Utils.recreate_dir(wd.report)
Utils.mkdirs(wd.covered_pickle_dir)
coverage.cover_pickles(wd)
# reporter = Reporter(package, wd.get_covered_pickles(), wd.images, wd.report)
# reporter.generate(html=True, xml=False, concise=False)
