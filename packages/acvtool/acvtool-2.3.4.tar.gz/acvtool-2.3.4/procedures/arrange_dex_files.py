from context import smiler

import os
from smiler.instrumenting.apkil.smalitree import SmaliTree
from smiler.smiler import arrange_acv_dexes
from smiler.instrumenting.zipper import ZipReader

apkpath = "/Users/ap/projects/dblt/apks/uber/base.apk"
unpacked_apk = "/Users/ap/acvtool/acvtool_working_dir/apktool"
acv_classes_dir_name = "classes33"

acvtree = SmaliTree(1, os.path.join(unpacked_apk, acv_classes_dir_name))
print("classes: {}".format(len(acvtree.classes)))
method_counter = sum([len(cl.methods) for cl in acvtree.classes])
print("methods: {}".format(method_counter))
fields = sum([len(cl.fields) for cl in acvtree.classes])
print("fields: {}".format(fields))
annotations = sum([len(cl.annotations) for cl in acvtree.classes])
print("annotations: {}".format(annotations))
insns = sum([sum([len(m.insns) for m in cl.methods]) for cl in acvtree.classes])
print("instructions: {}".format(insns))

apkfile = ZipReader(apkpath, unpacked_apk)
arrange_acv_dexes(acvtree, apkfile)