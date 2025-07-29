'''
This script prepares the working directory "wd" where 
acvtool/acvcut keep all temporary files and results.
'''
from context import smiler

import os, sys, shutil, time
import logging
from procedures import prepare
from running import launcher
from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.reporting.reporter import Reporter
from smiler.instrumenting.utils import Utils
from smiler.instrumenting import apktool

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
# this script is to experiment with twitter app
# adb install-multiple base-s.apk en-s.apk armeabi-s.apk xxhdpi-s.apk
package = "com.twitter.android"
apk_path = "/Users/ap/projects/dblt/googleplay/cmd/googleplay/twitter/adb/base.apk"

wd = WorkingDirectory(package, os.path.join("wd"))

Utils.rm_if_exists(wd.unpacked_apk)
prepare.prepare_wd(wd, apk_path)

smali_dirs = Utils.get_smali_dirs(wd.unpacked_apk)
smiler.instrument_app(wd, smali_dirs)
apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
smiler.patch_align_sign(wd.instrumented_package_path, wd.instrumented_apk_path)
#--
launcher.test_instrumented_detached(wd.instrumented_apk_path, package, wd)
