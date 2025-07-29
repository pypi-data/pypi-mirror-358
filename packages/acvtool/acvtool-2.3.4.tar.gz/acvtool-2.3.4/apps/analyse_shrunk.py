import logging
import os
import sys
from context import smiler
from running import launcher
from app import CurrentApp
from smiler.entities.wd import WorkingDirectory
from smiler.instrumenting import apktool
from smiler.instrumenting.smali_instrumenter import Instrumenter
from smiler.operations import binaries
from smiler import smiler
from analysis.smali import StatsCounter

'''This sript removes not used classes taking into account 
class hierarchy and interfaces.

We want to delete now (not used):
- classes
- interfaces
- stubbed methods
- fields

Class hierarchy analysis (CHA) solves these issues:
- classes may reference deleted superclasses
- classes may implement deleted interfaces

Euristics:
- probably all annotations get deleted whe R8 is used
'''

def remove_odd_methods_from_odd_classes(strees):
    for smalitree in strees: 
        for cl in smalitree.classes:
            if "abstract" not in cl.access:
                for m in cl.methods[:]:
                    if not m.called:
                        cl.methods.remove(m)
            #if cl.mtds_coverage() == 0:
                # for m in cl.methods[:]:
                #     cl.methods.remove(m)
                # if len(cl.fields) == 0 and "abstract" not in cl.access:
                #     smalitree.classes.remove(cl)


def remove_odd_classes(strees):
    cut_classes = []
    for smalitree in strees:
        for cl in smalitree.classes[:]:
                if not hasattr(cl, 'keep'):
                    cut_classes.append(cl.name)
                    #smalitree.classes.remove(cl)
                    # if any(not m.called for m in cl.methods):
                    #     for m in cl.methods[:]:
                    #         if not m.called and 'abstract' not in m.access:
                    #             cl.methods.remove(m)
    return cut_classes


def remove_odd_fields(strees):
    counter = 0
    for smalitree in strees:
        for cl in smalitree.classes:
            for f in cl.fields[:]:
                # TODO: refactor when new is used (hasattr used for compatibility, to not reinstrument the testing apps)
                if not hasattr(f, "referred"):# and not getattr(f, "referred"):
                    cl.fields.remove(f)
                    counter += 1
    logging.info("{} fields removed".format(counter))


def map_class_n_fields_names(smalitrees):
    class_name_refs = {}
    fieldname_to_field_map = {}
    for st in smalitrees:
        for cl in st.classes:
            class_name_refs[cl.name] = cl
            for f in cl.fields:
                name = "{}->{}:{}".format(cl.name, f.name, f.descriptor)
                fieldname_to_field_map[name] = f
    return class_name_refs, fieldname_to_field_map

def get_referred_fields(strees):
    fields_refs = set()
    for st in strees:
        for cl in st.classes:
            for m in cl.methods:
                if m.called:
                    for insn in m.insns:
                        if insn.buf.startswith(("sget","sput","iget","iput")):
                            # sstaticop vAA, field@BBBB
                            # iinstanceop vA, vB, field@CCCC
                            # iput p2, p0, Landroidx/constraintlayout/solver/SolverVariable;->strength:I
                            fields_refs.add(insn.buf.split()[-1])
    return fields_refs

def add_reflected_fields(fields_referred):
    # referred possibly reflection
    additional = [
        "Lcom/google/android/gms/internal/firebase-perf/zzbh;->zzid:Lcom/google/android/gms/internal/firebase-perf/zzbw;",
        "Lcom/google/android/gms/internal/firebase-perf/zzbh;->zzie:Lcom/google/android/gms/internal/firebase-perf/zzcu;",
        "Lcom/google/android/gms/internal/firebase-perf/zzbh;->zzif:I",
        "Lcom/google/android/gms/internal/firebase-perf/zzcp;->zzll:Z",
    ]
    for a in additional:
        fields_referred.add(a)

