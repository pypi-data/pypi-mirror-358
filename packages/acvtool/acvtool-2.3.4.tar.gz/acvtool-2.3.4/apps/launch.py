import logging
from app import CurrentApp
from context import running
from running import launcher
from smiler.operations import adb

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
app = CurrentApp()
adb.launch_app(app.package)