import logging
from context import running
from app import CurrentApp
from running import launcher
from smiler import smiler
from smiler.entities.wd import WorkingDirectory

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
app = CurrentApp()
wd = WorkingDirectory(app.package, "wd")
launcher.reinstall_app(app.package, [app.base_apk]+app.supportive_apks)
