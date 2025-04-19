from generator import generate_records
from builder import build_dense_tree, build_sparse_tree
from bplustree import BPlusTree

if __name__ == "__main__":
    keys = [10, 20, 30, 40, 50, 60, 70, 80]
    t = BPlusTree(order=4)
    for k in keys:
        t.insert(k)
    t.print_tree()
