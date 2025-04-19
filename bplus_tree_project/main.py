from generator import generate_records
from builder import build_dense_tree, build_sparse_tree
from bplustree import BPlusTree

if __name__ == "__main__":
    # build a small tree
    keys = [10, 20, 30, 40, 50, 60, 70, 80]
    t = BPlusTree(order=4)
    for k in keys:
        t.insert(k)

    # delete a key from a middle leaf
    t.delete(30)
    t.print_tree()

    # delete until the tree shrinks to a single leaf
    for k in [40, 50, 60, 70, 80, 10, 20]:
        t.delete(k)
    t.print_tree()
