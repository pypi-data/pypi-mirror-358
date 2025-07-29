
from smiler import smiler
from smiler.instrumenting.utils import Utils


def build_dex(classes_dir, output_dex):
    Utils.rm_if_exists(output_dex)
    cmd = "java -jar ~/distr/smali-2.5.2.jar assemble {} -o {}".format(classes_dir, output_dex)
    smiler.request_pipe(cmd)
