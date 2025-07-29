from context import smiler
from smiler.entities.wd import WorkingDirectory

package = "com.twitter.android"
wd_path = "wd"

wd = WorkingDirectory(package, wd_path)

print(wd.decompiled_apk)