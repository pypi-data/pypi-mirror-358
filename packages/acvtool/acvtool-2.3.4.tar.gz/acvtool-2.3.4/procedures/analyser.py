''' Counts method number in a smali dir '''
from context import smiler

import argparse
import yaml
import os
import sys

from logging import config as logging_config
from smiler.config import config

from smiler import smiler
from smiler.instrumenting.apkil.smalitree import SmaliTree
from smiler.instrumenting.utils import Utils

parser = argparse.ArgumentParser(description="counts code entities in smali dirs")
parser.add_argument("unpacked_apk", metavar="unpacked_apk", help="path to the unpacked apk")
parser.add_argument("-d", "--dex", metavar="dex", help="corresponding smali dir to count methods only in a single dex")
parser.add_argument("-k", "--klass", metavar="klass", help="give stats per method of a single class")


args = parser.parse_args()
print(args)
unpacked_apk = args.unpacked_apk # acvcut.wd_path
dex = args.dex
klass = args.klass

def setup_logging():
    with open(config.logging_yaml) as f:
        logging_config.dictConfig(yaml.safe_load(f.read()))

# python procedures/analyser.py wd/apktool -d smali_classes3 -k "Ltool/acv/AcvReporter1;"
def print_class_stats(unpacked_apk, dex, klass):
    tree = SmaliTree(1, os.path.join(unpacked_apk, dex))
    cl = (cl for cl in tree.classes if cl.name == klass).next()
    print("methods: {}".format(len(cl.methods)))
    print("fields: {}".format(len(cl.fields)))
    print("annotations: {}".format(len(cl.annotations)))
    for m in cl.methods:
        print("{}: {} insns".format(m.name, len(m.insns)))

def main():
    if args.klass:
        print_class_stats(unpacked_apk, dex, klass)
        return
    smali_dirs = []
    smali_dirs = Utils.get_smali_dirs(unpacked_apk)
    if dex:
        smali_dirs = [os.path.join(unpacked_apk, dex)]
    for id, sd in enumerate(smali_dirs, 1):
        smalitree = SmaliTree(id, sd)
        print("classes: {}".format(len(smalitree.classes)))
        method_counter = sum([len(cl.methods) for cl in smalitree.classes])
        print("methods: {}".format(method_counter))
        fields = sum([len(cl.fields) for cl in smalitree.classes])
        print("fields: {}".format(fields))
        annotations = sum([len(cl.annotations) for cl in smalitree.classes])
        print("annotations: {}".format(annotations))
        insns = sum([sum([len(m.insns) for m in cl.methods]) for cl in smalitree.classes])
        print("instructions: {}".format(insns))
    

if __name__ == "__main__":
    setup_logging()
    main()
