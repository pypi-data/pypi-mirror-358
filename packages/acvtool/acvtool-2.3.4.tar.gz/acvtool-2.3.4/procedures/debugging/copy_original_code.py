import logging
import os
from context import smiler
from context import apps

from smiler import smiler
from apps.app import CurrentApp
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting.utils import Utils


def copy_original_code(wd):
    dexs = wd.get_smali_dirs(wd.unpacked_apk)
    for dex_number in dexs.keys():
        dex_path = dexs[dex_number]
        orig_dex_path = os.path.join(wd.decompiled_apk, os.path.basename(dex_path))
        Utils.rm_if_exists(dex_path)
        if os.path.exists(orig_dex_path):
            Utils.copytree(orig_dex_path, dex_path)


def main(app):
    wd = WorkingDirectory(app.package, "wd")
    copy_original_code(wd)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    app = CurrentApp()
    main(app)