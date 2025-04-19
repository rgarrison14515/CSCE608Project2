import random
from generator import generate_records
from builder import build_dense_tree, build_sparse_tree

# Apply an operation to the tree and print changes (including updates to nodes)
def apply_and_report(tree, operation, key):
    trace = []

    # Execute the operation and track changes
    if operation == "insert":
        tree.insert(key, tracer=trace)
    elif operation == "delete":
        tree.delete(key, tracer=trace)
    else:  # search
        found = tree.search(key, tracer=trace)

    # Print operation and affected nodes
    print(f"\n>>> {operation.upper()} {key}")
    for entry in trace:
        if isinstance(entry, tuple) and entry[0] == "UPDATED":
            _, before, after = entry
            print("   - changed:")
            print("     before:", before)
            print("     after :", after)
        else:
            print("   -", entry)

# Run experiment on a dense or sparse B+ tree of a given order
def run_one(order, is_dense):
    keys = generate_records()
    tree = build_dense_tree(keys, order) if is_dense else build_sparse_tree(keys, order)
    label = "DENSE" if is_dense else "SPARSE"
    print(f"\n=== ORDER {order} | {label} TREE ===")

    rng = random.Random(42)  

    # Run 2 inserts for dense trees, or 2 deletes for sparse ones
    operations = []
    if is_dense:
        operations = [("insert", rng.randint(100000, 200000)) for _ in range(2)]
    else:
        operations = [("delete", rng.choice(keys)) for _ in range(2)]

    # 5 more random insert/delete operations
    operations += [
        ("insert" if rng.random() < 0.5 else "delete", rng.randint(100000, 200000))
        for _ in range(5)
    ]

    # 5 search operations
    operations += [
        ("search", rng.randint(100000, 200000))
        for _ in range(5)
    ]

    # Apply each operation and show the results
    for op, key in operations:
        apply_and_report(tree, op, key)

# Run experiment on dense and sparse trees of orders 13 and 24
if __name__ == "__main__":
    for order in (13, 24):
        run_one(order, is_dense=True)
        run_one(order, is_dense=False)
