import os
import logging
import sys
from context import smiler

from smiler import smiler
from procedures import prepare
from running import launcher
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool
from smiler.instrumenting.utils import Utils
from procedures import run_cut_single_dex
from tests import test_reporter
import cut_twi

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
package = "com.twitter.android"
apk_path = "/Users/ap/projects/dblt/googleplay/cmd/googleplay/twitter/adb/base.apk"

wd = WorkingDirectory(package, os.path.join("wd"))

Utils.rm_if_exists(wd.unpacked_apk)
prepare.prepare_wd(wd, apk_path)
smali_dirs = Utils.get_smali_dirs(wd.unpacked_apk)
smiler.instrument_app(wd, smali_dirs)
#sys.exit()
apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
smiler.patch_align_sign(wd.instrumented_package_path, wd.instrumented_apk_path)
launcher.twi_reinstall_launch(wd.instrumented_apk_path, package)
