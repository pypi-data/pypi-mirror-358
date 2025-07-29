import logging
from context import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.operations import coverage
from smiler.reporting.reporter import Reporter
from apps.app import CurrentApp

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

app = CurrentApp()
wd = WorkingDirectory(app.package, "wd")
reporter = Reporter(app.package, wd.get_covered_pickles(), wd.images, wd.report)
reporter.generate(html=True, xml=False, concise=False)
