
from context import smiler
import logging
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting.utils import Utils
from smiler.operations import adb
from smiler.reporting.reporter import Reporter


def main():
    wd = WorkingDirectory("com.twitter.android", "wd")
    reporter = Reporter(wd.package, wd.get_covered_pickles(), wd.images, wd.report)
    reporter.generate(html=True, xml=False, concise=False)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    main()