def get_referenced_class_names(strees):
    '''Extracting references from:
        - class has a called method means someone references it
        - method argument type (m.paras) of called method
        - instruction calls such as invoke
        - interfaces

        method to be run on shrunk code (no extra ref insns)
    '''

    class_names = set()
    for st in strees:
        for cl in st.classes:
            if any(m.called for m in cl.methods):
                class_names.add(cl.name)
            else:
                continue
            for m in cl.methods:
                if len(m.paras)>0 and any(not p.basic for p in m.paras):
                    # extract method argument type reference
                    for p in m.paras:
                        if not p.basic:
                            class_names.add(p.type_)
                if m.called:
                    for insn in m.insns:
                        if insn.buf.startswith(("const-class","check-cast","instance-of","new-instance","new-array","filled-new-array")):
                            # This insns refer to a class (type)
                            # const-class vAA, type@BBBB
                            # check-cast vAA, type@BBBB
                            # instance-of vA, vB, type@CCCC
                            # new-instance vAA, type@BBBB
                            # new-array vA, vB, type@CCCC
                            # filled-new-array {vC, vD, vE, vF, vG}, type@BBBB
                            # filled-new-array/range {vCCCC .. vNNNN}, type@BBBB
                            # Examples:
                            # const-class v2, Landroid/widget/AutoCompleteTextView;
                            # check-cast v0, [Ljava/util/Set;
                            # instance-of v0, p0, Landroid/view/ViewGroup;
                            ref = insn.buf.split()[-1]
                            if ref[0] == '[':
                                i = 1
                                while i < len(ref) and ref[i] == '[':
                                    i += 1
                                ref = ref[i:]
                            class_names.add(ref)

    return class_names


def load_shrunk_smalitrees(wd):
    strees = []
    shrunk_pickles = wd.get_shrunk_pickles()
    for dn in range(1, len(shrunk_pickles)+1):
        pkl = os.path.join(wd.shrunk_pickle_dir, "{}_{}.pickle".format(wd.package, dn))
        smalitree = binaries.load_smalitree(pkl)
        strees.append(smalitree)
    return strees


def mark_tree_referenced_classes(classname_to_classnode_map, cl_names_referred):
    for cn in cl_names_referred:
        if cn in classname_to_classnode_map:
            classname_to_classnode_map[cn].keep = True
        else:
            logging.info("odd class name: {}".format(cn))

def remove_implements(strees, cut_classes):
    implements_removed = 0
    for smalitree in strees:
            for cl in smalitree.classes:
                if len(cl.implements) > 0:
                    for im in cl.implements[:]:
                        if im in cut_classes:
                            cl.implements.remove(im)
                            implements_removed += 1
    logging.info("implements removed: {}".format(implements_removed))

def save_smali(strees):
    for smalitree in strees:
        instrumenter = Instrumenter(smalitree, "", "method", "")
        instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, instrument=False)


def get_class_tree_map(strees):
    class_map = {}
    for st in strees:
        for cl in st.classes:
            class_map[cl.name] = cl
    return class_map

def fix_class_hierarchy(strees, original_class_hierarchy, odd_superclasses, classes_left):
    '''When a class references to a removed superclass, we look through 
    in the old hierarchy and in the odd_superclasses list (those classes were not in the app).'''
    super_substitution = set()
    for cl in classes_left.values():
        if cl.super_name not in odd_superclasses \
            and cl.super_name not in classes_left:
            supersuper = original_class_hierarchy[cl.super_name]
            while supersuper not in classes_left and supersuper not in odd_superclasses:
                supersuper = original_class_hierarchy[supersuper]
            super_substitution.add("{}:{}->{}".format(cl.name, cl.super_name, supersuper))
            cl.super_name = supersuper
    binaries.save_list("wd/txt/super_substitution.txt", super_substitution)


def get_odd_superclasses(classname_to_classnode_map):
    '''Returns super class names that are not referenced. '''
    odd_superclasses = set()
    for name, cl in classname_to_classnode_map.items():
        if cl.super_name not in classname_to_classnode_map:
            logging.info("odd superclass: {} from {}".format(cl.super_name, name))
            odd_superclasses.add(cl.super_name)
    return odd_superclasses

def add_class_names_from_referred_field_types(cl_names_referred, fields_referenced, classname_to_classnode_map):
    for f in fields_referenced:
        cl1, field = f.split('->')
        field_name, cl2 = field.split(':')
        cl_names_referred.add(cl1)
        cl_names_referred.add(cl2)

