class BPlusTreeNode:
    def __init__(self, order, is_leaf=False):
        self.order = order
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.next_leaf = None  # only used for leaf nodes

    def is_full(self):
        # Max keys = order - 1 in most implementations; will refine if needed for edge cases
        return len(self.keys) >= self.order - 1

    def __str__(self):
        return f"{'Leaf' if self.is_leaf else 'Internal'} Node with keys: {self.keys}"

    def __repr__(self):
        return self.__str__()

class BPlusTree:
    def __init__(self, order):
        self.root = BPlusTreeNode(order, is_leaf=True)
        self.order = order

    #helper insert into leaf
    def _insert_into_leaf(self, leaf, key):
        """Insert key into the leaf node (no split)."""
        # Keep keys sorted
        i = 0
        while i < len(leaf.keys) and key > leaf.keys[i]:
            i += 1
        leaf.keys.insert(i, key)

    def _find_leaf(self, key, node=None):
        """Traverse the tree to find the leaf node where key should be inserted."""
        if node is None:
            node = self.root

        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        
        return node

    def _handle_leaf_split(self, leaf, key):
        print(f"(Stub) Need to split leaf with keys: {leaf.keys} and insert key: {key}")
        # Full implementation coming next

    def insert(self, key):
        root = self.root

        # If root is a leaf and not full, handle like before
        if root.is_leaf:
            if not root.is_full():
                self._insert_into_leaf(root, key)
            else:
                # First-time root split (still valid)
                new_leaf = BPlusTreeNode(self.order, is_leaf=True)
                temp_keys = root.keys + [key]
                temp_keys.sort()

                mid_index = len(temp_keys) // 2
                left_keys = temp_keys[:mid_index]
                right_keys = temp_keys[mid_index:]

                root.keys = left_keys
                new_leaf.keys = right_keys

                new_root = BPlusTreeNode(self.order, is_leaf=False)
                new_root.keys = [right_keys[0]]
                new_root.children = [root, new_leaf]

                self.root = new_root
                root.next_leaf = new_leaf
        else:
            # Root is an internal node — insert recursively
            leaf = self._find_leaf(key)
            if not leaf.is_full():
                self._insert_into_leaf(leaf, key)
            else:
                # Next step: split this leaf and propagate up
                self._handle_leaf_split(leaf, key)




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
