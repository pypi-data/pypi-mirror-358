import os
import re
import sys
import time
import logging
from analysis import smali
from cutter import basic_block
from running import launcher
from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.instrumenting.utils import Utils
from smiler.operations import binaries

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

package = "com.twitter.android"
pickle_path = "wd/covered_stubbed_1.pickle"

wd_path = "wd"
wd = WorkingDirectory(package, "wd")
dex_number = 1 

smalitree = binaries.load_smalitree(pickle_path)
smali.insns_stats(smalitree)
basic_block.remove_blocks_from_selected_method(smalitree)
#sys.exit()
smali.insns_stats(smalitree)
instrumenter = Instrumenter(smalitree, "", package)
instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, instrument=False)
#sys.exit()
classes_path = os.path.join(wd.unpacked_apk, "smali" if dex_number == 1 else "classes{}".format(dex_number))
out_dex_path = "/Users/ap/projects/dblt/acvcut/wd/base/classes{}.dex".format(dex_number if dex_number > 1 else "")
Utils.rm_if_exists(out_dex_path)
cmd = "java -jar ~/distr/smali-2.5.2.jar assemble {} -o {}".format(classes_path, out_dex_path)
smiler.request_pipe(cmd)
#sys.exit()
result_apk = launcher.build_n_sign("/Users/ap/projects/dblt/acvcut/wd/base", package)
launcher.twi_reinstall_launch(result_apk, package)
