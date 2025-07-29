import os
import shutil
from smiler.instrumenting.apkil.smalitree import SmaliTree
from smiler.instrumenting.utils import Utils


def move_classes_to_new_dex(classes_to_move, original_dex_number, unpacked_app_dir):
    next_dex_number = original_dex_number + 2
    new_dex_path = os.path.join(unpacked_app_dir, "smali_classes{}".format(next_dex_number))
    new_acv_dir = os.path.join(new_dex_path, "tool", "acv")
    if not os.path.exists(new_acv_dir):
        os.makedirs(new_acv_dir)
    for cl in classes_to_move:
        shutil.move(cl, new_acv_dir)
        print("{} moved to new the dex directory {}".format(os.path.basename(cl), os.path.basename(new_acv_dir)))

unpacked_apk = "wd/apktool/com.twitter.android"
acv_classes_dir = os.path.join(unpacked_apk, "smali_classes13")
input_smali_dirs = Utils.get_smali_dirs(unpacked_apk)

code_dir_number = 12
acv_tree = SmaliTree(code_dir_number+1, acv_classes_dir)
# class_number = len(acv_tree.classes)
fields_number =  sum([len(cl.fields) for cl in acv_tree.classes])
# methods_number =  sum([len(cl.methods) for cl in acv_tree.classes])
if fields_number > 65400: #65535
    acv_reporter_classes = [cl for cl in acv_tree.classes if cl.name.startswith("Ltool/acv/AcvReporter")]
    fields_number_counter = 0
    classes_to_move = []
    for i, cl in enumerate(acv_reporter_classes):
        fields_number_counter += len(cl.fields)
        if fields_number_counter > 65000:
            classes_to_move.append(cl.file_path)
    if classes_to_move:
        move_classes_to_new_dex(classes_to_move, len(input_smali_dirs), os.path.dirname(input_smali_dirs[0]))
