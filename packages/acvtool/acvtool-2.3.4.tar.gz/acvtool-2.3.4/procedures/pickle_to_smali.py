import logging
from context import smiler
from smiler import smiler
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.operations import binaries


def save_all_pickles_to_smali(pkls):
    for p in pkls:
        pickle_to_smali(p)


def pickle_to_smali(pickle_path):
    '''    Smali goes to the folder pointed in the smalitree.foldername.
    Usually it is within "wd/apktool".
    '''
    st = binaries.load_smalitree(pickle_path)
    instrumenter = Instrumenter(st, "", "method", "")
    instrumenter.save_instrumented_smalitree_by_class(st, instrument=False)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    wd = WorkingDirectory("", "wd")
    pkls = wd.get_shrunk_pickles().values()
    save_all_pickles_to_smali(pkls)
