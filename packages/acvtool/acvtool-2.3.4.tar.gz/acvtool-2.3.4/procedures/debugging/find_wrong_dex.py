import logging
import os

from context import smiler
from analysis.smali import StatsCounter
from cutter import basic_block, methods
from smiler import smiler
from running import launcher
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.instrumenting.utils import Utils
from smiler.operations import binaries
import copy_original_code

'''This script looks for the messed up dex code directory.
It sequentially removes and copies dex directories, builds the app and checks if it fails.
When the app does not fail anymore then the previous dex directory was corrupt.'''

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

def shrink_tree(smalitree, stub_dir):
    methods.clean_not_executed_methods(smalitree)
    basic_block.remove_blocks_from_selected_method(smalitree)

package = "com.twitter.android"
wd = WorkingDirectory(package, "wd")
dexs = wd.get_smali_dirs(wd.unpacked_apk)
pickle_files = wd.get_covered_pickles()

copy_original_code(wd)
counter = StatsCounter()
for dex_number in dexs.keys():
    logging.info("processing dex: {}".format(dex_number))
    pickle_path = pickle_files[dex_number]
    smalitree = binaries.load_smalitree(pickle_path)
    counter.put_original(smalitree)
    shrink_tree(smalitree, wd.stub_dir)
    counter.put_shrunk(smalitree)
    instrumenter = Instrumenter(smalitree, "", wd.package)
    instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, instrument=False)
    apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
    smiler.patch_align_sign(wd.instrumented_package_path, wd.short_apk_path)
    result = launcher.twi_reinstall_launch(wd.short_apk_path, package)
    if not result:
        logging.info("reinstall failed on the dex number: {}".format(dex_number))
        break
    dex_path = dexs[dex_number]
    orig_dex_path = os.path.join(wd.decompiled_apk, os.path.basename(dex_path))
    Utils.rm_if_exists(dex_path)
    Utils.copytree(orig_dex_path, dex_path)
    

