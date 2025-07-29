import logging

from context import smiler
from context import apps

from smiler import smiler
from apps.app import CurrentApp
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.operations import binaries
'''Looking for an issue why instrumentation breaks building specific dex file.
'''


def binary_instrument_search(smalitree_path):
    smalitree = binaries.load_smalitree(smalitree_path)
    low = 0
    high = len(smalitree.classes)
    mid = 0
    logging.info("number of classes: {}:".format(high+1))
    while low <= high:
        mid = (low + high) // 2
        logging.info("classes: {}-{} to shrink".format(low, mid))
        success = instrument(smalitree, low, mid)
        logging.info("build succeded: {} ({} - {})".format(success, low, mid))
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
        if low <= high: # recover original smalitree for the next iteration
            smalitree = binaries.load_smalitree(smalitree_path)


def instrument(smalitree):
    smali_instrumenter = Instrumenter(smalitree, None, None)
    smali_instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, True)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

    app = CurrentApp()
    wd = WorkingDirectory(app.package, "wd")
    dex_number = 1
    smalitree_path = wd.get_pickles()[dex_number]
    smalitree = binaries.load_smalitree(smalitree_path)
    instrument(smalitree)
    print(wd.instrumented_package_path)
    result = apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
    #binary_instrument_search(smalitree_path)
