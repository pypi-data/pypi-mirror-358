import logging
from context import smiler
from apps.app import CurrentApp
from smiler.entities.wd import WorkingDirectory
from smiler.operations import binaries, coverage


def calculate_total_coverage_per_dex(wd):
    ecs = wd.get_ecs()
    total = coverage.ProbesCoverage()
    for k in ecs.keys():
        bin_coverage = binaries.read_multiple_ec_per_tree(ecs[k])
        probes_cov = coverage.calculate(bin_coverage)
        total.covered += probes_cov.covered
        total.total += probes_cov.total
        logging.info("ec: {}, probes: {} out of {} total; {}% coverage".format(k, probes_cov.covered, probes_cov.total, probes_cov.coverage()))
    logging.info("total {} out of {}; {}% coverage".format(total.covered, total.total, total.coverage()))


def progresssive_coverage_per_dex(wd):
    ecs = wd.get_ecs_by_ts_by_dex()
    for ts in sorted(ecs.keys()):
        covs = []
        for dn in ecs[ts].keys():
            bin_cov = binaries.read_ec(ecs[ts][dn])
            probes_cov = coverage.calculate(bin_cov)
            cov_val = 100*float(probes_cov.covered)/probes_cov.total
            covs.append("{}: {}%".format(dn, cov_val))
        covs_line = "\t".join(covs)
        logging.info("ts {}: {}".format(ts, covs_line))


def main():
    app = CurrentApp()
    wd = WorkingDirectory(app.package, "wd")
    #calculate_total_coverage_per_dex(wd)
    progresssive_coverage_per_dex(wd)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    main()
    