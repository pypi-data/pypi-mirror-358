import logging
from context import smiler
from analysis import smali
from cutter import basic_block, methods
from procedures import prepare
from running import launcher
from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.instrumenting.utils import Utils
from smiler.operations import binaries, coverage


def main(smali_dir_number, is_stubbed=False):
    package = "com.twitter.android"
    wd = WorkingDirectory(package, "wd")
    dex_number = 1
    pickle = wd.get_pickles()[dex_number]
    ec = wd.get_ecs()[dex_number]
    covered_pickle = "wd/covered_{}.pickle".format(smali_dir_number)
    stubbed_pickle = "wd/stubbed_{}.pickle".format(smali_dir_number)
    short_pickle = "wd/short_{}.pickle".format(smali_dir_number)
    if is_stubbed:
        pickle = stubbed_pickle
    Utils.rm_if_exists(wd.unpacked_apk)
    prepare.prepare_wd(wd, "")
    smalitree = binaries.load_smalitree(pickle)
    bin_coverage = binaries.read_ec(ec)
    coverage.cover_tree(smalitree, bin_coverage)
    if not is_stubbed:
        binaries.save_pickle(smalitree, covered_pickle)
    smali.insns_stats(smalitree)
    stub_methods = methods.clean_not_executed_methods(smalitree)
    if not is_stubbed:
        binaries.save_pickle(smalitree, stubbed_pickle)
    basic_block.remove_blocks_from_selected_method(smalitree)
    binaries.save_pickle(smalitree, short_pickle)
    smali.insns_stats(smalitree)
    instrumenter = Instrumenter(smalitree, "", "method", package)
    instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, instrument=False)

    apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
    smiler.patch_align_sign(wd.instrumented_package_path, wd.short_apk_path)
    launcher.twi_reinstall_launch(wd.short_apk_path, package)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    main(1, is_stubbed=True)
