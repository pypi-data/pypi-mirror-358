import os
import re
import time
import logging
from smiler import smiler
from smiler.instrumenting import apktool
from smiler.instrumenting.utils import Utils
from smiler.operations import adb, binaries
from smiler.reporting.reporter import Reporter

FATAL_LOG_LINE1 = "FATAL EXCEPTION:"
FATAL_LOG_LINE2 = "Process: {}"
EXCEPTION_MESSAGE = "FATAL\sEXCEPTION:[ a-zA-Z\d\. -]+\n[0-9-:,.\w ]+\n[\d\- \.\:]+([\w'\/ \.\:\(\)\,\$\[\]\d\"\{\}#|=-]+)"

apk_dir = "/Users/ap/projects/dblt/googleplay/cmd/googleplay/twitter/adb"
en_apk = "/Users/ap/projects/dblt/googleplay/cmd/googleplay/twitter/adb/en-s.apk"
lib_apk = "/Users/ap/projects/dblt/googleplay/cmd/googleplay/twitter/adb/armeabi-s.apk"
res_apk = "/Users/ap/projects/dblt/googleplay/cmd/googleplay/twitter/adb/xxhdpi-s.apk"

def check_error(text, app):
    '''Checks is there is Fatal exception message in the log file.'''
    re_line1 = re.search(FATAL_LOG_LINE1, text)
    pattern_line2 = re.escape(FATAL_LOG_LINE2.format(app))
    re_line2 = re.search(pattern_line2, text)
    return (re_line1 is not None) & (re_line2 is not None)


def build_n_sign(unpacked_apk, package=None):
    apktool.build(unpacked_apk, "wd/test.apk")

    result_apk = "wd/test-s.apk"
    smiler.patch_align_sign("wd/test.apk", result_apk)
    return result_apk


def extract_error(text):
    search = re.search(EXCEPTION_MESSAGE, text)
    if search:
        groups = search.groups()
        if groups:
            return groups[0]


def reinstall_app(package, apks):
    try:
        smiler.uninstall(package)
    except Exception as ex:
        logging.info(ex)
    install_app(apks)


def install_app(apks):
    smiler.install_multiple(apks)


def reinstall(result_apk, package, grant_permissions=True):
    try:
        smiler.uninstall(package)
    except Exception as ex:
        print(ex)
    install(result_apk, package, grant_permissions)


def install(result_apk, package, grant_permissions=True):
    apks = [result_apk, en_apk, lib_apk, res_apk]
    smiler.install_multiple(apks)
    if grant_permissions:
        smiler.grant_storage_permission(package)


def twi_launch_login(package):
    os.system("adb logcat -c")
    smiler.request_pipe("adb shell monkey -p {} 1".format(package))
    time.sleep(5)
    logging.info("tap Log In")
    adb.tap(680, 1990, 1)


def launch(package):
    os.system("adb logcat -c")
    smiler.request_pipe("adb shell monkey -p {} 1".format(package))


def launch_log(package):
    launch(package)
    time.sleep(4)
    success = save_n_check_logcat(package)
    return success


def twi_install_launch(result_apk, package, grant_permissions=True):
    install(result_apk, package, grant_permissions)
    twi_launch_login(package)
    time.sleep(6)
    success = save_n_check_logcat(package)
    return success


def save_n_check_logcat(package):
    os.system("adb logcat -d *:E > wd/logcat.txt")
    logcat_text = binaries.read_file("wd/logcat.txt")
    is_error = check_error(logcat_text, package)
    if is_error:
        error_message = extract_error(logcat_text)
        logging.info(error_message)
    return not is_error


def twi_reinstall_launch(result_apk, package, grant_permissions=True):
    try:
        adb.delete_app_sdcard_dir(package)
        smiler.uninstall(package)
    except Exception as ex:
        print(ex)
    success = twi_install_launch(result_apk, package, grant_permissions)
    return success


def test_instrumented(result_apk, package, wd):
    reinstall(result_apk, package, grant_permissions=True)
    os.system("adb logcat -c")
    smiler.start_instrumenting(package, release_thread=True)
    raw_input("Test the app and press Enter to continue...")
    time.sleep(1)
    smiler.stop_instrumenting(package)
    smiler.get_execution_results(package, wd.ec_dir, wd.images)
    Utils.recreate_dir(wd.report)
    reporter = Reporter(package, wd.get_covered_pickles(), wd.get_ecs(), wd.images, wd.report)
    reporter.generate(html=True, xml=False)


def test_instrumented_detached_app(app, wd):
    os.system("adb logcat -c")
    reinstall_app(app.package, [wd.instrumented_apk_path]+app.supportive_apks)
    logging.info("sleeping 10...")
    time.sleep(10)
    Utils.mkdirs(wd.ec_dir)
    smiler.grant_storage_permission(wd.package)
    time.sleep(2)
    adb.save_coverage(wd.package)
    time.sleep(2)
    smiler.get_execution_results(wd.package, wd.ec_dir, wd.images)
    Utils.recreate_dir(wd.report)
    reporter = Reporter(wd.package, wd.get_covered_pickles(), wd.get_ecs(), wd.images, wd.report)
    reporter.generate(html=True, xml=False, concise=False)


def test_instrumented_detached(result_apk, package, wd):
    '''Runs simple routing without initializing the instrumentation process.'''
    os.system("adb logcat -c")
    twi_reinstall_launch(result_apk, package, grant_permissions=False)
    logging.info("sleeping 10...")
    time.sleep(10)
    Utils.mkdirs(wd.ec_dir)
    smiler.grant_storage_permission(package)
    time.sleep(2)
    adb.save_coverage(package)
    time.sleep(2)
    smiler.get_execution_results(package, wd.ec_dir, wd.images)
    Utils.recreate_dir(wd.report)
    reporter = Reporter(package, wd.get_covered_pickles(), wd.get_ecs(), wd.images, wd.report)
    reporter.generate(html=True, xml=False, concise=False)
