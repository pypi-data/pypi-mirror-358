import os, shutil, time
from smiler import smiler
from smiler.reporting import reporter
from smiler.libs.libs import Libs
from smiler.granularity import Granularity
from smiler.instrumenting.utils import Utils
import argparse

parser = argparse.ArgumentParser(description='Prepares the working directory.')
parser.add_argument("-k", "--keepsource", action="store_true", help="keeps apktool's generated sources", required=False)
parser.add_argument("apk_path", metavar="apk_path", help="path to the original apk")
parser.add_argument("--wd", metavar="wd", help="path to the working directory")
parser.add_argument("--package", metavar="package", help="app package name")

args = parser.parse_args()
wd_path = args.wd # acvcut.wd_path
apk_path = args.apk_path # acvcut.apk_path
package = args.package # acvcut.package
keepsource = args.keepsource # acvcut.keepsource

ignore_methods = None # list of methods to ignore coverage measurement 

apktool = Libs.APKTOOL_PATH

app_name = os.path.basename(apk_path)
acv_wd = os.path.join("wd")

pickle = os.path.join(acv_wd, "metadata", app_name[:-3]+'pickle')
pickle_wd = os.path.join(wd_path, "metadata", os.path.basename(pickle))
instr_apk = os.path.join(acv_wd, "instr_"+ app_name)
instr_apk_wd = os.path.join(wd_path, "instr_"+ app_name)

decompiled_app_dir = os.path.join(wd_path, "dec_apk")
smali_dir = os.path.join(decompiled_app_dir, "smali")
smali_dir_cp = os.path.join(wd_path, "smali_orig")

report_out = os.path.join(wd_path)

DEBUG = False

if not DEBUG and os.path.exists(wd_path):
    Utils.recreate_dir(wd_path)
    shutil.rmtree(wd_path)
    os.makedirs(wd_path)

# prepare apktool dirs 
if not DEBUG:
    cmd_dec = "java -jar {} d {} -o {}".format(apktool, apk_path, decompiled_app_dir)
    os.system(cmd_dec)
    shutil.copytree(smali_dir, smali_dir_cp)
else:
    shutil.rmtree(smali_dir)
    shutil.copytree(smali_dir_cp, smali_dir)

smiler.instrument_apk(apk_path, acv_wd, ignore_filter=ignore_methods, keep_unpacked=keepsource)

# if DEBUG:
#     sys.exit()
# copy instrumented metadata
dirname = os.path.dirname(pickle_wd)
if not os.path.exists(dirname):
    os.makedirs(dirname)
#shutil.copy(pickle, pickle_wd)
#shutil.copy(instr_apk, instr_apk_wd)
#shutil.rmtree(acv_wd)

# continue acvtool flow
# acvtool (run emulator first)
#smiler.uninstall(package)
smiler.install(instr_apk_wd)
os.system("adb logcat -c")
smiler.start_instrumenting(package, release_thread=True)
# time.sleep(1)
# os.system("adb shell monkey -p {} 1".format(package))

raw_input("Test the app and press Enter to continue...")
time.sleep(1)
smiler.stop_instrumenting(package)
reporter.generate(package, pickle_wd, report_out, ignore_filter=ignore_methods)
print("report: {}".format(report_out))
