import logging
from context import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.operations import binaries, coverage

def main():
    package = "com.twitter.android"
    wd = WorkingDirectory(package, "wd")
    ecs = wd.get_ecs()
    dex=3
    bin_coverage = binaries.read_multiple_ec_per_tree(ecs[dex])
    prob_cov = coverage.calculate(bin_coverage)
    logging.info("probes: {} out of {} total; {}% coverage".format(prob_cov.covered, prob_cov.total, prob_cov.coverage()))


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    main()
    