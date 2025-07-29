import logging
from context import smiler
from analysis import smali
from running import launcher
from smiler import smiler
from cutter import basic_block
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.operations import binaries
'''This is the shortened version of the run_cut_single_dex.py'''
logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

package = "com.twitter.android"
stubbed_pickle = "wd/stubbed_1.pickle"
smalitree = binaries.load_smalitree(stubbed_pickle)
smali.insns_stats(smalitree)
basic_block.clean_class_by_name(smalitree, 
    # "Landroidx/appcompat/app/d;",
    # "A(Landroidx/appcompat/app/d;)V")
"Lcom/google/android/gms/dynamite/DynamiteModule;",
"f(Landroid/content/Context;Ljava/lang/String;Z)I")
smali.insns_stats(smalitree)
instrumenter = Instrumenter(smalitree, "", "method", package)
instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, instrument=False)
wd = WorkingDirectory(package, "wd")
apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
smiler.patch_align_sign(wd.instrumented_package_path, wd.short_apk_path)
launcher.twi_reinstall_launch(wd.short_apk_path, package)
