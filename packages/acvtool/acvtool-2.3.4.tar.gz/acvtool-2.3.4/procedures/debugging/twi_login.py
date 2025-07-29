import logging
from context import running
from running import launcher
from smiler.entities.wd import WorkingDirectory
import os
import time

from smiler.operations import adb

def click_twi_home():
    if d(description="Home", className="android.widget.LinearLayout").exists:
        d(description="Home", className="android.widget.LinearLayout").click()
        print("Home")
    else:
        d(description="Home. New items", className="android.widget.LinearLayout").click()
        print("Home. New items")

def routine():
    # d.screen.on()
    # os.system("adb shell monkey -p com.twitter.android 1")
    # time.sleep(2)
    #os.system("adb shell input tap 680 1990")
    #time.sleep(2)
    d(resourceId="com.twitter.android:id/text_field").click()
    d(resourceId="com.twitter.android:id/text_field").set_text("acvcut2")
    time.sleep(2)
    #class="android.view.View"
    #index="0", text="Next", class="android.view.View", enabled="true", visible-to-user="true" bounds="[917,1901][1003,1957]"
    d(index="0", text="Next", className="android.view.View", enabled="true").click()
    d(resourceId="com.twitter.android:id/password_field").set_text("yCt5Wfso")
    time.sleep(2)
    d(index="0", text="Log in", className="android.view.View").click()
    os.system("adb shell input tap 680 1990")
    #click_twi_home()

def main():
    package = "com.twitter.android"

    wd = WorkingDirectory(package, "wd")
    #launcher.reinstall_launch(wd.short_apk_path, package, grant_permissions=False)
    logging.info("delete sdcard app path")
    adb.delete_app_sdcard_dir(package)
    #adb.clear_app_data(package)
    logging.info("sleep 2")
    time.sleep(2)
    logging.info("launch")
    launcher.twi_launch_login(package)
    logging.info("sleep 2")
    time.sleep(2)
    logging.info("click home")
    os.system("adb shell input tap 50 1990")
    logging.info("sleep 2")
    time.sleep(2)
    logging.info("click home")
    os.system("adb shell input tap 50 1990")
    logging.info("click home")
    os.system("adb shell input tap 50 1990")
    
    
    #routine()
    #launcher.save_n_check_logcat(package)
# blueline:/ $ sendevent /dev/input/event2 3 57 0
# blueline:/ $ sendevent /dev/input/event2 3 53 300
# blueline:/ $ sendevent /dev/input/event2 3 54 400
# blueline:/ $ sendevent /dev/input/event2 3 48 5
# blueline:/ $ sendevent /dev/input/event2 3 58 50
# blueline:/ $ sendevent /dev/input/event2 0 2 0
# blueline:/ $ sendevent /dev/input/event2 0 0 0

# ABS_MT_TRACKING_ID (57) - ID of the touch (important for multi-touch reports)
# ABS_MT_POSITION_X (53) - x coordinate of the touch
# ABS_MT_POSITION_Y (54) - y coordinate of the touch
# ABS_MT_TOUCH_MAJOR (48) - basically width of your finger tip in pixels
# ABS_MT_PRESSURE (58) - pressure of the touch
# SYN_MT_REPORT (2) - end of separate touch data
# SYN_REPORT (0) - end of report

# /dev/input/event2: EV_KEY       BTN_TOUCH            DOWN
# /dev/input/event2: EV_ABS       ABS_MT_TRACKING_ID   0000016d
# /dev/input/event2: EV_ABS       ABS_MT_POSITION_X    000001e0
# /dev/input/event2: EV_ABS       ABS_MT_POSITION_Y    000004fd
# /dev/input/event2: EV_ABS       ABS_MT_TOUCH_MAJOR   00000008
# /dev/input/event2: EV_ABS       ABS_MT_TOUCH_MINOR   00000008
# /dev/input/event2: EV_ABS       ABS_MT_PRESSURE      00000029
# /dev/input/event2: EV_SYN       SYN_REPORT           00000000
# /dev/input/event2: EV_ABS       ABS_MT_PRESSURE      00000000
# /dev/input/event2: EV_ABS       ABS_MT_TRACKING_ID   ffffffff
# /dev/input/event2: EV_KEY       BTN_TOUCH            UP
# /dev/input/event2: EV_SYN       SYN_REPORT           00000000


def adb_sendevent(a,b,c):
    cmd = "adb shell sendevent /dev/input/event2 {} {} {}".format(a,b,c)
    os.system(cmd)



def sendevent():
    adb_sendevent(3,57,0)
    adb_sendevent(3,53,200)
    adb_sendevent(3,54,200)
    adb_sendevent(3,48,5)
    adb_sendevent(3,58,50) # pressure
    adb_sendevent(0,2,0)
    adb_sendevent(0,0,0)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    #main()
    sendevent()