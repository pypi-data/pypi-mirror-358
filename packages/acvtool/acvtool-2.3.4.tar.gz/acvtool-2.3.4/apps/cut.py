import os
import logging
import shutil
import sys
from context import smiler
from running import launcher
import refresh_mfp_wd
from smiler import smiler
from analysis.smali import StatsCounter
from cutter import basic_block, invokes, methods
from procedures import prepare
from app import CurrentApp
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.instrumenting.utils import Utils
from smiler.operations import binaries


def shrink_tree(smalitree, stub_dir):
    methods.clean_not_executed_methods(smalitree)


def debloat_app_code(wd):
    pickle_files = wd.get_covered_pickles()
    counter = StatsCounter()
    for dex_number in range(1, len(pickle_files)+1):
        logging.info("processing dex: {}".format(dex_number))
        pickle_path = pickle_files[dex_number]
        smalitree = binaries.load_smalitree(pickle_path)
        counter.put_original(smalitree)
        shrink_tree(smalitree, wd.stub_dir)
        basic_block.remove_blocks_from_selected_method(smalitree)
        binaries.save_pickle(smalitree, os.path.join(wd.shrunk_pickle_dir, "{}_{}.pickle".format(wd.package, dex_number)))
        counter.put_shrunk(smalitree)
        instrumenter = Instrumenter(smalitree, "", "method", wd.package)
        instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, instrument=False)
        #builder.build_dex(smaliclasses_dirs[dex_number], output_dexs[dex_number])
    counter.log_total()


def main():
    app = CurrentApp()
    wd = WorkingDirectory(app.package, "wd")
    prepare.refresh_wd_no_smali(wd) # important after instrumentation
    # refresh_mfp_wd.copy_smali_dirs(wd) # specific to the app dex reallocation
    debloat_app_code(wd)
    apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
    smiler.patch_align_sign(wd.instrumented_package_path, wd.short_apk_path)
    logging.info("size: {} MB".format(int(os.path.getsize(wd.short_apk_path))/1000000))
    launcher.reinstall_app(app.package, [wd.short_apk_path]+app.supportive_apks)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s%(levelname)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    logging.addLevelName(logging.WARNING, " \033[91mW\033[0m")
    logging.addLevelName(logging.INFO, "")
    main()
