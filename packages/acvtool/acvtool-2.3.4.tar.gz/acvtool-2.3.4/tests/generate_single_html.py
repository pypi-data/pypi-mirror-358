import logging
import os
import sys
from context import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.entities.wd import WorkingDirectory
from smiler.granularity import Granularity
from smiler.reporting.reporter import Reporter
from apps.app import MyFitnessPal
from smiler.serialisation.html_serialiser import HtmlSerialiser
from smiler.operations import binaries

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

app = MyFitnessPal()
wd = WorkingDirectory(app.package, "wd")

report_dir = wd.report+"_shrunk"

pkl = wd.get_shrunk_pickles()[2]
smalitree = binaries.load_smalitree(pkl)
htmlSerialiser = HtmlSerialiser(app.package, Granularity.INSTRUCTION, report_dir)
for cl in smalitree.classes:
    if cl.name == "Lcom/google/android/gms/internal/firebase-perf/zzbw;":
        htmlSerialiser.save_class(cl, os.path.join(report_dir, str(2)))
        logging.info("saved: {}".format(cl.name))
        sys.exit()



