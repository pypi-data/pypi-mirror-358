
import logging
import os
from context import smiler
from cutter import basic_block, methods
from running import launcher
from apps.app import MyFitnessPal

from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.operations import adb, binaries
'''We search for a class where debloating breaks the app.
- load covered code tree
- debloat classes using binary search
- launch the app to check if it breaks

Precondition: to shrink towards working version with cut_single_dex.py (e.g. clean the not executed methods only).
'''

def binary_debloat_search(smalitree_path, wd, app, start=None, end=None):
    smalitree = binaries.load_smalitree(smalitree_path)
    low = 0 if not start else start
    high = len(smalitree.classes) - 1 if not end else end
    mid = 0
    logging.info("number of classes: {}".format(high+1))
    while low <= high:
        mid = (low + high) // 2
        logging.info("classes: {}-{} to shrink".format(low, mid))
        smalitree = binaries.load_smalitree(smalitree_path)
        success = debloat(smalitree, low, mid, wd, app)
        logging.info("launcher succeded: {} ({}-{})".format(success, low, mid))
        if not success:
            if low == mid or mid - low == 1:
                logging.info("found class {}: {}".format(low, smalitree.classes[low].name))
                return
            high = mid
        else:
            if low == mid or mid - low == 1:
                logging.info("no broken code found")
                return
            low = mid
            high = high+(high-mid)/2


def debloat(smalitree, start, end, wd, app):
    #methods.clean_not_exec_methods_range(smalitree, start, end)
    basic_block.clean_classes(smalitree, start, end)
    instrumenter = Instrumenter(smalitree, "", app.package)
    instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, instrument=False)
    logging.info("assembling...")
    apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
    smiler.patch_align_sign(wd.instrumented_package_path, wd.short_apk_path)
    logging.info("size: {} MB".format(int(os.path.getsize(wd.short_apk_path))/1000000))
    launcher.reinstall_app(app.package, [wd.short_apk_path]+app.supportive_apks)
    res = launcher.launch_log(app.package)
    return res


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    app = MyFitnessPal()
    wd = WorkingDirectory(app.package, "wd")
    dex_number = 5
    smalitree_path = wd.get_shrunk_pickles()[dex_number]
    binary_debloat_search(smalitree_path, wd, app, start=4771, end=9543)
