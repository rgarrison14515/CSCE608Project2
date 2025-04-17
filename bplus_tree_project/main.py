from generator import generate_records
from builder import build_dense_tree, build_sparse_tree


if __name__ == "__main__":
    test_keys = [10, 20, 30, 40, 50]
    order = 4  # max 3 keys per node

    tree = build_dense_tree(test_keys, order)
    tree.print_tree()