def add_method_params_n_return_types(cl_names_referred, strees):
    types = set()
    for st in strees:
        for cl in st.classes:
            for m in cl.methods:
                if m.called:
                    types.add(m.ret.type_)
                    for p in m.paras:
                        types.add(p.type_)
    binaries.save_list("wd/txt/method_desc_types.txt", types)
    cl_names_referred.update(types)
                    
def mark_tree_referred_fields(field_ref_to_fieldnode_map, fields_referred):
    '''Runs over fields referred to in the methods to mark them in the smalitree.'''
    counter = 0
    true_referred = []
    for fn in fields_referred:
        if fn in field_ref_to_fieldnode_map:
            field_ref_to_fieldnode_map[fn].referred = True
            counter += 1
            true_referred.append(fn)
        else:
            # this field not in the smali code, but somewhere else (lib or Android side)
            logging.warn("odd field refferenced: {}".format(fn))
    logging.info("fields marked as referred: {}".format(counter))
    binaries.save_list("wd/txt/fields_referred_true.txt", true_referred)


def process_code(wd):
    strees = load_shrunk_smalitrees(wd)
    cl_names_referred = get_referenced_class_names(strees)
    fields_referred = get_referred_fields(strees)
    #add_reflected_fields(fields_referred)
    binaries.save_list("wd/txt/fields_referred.txt", fields_referred)
    logging.info("classes: {}".format(len(cl_names_referred)))
    logging.info("fields: {}".format(len(fields_referred)))
    classname_map, fieldname_map = map_class_n_fields_names(strees)
    binaries.save_list("wd/txt/fields_map.txt", fieldname_map)
    add_class_names_from_referred_field_types(cl_names_referred, fields_referred, classname_map)
    add_method_params_n_return_types(cl_names_referred, strees)
    odd_superclasses = get_odd_superclasses(classname_map)
    # mark_tree_referenced_classes(classname_to_classnode_map, cl_names_referred)
    mark_tree_referred_fields(fieldname_map, fields_referred)
    counter = StatsCounter()
    counter.put_original_trees(strees)
    cut_classes = remove_odd_classes(strees)
    # remove_implements(strees, cut_classes)
    binaries.save_list("wd/txt/cut_classes.txt", cut_classes)
    remove_odd_fields(strees)
    classname_map, fieldname_map = map_class_n_fields_names(strees)
    # fix_class_hierarchy(strees, original_class_hierarchy, odd_superclasses, classname_to_classnode_map)
    counter.put_shrunk_trees(strees)
    counter.log_total()
    #logging.info("removed classes: {}".format(len(cut_classes)))
    # clean_references
    save_smali(strees)


# to depricate
def show_not_covered_classes(wd):
    pkl = os.path.join(wd.shrunk_pickle_dir, "{}_{}.pickle".format(wd.package, 1))
    st = binaries.load_smalitree(pkl)
    for cl in st.classes:
        if cl.is_coverable() and not any(m.called for m in cl.methods):
            logging.info(cl.name)


def remove_methods(wd):
    strees = load_shrunk_smalitrees(wd)
    counter = StatsCounter()
    counter.put_original_trees(strees)
    remove_odd_methods_from_odd_classes(strees)
    counter.put_shrunk_trees(strees)
    counter.log_total()
    binaries.save_pickle(strees[0], os.path.join("wd/covered_pickles", "{}_{}.pickle".format(wd.package, 1)))
    save_smali(strees)


def main():
    app = CurrentApp()
    wd = WorkingDirectory(app.package, "wd")
    #process_code(wd)
    show_not_covered_classes(wd)
    remove_methods(wd)
    apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
    smiler.patch_align_sign(wd.instrumented_package_path, wd.cha_apk_path)
    launcher.reinstall_app(app.package, [wd.cha_apk_path]+app.supportive_apks)
    launcher.launch_log(app.package)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s%(levelname)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
    logging.addLevelName(logging.WARNING, " \033[91mW\033[0m")
    logging.addLevelName(logging.INFO, "")
    main()
