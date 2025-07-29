import os
from smiler.instrumenting.zipper import ZipReader
from smiler.instrumenting import baksmali

'''
This script extracts a single dex file from an APK and decodes it into smali.
$ python3.11 procedures/dex_pull.py
'''

dex_name = "classes2.dex"
apkpath = "/Users/ap/projects/dblt/apks/uber/base.apk"
output = "./wd/apktool"
dexpath = f"{output}/{dex_name}"

os.makedirs(output, exist_ok=True)

apkzip = ZipReader(apkpath)
apkzip.extract(output, [dex_name])
print(f"extracted to {dexpath}")
baksmali.decode_single_dex(dexpath, dexpath[:-4])
print(f"disassembled to {dexpath[:-4]}")

