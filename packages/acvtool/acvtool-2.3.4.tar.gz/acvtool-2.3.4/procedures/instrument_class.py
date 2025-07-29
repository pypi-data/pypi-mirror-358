from context import smiler

import os

from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.instrumenting.core.method_instrumenter import MethodInstrumenter
from smiler.instrumenting.apkil.classnode import ClassNode
from smiler.instrumenting.core.class_instrumenter import ClassInstrumenter
from smiler.granularity import Granularity


classpath = os.path.join('tests/examples/original', 'PinnerStruct.smali')
classname = 'Lcom/uber/model/core/generated/edge/models/mobile/databindings/PinnerStruct;'
outpath = os.path.join('tests/examples/instrumented', 'PinnerStruct.smali')

mi = MethodInstrumenter(Granularity.INSTRUCTION)
ci = ClassInstrumenter(mi)

smali_class = ClassNode(classpath)

print(f"descriptor: {smali_class.methods[0].descriptor}")
print(f"len paras {len(smali_class.methods[0].paras)}")
print(f"parameters: {smali_class.methods[0].parameters}")
print(f"registers: {smali_class.methods[0].registers}")

code, cover_index, method_number, is_instrumented = ci.instrument_class(0, smali_class, 0)
print(f"{os.path.basename(classpath)}: {cover_index} probes, {method_number} methods, is_instrumented: {is_instrumented}")

Instrumenter.save_class(outpath, code)
