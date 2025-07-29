''' Run full acvtool cycle on an apk to check if it works.'''

import os, sys, shutil

from smiler.config import config
from smiler.reporting import reporter
from smiler import instrumenting
from smiler.libs.libs import Libs
from smiler import smiler
import acvcut

def main():
    wd_path = os.path.join('..', 'wd_acvtest')
    instr_apk = os.path.join(wd_path, "instr_app.apk")
    instr_pickle_path = os.path.join(wd_path, 'metadata', 'app.pickle')
    ecdir = os.path.join("..", 'wd', 'report', "io.pilgun.multidexapp","ec_files")
    stubs_path = os.path.join('..', 'wd', 'stubs.txt')

    #smiler.instrument_apk(acvcut.apk_path, wd_path, ignore_filter=stubs_path)
    # smiler.install(instr_apk)
    # smiler.start_instrumenting(acvcut.package, True)
    # os.system("adb shell monkey -p {} 1".format(acvcut.package))
    # smiler.stop_instrumenting(acvcut.package)
    # smiler.get_execution_results(package_name, ec_dir, images_dir)
    reporter.generate(acvcut.package, instr_pickle_path, wd_path, ec_dir=ecdir, ignore_filter=stubs_path)



if __name__ == "__main__":
    main()