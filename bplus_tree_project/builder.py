from bplustree import BPlusTree

def build_dense_tree(keys, order):
    tree = BPlusTree(order)
    for key in keys:
        tree.insert(key)
    return tree

def build_sparse_tree(keys, order):
    tree = BPlusTree(order)
    for key in keys:
        tree.insert(key)
        # Could throttle insertions (e.g., pad with dummy deletes later)
    return tree
