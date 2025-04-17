class BPlusTreeNode:
    def __init__(self, order, is_leaf=False):
        self.order = order
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.next_leaf = None  # only used for leaf nodes

    def is_full(self):
        return len(self.keys) >= self.order - 1

    def __str__(self):
        return f"{'Leaf' if self.is_leaf else 'Internal'} Node with keys: {self.keys}"


class BPlusTree:
    def __init__(self, order):
        self.root = BPlusTreeNode(order, is_leaf=True)
        self.order = order

    def insert(self, key):
        # Will implement later
        pass

    def delete(self, key):
        # Will implement later
        pass

    def search(self, key):
        # Will implement later
        pass

    def range_search(self, start_key, end_key):
        # Will implement later
        pass

    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        print("    " * level + str(node))
        if not node.is_leaf:
            for child in node.children:
                self.print_tree(child, level + 1)
