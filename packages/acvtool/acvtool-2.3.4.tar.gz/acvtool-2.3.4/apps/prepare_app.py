import logging
from context import running
from app import CurrentApp
from procedures import prepare
from running import launcher
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting.utils import Utils

def main(app):
    wd = WorkingDirectory(app.package, "wd")

    Utils.rm_if_exists(wd.unpacked_apk)
    prepare.prepare_wd(wd, app.base_apk)
    prepare.instrument_build_sign(wd)

    launcher.test_instrumented_detached_app(app, wd)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    app = CurrentApp()
    main(app)
