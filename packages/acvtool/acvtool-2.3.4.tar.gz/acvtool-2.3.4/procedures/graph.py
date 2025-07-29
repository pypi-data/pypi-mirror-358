import os
from acvtool.cutter import shrinker
from acvtool.smiler.config import config
from acvtool.smiler.operations import binaries
from context import acvtool

import gravis
import networkx

from acvtool.smiler.entities.wd import WorkingDirectory

# parser = argparse.ArgumentParser(description="counts code entities in smali dirs")
# parser.add_argument("wd", metavar="wd", help="path to the working directory", 
#                     default=config.default_working_dir)

# args = parser.parse_args()
wd = WorkingDirectory("org.secuso.privacyfriendlydicer", config.default_working_dir)

print(wd.wd_path)
pickle_file = wd.get_covered_pickles()[1]
smalitree = binaries.load_smalitree(pickle_file)
shrinker.remove_not_executed_methods_and_classes(smalitree)


method_call_refs = {}
for cl in smalitree.classes:
    if not cl.name.startswith("Lorg/secuso/privacyfriendlydicer/"):
        continue
    for method in cl.methods:
        full_name=cl.name+"->"+method.descriptor
        if full_name not in method_call_refs:
            # if "bridge" in method.access:
            #     paint the node red
            method_call_refs[full_name] = []
        for insn in method.insns:
            if insn.covered and insn.buf.startswith("invoke-") :#and insn.covered:
                if insn.buf.startswith("invoke-virtual"):
                    print(insn.buf)
                method_call_refs[full_name].append(insn.buf.split(" ")[-1])

g = networkx.DiGraph()
g.graph['node_label_size'] = 14
g.graph['node_label_color'] = 'green'
g.add_nodes_from(method_call_refs.keys())
g.add_edges_from([(k, v) for k in method_call_refs.keys() for v in method_call_refs[k]])
root_nodes = [node for node, in_degree in g.in_degree() if in_degree == 0]
red_counter = 0
for node, in_degree in g.in_degree():
    if in_degree == 0:
        g.nodes[node].update({'color': 'red'})
        red_counter += 1
        print(node)
fig = gravis.d3(g, use_node_size_normalization=False, node_size_normalization_max=30,
            use_edge_size_normalization=True, edge_size_data_source='weight', edge_curvature=0.3,
            zoom_factor=0.6, graph_height=900)
print(f"nodes: {len(g.nodes)} edges: {len(g.edges)}")
print(f"root nodes: {red_counter}")
if os.path.exists('graph.html'):
    os.remove('graph.html')
fig.export_html('graph.html')
