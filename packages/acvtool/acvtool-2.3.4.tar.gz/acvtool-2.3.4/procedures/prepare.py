import logging
import os
import shutil
from smiler import smiler

from smiler.instrumenting import apktool
from smiler.instrumenting.utils import Utils


def prepare_wd(wd, apk_path):
    '''Creates required directories with smali sources if not exist.'''
    logging.info("setting the working directory up...")
    if not os.path.isdir(wd.wd_path):
        os.makedirs(wd.wd_path)
    if not os.path.isdir(wd.decompiled_apk):
        apktool.decode(apk_path, wd.decompiled_apk)
        if wd.package == "com.twitter.android":
            check_locales_config_xml(wd.decompiled_apk)
    if not os.path.isdir(wd.unpacked_apk):
        shutil.copytree(wd.decompiled_apk, wd.unpacked_apk)

def refresh_wd_no_smali(wd):
    '''We actually need app files except smali dirs.
    The smali dirs to be recover from the smalitree.'''
    logging.info("removing smali dirs")
    smali_dirs = wd.get_smali_dirs(wd.unpacked_apk)
    for sd in smali_dirs.values():
        if os.path.exists(sd):
            shutil.rmtree(sd)
    logging.info("removing build/apk dir")
    build_apk_dir = os.path.join(wd.unpacked_apk, "build/apk")
    if os.path.exists(build_apk_dir):
        shutil.rmtree(build_apk_dir)
    logging.info("refreshing AndroidManifest.xml")
    shutil.copy(os.path.join(wd.decompiled_apk, "AndroidManifest.xml"), os.path.join(wd.unpacked_apk, "AndroidManifest.xml"))


def check_locales_config_xml(unpacked_apk):
    locales_config_xml = os.path.join(unpacked_apk, "res", "xml", "locales_config.xml")
    if not os.path.exists(locales_config_xml):
        return
    os.remove(locales_config_xml)
    print("res/xml/locales_config.xml has been deleted")
    public_xml_path = os.path.join(unpacked_apk, "res", "values", "public.xml")
    with open(public_xml_path, 'r+') as f:
        lines = f.readlines()
        lines[:] = lines[:-2]
        lines.append("</resources>")
        f.seek(0)
        f.write("".join(lines))
        f.truncate()
    print("res/values/public.xml has been updated (locales_config)")
    manifest_path = os.path.join(unpacked_apk, "AndroidManifest.xml")
    with open(manifest_path, 'r+') as f:
        xml_text = f.read()
        xml_text = xml_text.replace('android:localeConfig="@xml/locales_config" ', "")
        f.seek(0)
        f.write(xml_text)
        f.truncate()
    print("AndroidManifest.xml has been updated (locales_config)")


def reinit_unpacked_apk(wd):
    remove_smali_dirs(wd.unpacked_apk)
    all_smali_dirs = Utils.get_smali_dirs(wd.unpacked_apk)
    for d in all_smali_dirs:
        Utils.rm_if_exists(d)
    dec_smali_dirs = Utils.get_smali_dirs(wd.decompiled_apk)
    for d in dec_smali_dirs:
        shutil.copytree(d, wd.unpacked_apk)
    remove_built_dexes(wd.unpacked_apk)


def remove_smali_dirs(unpacked_apk):
    smali_dirs = Utils.get_smali_dirs(unpacked_apk)
    for sd in smali_dirs:
        shutil.rmtree(sd)


def remove_built_dexes(unpacked_apk):
    os.system("rm {}/classes*".format(os.path.join(unpacked_apk, "build", "apk")))


def instrument_build_sign(wd):
    smali_dirs = Utils.get_smali_dirs(wd.unpacked_apk)
    smiler.instrument_app(wd, smali_dirs)
    apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
    smiler.patch_align_sign(wd.instrumented_package_path, wd.instrumented_apk_path)
    return wd.instrumented_apk_path

