import logging
import os
import sys
import time
from context import running
from running import launcher
from smiler.entities.wd import WorkingDirectory
from smiler.operations import adb
'''
coordinates
> reinstall_launch
Click to Type username
/dev/input/event2: EV_ABS       ABS_MT_POSITION_X    0000010f 271
/dev/input/event2: EV_ABS       ABS_MT_POSITION_Y    000002b9 697
Type acvcut2
Click next
/dev/input/event2: EV_ABS       ABS_MT_POSITION_X    000003ad 941
/dev/input/event2: EV_ABS       ABS_MT_POSITION_Y    0000048c 1164
Click password field
/dev/input/event2: EV_ABS       ABS_MT_POSITION_X    000000fe 254
/dev/input/event2: EV_ABS       ABS_MT_POSITION_Y    00000293 659
> input text password
Click login
/dev/input/event2: EV_ABS       ABS_MT_POSITION_X    0000038b 907
/dev/input/event2: EV_ABS       ABS_MT_POSITION_Y    0000047d 1149
Click search tab
/dev/input/event2: EV_ABS       ABS_MT_POSITION_X    00000139 313
/dev/input/event2: EV_ABS       ABS_MT_POSITION_Y    000007a0 1952
Click home tab
/dev/input/event2: EV_ABS       ABS_MT_POSITION_X    00000073 115
/dev/input/event2: EV_ABS       ABS_MT_POSITION_Y    000007b3 1971
'''

def main():
    package = "com.twitter.android"

    wd = WorkingDirectory(package, "wd")
    logging.info("delete sdcard app path")
    adb.delete_app_sdcard_dir(package)
    launcher.reinstall(wd.instrumented_apk_path, package, grant_permissions=False)
    launcher.twi_launch_login(package)
    login()
    tap_cycle(20)

    
def login():
    time.sleep(3)
    logging.info("click username field")
    adb.tap(271, 697, 0.5)
    logging.info("type username")
    adb.input_text("acvcut2", 1)
    logging.info("click next")
    adb.tap(907, 1149, 2)
    logging.info("tap password field")
    adb.tap(271, 697, 0.5)
    logging.info("type password")
    adb.input_text("yCt5Wfso", 2)
    logging.info("click login")
    adb.tap(907, 1149, 3)


def routine():
    login()
    logging.info("done")


def tap_home(delay=0):
    logging.info("tap home tab")
    adb.tap(115, 1971, delay)


def tap_cycle(n=10):
    for i in range(1, n):
        logging.info("testing round {}".format(i))
        tap_tabs()


def tap_tabs(delay=0):
    tap_home(delay)
    logging.info("tap search tab btn")
    adb.tap(313, 1952, delay)
    logging.info("tap voice tab btn")
    adb.tap(500, 1952, delay)
    logging.info("tap notifications tab btn")
    adb.tap(650, 1952, delay)
    logging.info("tap messages tab btn")
    adb.tap(900, 1952, delay)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    main()
