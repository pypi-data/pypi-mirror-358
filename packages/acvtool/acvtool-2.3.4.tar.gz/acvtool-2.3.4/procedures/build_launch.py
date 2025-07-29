import logging
import os
import sys
from context import smiler
from apps.app import CurrentApp
from running import launcher
from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
app = CurrentApp()
wd = WorkingDirectory(app.package, "wd")
logging.info("assembling...")
apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
smiler.patch_align_sign(wd.instrumented_package_path, wd.short_apk_path)
launcher.reinstall_app(wd.package, [wd.short_apk_path]+app.supportive_apks)
launcher.launch(app.package)
