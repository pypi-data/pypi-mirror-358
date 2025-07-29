import os, time
from smiler import smiler
from smiler.operations import binaries
from smiler.reporting import reporter
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.instrumenting import apktool, manifest_instrumenter
from smiler.entities.wd import WorkingDirectory
import acvcut

def main():
    original_apk_path = os.path.join("..", "apks", "simple_apps", "app.apk")
    app_name = os.path.basename(original_apk_path)

    wd_path = os.path.join('..', 'wd_short')
    smali_dir = os.path.join(wd_path, "apktool", acvcut.package, "smali")

    unpacked_app_path = os.path.join(wd_path, "apktool", acvcut.package)
    unpacked_app_path =apktool.decode(original_apk_path, wd_path+"/unpacked")
    smalitree = binaries.load_smalitree(acvcut.cut_smalitree_path)
    instrumentation_pickle_path = smiler.get_pickle_path(app_name[:-4], wd_path)
    instrumenter = Instrumenter(smalitree, acvcut.package)
    instrumenter.save_instrumented_smali(smali_dir)
    binaries.save_pickle(instrumentation_pickle_path)
    
    instrument_manifest(unpacked_app_path)

    instrumented_apk_path = build_n_sign(original_apk_path, wd_path, unpacked_app_path, apktool)
    
    run_acv_online_routine(wd_path, instrumented_apk_path, instrumentation_pickle_path)
    

def run_acv_online_routine(wd_path, instrumented_apk_path, instrumentation_pickle_path):
    report_out = os.path.join(wd_path, "report")

    smiler.uninstall(acvcut.package)
    smiler.install(instrumented_apk_path)
    smiler.start_instrumenting(acvcut.package, release_thread=True)
    os.system("adb shell monkey -p {} 1".format(acvcut.package))
    time.sleep(3)
    smiler.stop_instrumenting(acvcut.package)
    reporter.generate(acvcut.package, instrumentation_pickle_path, report_out)

def build_n_sign(apk_path, wd_path, app_data_path, apktool):
    instrumented_package_path = smiler.get_path_to_instrumented_package(apk_path, wd_path)
    apktool.build(app_data_path, instrumented_apk_path)
    instrumented_apk_path = smiler.get_path_to_insrumented_apk(instrumented_package_path, wd_path)
    smiler.patch_align_sign(instrumented_package_path, instrumented_apk_path)
    return instrumented_apk_path

def instrument_manifest(app_data_path):
    manifest_path = WorkingDirectory.get_manifest_path(app_data_path)
    manifest_instrumenter.instrument_manifest(manifest_path)


if __name__ == "__main__":
    main()


