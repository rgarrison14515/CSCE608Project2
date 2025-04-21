from generator import generate_records
from builder import build_dense_tree, build_sparse_tree
from bplustree import BPlusTree

# File used for testing, getting output for project report
if __name__ == "__main__":
    # test for dense tree
    '''
    # Generate a small but rich dataset (for visual clarity)
    keys = generate_records(num_records=30)  # Fewer keys = more readable tree

    # Build a dense B+ tree of a smaller order for better printing
    order = 4
    tree = build_dense_tree(keys, order)

    print("Dense B+ Tree (order = 4, 30 keys):")
    tree.print_tree()
    '''
    #test for sparse tree
    '''
    keys = generate_records(num_records=30)
    order = 4
    tree = build_sparse_tree(keys, order)
    print("Sparse B+ Tree (order = 4, 30 keys, after deletions):")
    tree.print_tree()
    '''

    # insertion test
    '''
    # INSERTION DEMO: Force a split + promotion
    print("Insertion Demo (Order 3)")
    t = BPlusTree(order=3)

    for k in [10, 20, 30, 40]:
        print(f"\nInserting {k}:")
        t.insert(k)
        t.print_tree()
    '''

        # DELETION DEMO: Show merging + height drop
    print("\n=== Deletion Demo (Order 3) ===")
    t = BPlusTree(order=3)

    for k in [10, 20, 30, 40]:
        t.insert(k)

    print("\nInitial Tree:")
    t.print_tree()

    for k in [40, 30]:
        print(f"\nDeleting {k}:")
        t.delete(k)
        t.print_tree()
