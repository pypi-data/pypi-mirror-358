import logging
import os
import shutil
from context import smiler
from smiler import smiler
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.instrumenting.apkil.smalitree import SmaliTree
logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

package = "com.twitter.android"
smali_dir = "wd/dec_apk/smali_classes12"
lesssmali_dir = "wd/lesssmali12"
if not os.path.isdir(lesssmali_dir):
    logging.info("copying code")
    shutil.copytree(smali_dir, lesssmali_dir)
logging.info("reading")
smalitree = SmaliTree(1, lesssmali_dir)
instrumenter = Instrumenter(smalitree, "", "method", package)
instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, instrument=False)
logging.info("done")