import os
import gravis
import networkx
from acvtool.smiler.config import config
from acvtool.smiler.operations import binaries
from acvtool.smiler.entities.wd import WorkingDirectory
import math


# requirements to add to setup.py
#     'gravis': '0.1.0',
#     'networkx': '3.4.2',

package = "org.regular.random"
graph_output_path = "full-graph.html"
filter_class = ""
#filter_class="Lorg/regular/random/PossiblePoetry"

wd = WorkingDirectory(package, config.default_working_dir)
print(wd.wd_path)

pickle_file = wd.get_pickles()[1]
smalitree = binaries.load_smalitree(pickle_file)

method_call_refs = {}
for cl in smalitree.classes:
    if not cl.name.startswith(filter_class):
        continue
    for method in cl.methods:
        full_name = cl.name + "->" + method.descriptor
        if full_name not in method_call_refs:
            method_call_refs[full_name] = []
        for insn in method.insns:
            if insn.buf.startswith("invoke-"):
                method_call_refs[full_name].append(insn.buf.split(" ")[-1])

# Organize nodes that have cl.super_name == Landroid/app/Activity; into a square

# activity_nodes = []
# for cl in smalitree.classes:
#     if cl.super_name == "Landroid/app/Activity;":
#         for method in cl.methods:
#             full_name = cl.name + "->" + method.descriptor
#             if full_name in g.nodes:
#                 activity_nodes.append(full_name)

# # Arrange these nodes in a square by assigning 'x' and 'y' attributes

# n = len(activity_nodes)
# if n > 0:
#     side = math.ceil(math.sqrt(n))
#     for idx, node in enumerate(activity_nodes):
#         row = idx // side
#         col = idx % side
#         g.nodes[node]['x'] = col * 100
#         g.nodes[node]['y'] = row * 100
#         g.nodes[node]['color'] = 'orange'  # Optionally highlight these nodes

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
    # Mark leaf nodes (out_degree == 0) as blue
    if g.out_degree(node) == 0:
        g.nodes[node].update({'color': 'blue'})
        # Arrange nodes whose class is an Activity into a square grid
        activity_nodes = []
        for cl in smalitree.classes:
            if cl.super_name == "Landroid/app/Activity;":
                for method in cl.methods:
                    full_name = cl.name + "->" + method.descriptor
                    if full_name in g.nodes:
                        activity_nodes.append(full_name)

        n = len(activity_nodes)
        if n > 0:
            side = math.ceil(math.sqrt(n))
            for idx, node in enumerate(activity_nodes):
                row = idx // side
                col = idx % side
                g.nodes[node]['x'] = col * 100
                g.nodes[node]['y'] = row * 100
                g.nodes[node]['color'] = 'orange'

fig = gravis.d3(
    g,
    use_node_size_normalization=False,
    node_size_normalization_max=30,
    use_edge_size_normalization=False,
    edge_size_data_source='weight',
    edge_curvature=0.2,
    zoom_factor=0.6,
    graph_height=900,
    edge_size_factor=1,
)
print(f"nodes: {len(g.nodes)} edges: {len(g.edges)}")
print(f"root nodes: {red_counter}")
if os.path.exists(graph_output_path):
    os.remove(graph_output_path)
fig.export_html(graph_output_path)