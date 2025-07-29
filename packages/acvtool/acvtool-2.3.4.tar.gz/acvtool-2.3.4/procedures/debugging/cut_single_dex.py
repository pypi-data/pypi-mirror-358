import logging
import os
import sys
from context import smiler
from apps.app import MyFitnessPal
from cutter import basic_block, methods
from running import launcher
from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.instrumenting.utils import Utils
from smiler.operations import binaries

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

app = MyFitnessPal()
wd = WorkingDirectory(app.package, "wd")
dex_number = 1
smalitree_path = wd.get_shrunk_pickles()[dex_number]
dexs = wd.get_smali_dirs(wd.unpacked_apk)

smalitree = binaries.load_smalitree(smalitree_path)
methods.clean_not_executed_methods(smalitree)
basic_block.remove_blocks_from_selected_method(smalitree)
#binaries.save_pickle(smalitree, os.path.join(wd.shrunk_pickle_dir, "{}_{}.pickle".format(app.package, dex_number)))
#sys.exit()
instrumenter = Instrumenter(smalitree, "", "method", wd.package)
instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, instrument=False)
apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
smiler.patch_align_sign(wd.instrumented_package_path, wd.short_apk_path)
launcher.reinstall_app(app.package, [wd.short_apk_path]+app.supportive_apks)
result = launcher.launch_log(app.package)
logging.info("result: {}".format(result))
