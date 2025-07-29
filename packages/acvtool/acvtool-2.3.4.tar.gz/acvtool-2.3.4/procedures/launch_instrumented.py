import logging
from context import apps
from apps.app import MyFitnessPal
from running import launcher
from smiler.entities.wd import WorkingDirectory

'''Launch for testing.'''

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

app = MyFitnessPal()
wd = WorkingDirectory(app.package, "wd")
launcher.reinstall_app(wd.package, [wd.instrumented_apk_path]+app.supportive_apks)
launcher.launch(app.package)
