from bplustree import BPlusTree
import random

def build_dense_tree(keys, order):
    tree = BPlusTree(order)
    random.shuffle(keys)           # dense wants random order
    for k in keys:
        tree.insert(k)
    return tree

def build_sparse_tree(keys, order):
    tree = BPlusTree(order)
    keys_sorted = sorted(keys)     #  insert monotonically
    for k in keys_sorted:
        tree.insert(k)
    # delete every second key to thin the tree
    for k in keys_sorted[::2]:
        tree.delete(k)
    return tree
