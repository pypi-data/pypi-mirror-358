from context import smiler
import os
import logging
from analysis import smali
from analysis.smali import StatsCounter
from cutter import basic_block, invokes, methods
from procedures.debugging import twi_bot
from running import launcher
from smiler import smiler
from procedures import prepare, pull_coverage
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.instrumenting.utils import Utils
from smiler.operations import binaries, coverage

orig_invoke_list = set()
result_invoke_list = set()

def shrink_tree(smalitree, stub_dir):
    methods.clean_not_executed_methods(smalitree)
    basic_block.remove_blocks_from_selected_method(smalitree)
    # orig_invokes = invokes.get_invoke_direct_methods(smalitree)
    # stub_methods = methods.clean_not_executed_methods(smalitree)
    # stub_output_path = os.path.join(stub_dir, "{}.txt".format(smalitree.Id))
    # binaries.save_list(stub_output_path, stub_methods)
    #methods.remove_static(smalitree)
    # result_invokes = invokes.get_invoke_direct_methods(smalitree)
    # to_remove_invokes = orig_invokes - result_invokes
    # invokes.remove_methods_by_invokes(smalitree, to_remove_invokes)

def debloat_app_code(wd):
    pickle_files = wd.get_covered_pickles()
    ecs = wd.get_ecs()
    counter = StatsCounter()
    for dex_number in range(1, len(pickle_files)+1):
        logging.info("processing dex: {}".format(dex_number))
        pickle_path = pickle_files[dex_number]
        smalitree = binaries.load_smalitree(pickle_path)
        bin_coverage = binaries.read_multiple_ec_per_tree(ecs[dex_number])
        coverage.cover_tree(smalitree, bin_coverage)
        binaries.save_pickle(smalitree, pickle_path)
        counter.put_original(smalitree)
        shrink_tree(smalitree, wd.stub_dir)
        counter.put_shrunk(smalitree)
        instrumenter = Instrumenter(smalitree, "", "method", wd.package)
        instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, instrument=False)
        #builder.build_dex(smaliclasses_dirs[dex_number], output_dexs[dex_number])
    counter.log_total()


def main():
    package = "com.twitter.android"
    wd = WorkingDirectory(package, "wd")
    Utils.recreate_dir(wd.ec_dir)
    pull_coverage.main()
    debloat_app_code(wd)

    apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
    smiler.patch_align_sign(wd.instrumented_package_path, wd.short_apk_path)
    logging.info("size: {} MB".format(int(os.path.getsize(wd.short_apk_path))/1000000))
    launcher.twi_reinstall_launch(wd.short_apk_path, package, grant_permissions=False)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    main()
    twi_bot.routine()
