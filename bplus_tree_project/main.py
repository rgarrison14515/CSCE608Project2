from generator import generate_records
from builder import build_dense_tree, build_sparse_tree

if __name__ == "__main__":
    records = generate_records()
    order = 13

    print("Building dense B+ Tree...")
    dense_tree = build_dense_tree(records, order)
    dense_tree.print_tree()

    print("\nBuilding sparse B+ Tree...")
    sparse_tree = build_sparse_tree(records, order)
    sparse_tree.print_tree()
