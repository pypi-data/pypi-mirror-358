import logging


def insns_stats(smalitree):
    stats = count_stats(smalitree)
    print("{}: {} insns | methods: {} total, {} synchronized, {} ignored | {} classes".format(
        stats.treeId, stats.insns, stats.methods, stats.sync_methods, stats.ignored_methods, stats.classes
    ))


def count_stats(smalitree):
    classes = len(smalitree.classes)
    methods = sum([len(cl.methods) for cl in smalitree.classes])
    sync_methods = sum([sum(1 for m in ms if m.synchronized) for ms in [cl.methods for cl in smalitree.classes]])
    ignored_methods = sum([sum(1 for m in ms if m.ignore) for ms in [cl.methods for cl in smalitree.classes]])
    fields_sum = sum([len(cl.fields) for cl in smalitree.classes])
    insns_sum = sum([sum([len(m.insns) for m in ms]) for ms in [cl.methods for cl in smalitree.classes]])
    tree_stats = TreeStats(smalitree.Id, insns_sum, fields_sum, methods, sync_methods, ignored_methods, classes)
    return tree_stats


class StatsCounter(object):
    '''Calculates how many classes and methods'''

    def __init__(self):
        self.stats_original = []
        self.stats_shrunk = []


    def put_original(self, smalitree):
        stats = count_stats(smalitree)
        self.stats_original.append(stats)


    def put_original_trees(self, strees):
        for st in strees:
            self.stats_original.append(count_stats(st))


    def put_shrunk(self, smalitree):
        stats = count_stats(smalitree)
        self.stats_shrunk.append(stats)


    def put_shrunk_trees(self, strees):
        for st in strees:
            self.stats_shrunk.append(count_stats(st))


    def calculate_total(self, stats_array):
        stats = TreeStats(
            0,
            sum(st.insns for st in stats_array),
            sum(st.fields for st in stats_array),
            sum(st.methods for st in stats_array),
            sum(st.sync_methods for st in stats_array),
            sum(st.ignored_methods for st in stats_array),
            sum(st.classes for st in stats_array)
        )
        return stats


    def log_stats(self, stats):
        logging.info("{}: {} insns | fields: {} | methods: {} total, {} synchronized, {} ignored | {} classes".format(
            stats.treeId, stats.insns, stats.fields, stats.methods, stats.sync_methods, stats.ignored_methods, stats.classes
        ))


    def log_total(self):
        total_original = self.calculate_total(self.stats_original)
        total_shrunk = self.calculate_total(self.stats_shrunk)
        self.log_stats(total_original)
        self.log_stats(total_shrunk)
        insns_cut = 100*(total_original.insns-total_shrunk.insns)/total_original.insns
        logging.info("insns removed: {}%".format(insns_cut))


class TreeStats(object):
    def __init__(self, treeId, insns, fields, methods, sync_methods, ignored_methods, classes):
        self.treeId = treeId
        self.insns = insns
        self.fields = fields
        self.methods = methods
        self.sync_methods = sync_methods
        self.ignored_methods = ignored_methods
        self.classes = classes
