
import logging
import os
from context import smiler
from running import launcher
from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting.utils import Utils
logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
package = "com.twitter.android"
wd = WorkingDirectory(package, "wd_test")
dex_number = 1

classes_path = os.path.join(wd.unpacked_apk, "smali" if dex_number == 1 else "smali_classes{}".format(dex_number))
out_dex_path = "wd/base/classes{}.dex".format(dex_number if dex_number > 1 else "")
Utils.rm_if_exists(out_dex_path)
cmd = "java -jar ~/distr/smali-2.5.2.jar assemble {} -o {}".format(classes_path, out_dex_path)
print(cmd)
os.system(cmd)
#sys.exit()
result_apk = launcher.build_n_sign("wd/base", package)
launcher.twi_reinstall_launch("wd/test-s.apk", package)