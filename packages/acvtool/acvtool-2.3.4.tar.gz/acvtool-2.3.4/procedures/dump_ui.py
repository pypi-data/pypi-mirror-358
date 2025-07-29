from context import smiler
from smiler import smiler

scrn_cmd = "adb shell screencap -p /sdcard/Download/screen.png"
pull_cmd = "adb pull /sdcard/Download/screen.png ./"
ui_dump_cmd = "adb shell uiautomator dump /sdcard/Download/dump.xml"
pull_ui_cmd = "adb pull /sdcard/Download/dump.xml ./"
smiler.request_pipe(scrn_cmd)
smiler.request_pipe(pull_cmd)
smiler.request_pipe(ui_dump_cmd)
smiler.request_pipe(pull_ui_cmd)
