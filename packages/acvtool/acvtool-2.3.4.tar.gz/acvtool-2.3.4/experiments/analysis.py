import logging
import os
import sys
from context import smiler
from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.operations import binaries, coverage
import pandas as pd

def calculate_cov_multiple(ecs):
    res_cov = coverage.ProbesCoverage()
    for ec in ecs:
        bin_cov = binaries.read_ec(ec)
        prob_cov = coverage.calculate(bin_cov)
        res_cov.covered += prob_cov.covered
        res_cov.total += prob_cov.total
    return res_cov


def main():
    package = "com.twitter.android"
    wd = WorkingDirectory(package, "wd")
    ecs = wd.get_ecs_by_ts()
    sorted_ecs_keys = sorted(ecs.keys())
    print(len(sorted_ecs_keys))
    i = 3 # number of experimental runs
    s =  1
    df = pd.DataFrame()
    d = {}
    ecs_v_index = 0
    while i > 0:
        j = 30 # number of coverage measurements per run
        cov_values = []
        while j > 0:
            ts = sorted_ecs_keys[ecs_v_index]
            logging.info("{}. reading ecs: {}. {} ecs files".format(s, ts, len(ecs[ts])))
            cov = calculate_cov_multiple(ecs[ts])
            print("covered: {}, total: {}, cov: {}".format(cov.covered, cov.total, cov.coverage()))
            cov_values.append(cov.coverage())
            j -= 1
            ecs_v_index += 1
        d["run{}".format(s)] = cov_values
        i -= 1
        s += 1
    df = pd.DataFrame(d)
    df.to_csv(os.path.join(wd.wd_path, "cov_df.csv"))


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    main()