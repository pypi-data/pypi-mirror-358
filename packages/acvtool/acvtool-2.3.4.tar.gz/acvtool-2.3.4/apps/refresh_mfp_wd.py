import logging
import os
import shutil
from context import procedures
from app import MyFitnessPal
from procedures import prepare
from smiler.entities.wd import WorkingDirectory


def copy_smali_dirs(wd):
    '''Directory structure that works for full instrumentation.
    We add 4 more dex files and move some code overthere so the 65K methods/references
    limit is respected.
    '''
    logging.info("copying smali dirs")
    smali_dirs = wd.get_smali_dirs(wd.decompiled_apk)
    print(smali_dirs)
    for sd in smali_dirs.values():
        out_sd = os.path.join(wd.unpacked_apk, os.path.basename(sd))
        logging.info("{} -> {}".format(sd, out_sd))
        shutil.copytree(sd, out_sd)
    logging.info("reorganising smali dirs")
    os.makedirs(os.path.join(wd.unpacked_apk, "smali_classes9"))
    shutil.move(os.path.join(wd.unpacked_apk, "smali_classes3/com"), os.path.join(wd.unpacked_apk, "smali_classes9"))

    os.makedirs(os.path.join(wd.unpacked_apk, "smali_classes10"))
    shutil.move(os.path.join(wd.unpacked_apk, "smali_classes5/bo"), os.path.join(wd.unpacked_apk, "smali_classes10"))
    shutil.move(os.path.join(wd.unpacked_apk, "smali_classes5/coil"), os.path.join(wd.unpacked_apk, "smali_classes10"))

    os.makedirs(os.path.join(wd.unpacked_apk, "smali_classes11/com/myfitnesspal"))
    shutil.move(os.path.join(wd.unpacked_apk, "smali_classes6/kotlin"), os.path.join(wd.unpacked_apk, "smali_classes11"))
    shutil.move(os.path.join(wd.unpacked_apk, "smali_classes6/com/myfitnesspal/intermittentfasting"), os.path.join(wd.unpacked_apk, "smali_classes11/com/myfitnesspal"))

    os.makedirs(os.path.join(wd.unpacked_apk, "smali_classes12/com"))
    shutil.move(os.path.join(wd.unpacked_apk, "smali_classes7/com/google"), os.path.join(wd.unpacked_apk, "smali_classes12/com/"))
    shutil.move(os.path.join(wd.unpacked_apk, "smali_classes7/com/inmobi"), os.path.join(wd.unpacked_apk, "smali_classes12/com/"))

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    app = MyFitnessPal()
    wd = WorkingDirectory(app.package, "wd")
    prepare.refresh_wd_no_smali(wd)
    copy_smali_dirs(wd)