class BPlusTreeNode:
    def __init__(self, order, is_leaf=False, parent=None):
        self.order = order
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []          # list[ BPlusTreeNode ]
        self.next_leaf = None       # forward pointer for range scans
        self.parent = parent        # back‑pointer used when bubbling splits

    # convenience 
    def is_full(self):
        return len(self.keys) > self.order - 1          # max keys = order - 1

    def insert_key_sorted(self, key):
        idx = 0
        while idx < len(self.keys) and key > self.keys[idx]:
            idx += 1
        self.keys.insert(idx, key)
        return idx

    def __str__(self):
        typ = "Leaf" if self.is_leaf else "Internal"
        return f"{typ} Node(keys={self.keys})"

    __repr__ = __str__


class BPlusTree:
    # constructor
    def __init__(self, order):
        self.order = order
        self.root = BPlusTreeNode(order, is_leaf=True)

    # helper: locate leaf that should contain key
    def _find_leaf(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        return node

    # helper: split a full *leaf* and return (new_leaf, promoted_key)
    def _split_leaf(self, leaf):
        mid = (self.order) // 2
        new_leaf = BPlusTreeNode(self.order, is_leaf=True, parent=leaf.parent)

        new_leaf.keys = leaf.keys[mid:]
        leaf.keys = leaf.keys[:mid]

        # link the leaf chain
        new_leaf.next_leaf = leaf.next_leaf
        leaf.next_leaf = new_leaf

        promoted_key = new_leaf.keys[0]
        return new_leaf, promoted_key

    # helper: split a full *internal* node and return (new_right, promoted) 
    def _split_internal(self, internal):
        mid_idx = len(internal.keys) // 2
        promoted_key = internal.keys[mid_idx]

        right = BPlusTreeNode(self.order, is_leaf=False, parent=internal.parent)

        # distribute keys / children
        right.keys = internal.keys[mid_idx + 1:]
        internal.keys = internal.keys[:mid_idx]

        right.children = internal.children[mid_idx + 1:]
        internal.children = internal.children[:mid_idx + 1]

        # fix parents of moved children
        for child in right.children:
            child.parent = right

        return right, promoted_key

    # INSERT 
    def insert(self, key):
        leaf = self._find_leaf(key)
        leaf.insert_key_sorted(key)

        # if leaf overflow ⇒ split and propagate
        if not leaf.is_full():
            return

        new_leaf, promo = self._split_leaf(leaf)
        self._propagate_split(leaf, new_leaf, promo)

    # helper: bubble split results up the tree 
    def _propagate_split(self, left, right, promo_key):
        parent = left.parent

        if parent is None:
            # create new root
            new_root = BPlusTreeNode(self.order, is_leaf=False)
            new_root.keys = [promo_key]
            new_root.children = [left, right]
            left.parent = right.parent = new_root
            self.root = new_root
            return

        # insert separator and pointer to right sibling
        insert_pos = parent.insert_key_sorted(promo_key)
        parent.children.insert(insert_pos + 1, right)
        right.parent = parent

        if parent.is_full():
            new_right, promo_up = self._split_internal(parent)
            self._propagate_split(parent, new_right, promo_up)

    # SEARCH 
    def search(self, key):
        leaf = self._find_leaf(key)
        return key in leaf.keys

    #  RANGE SEARCH: inclusive [start, end] 
    def range_search(self, start_key, end_key):
        result = []
        leaf = self._find_leaf(start_key)

        while leaf is not None:
            for k in leaf.keys:
                if start_key <= k <= end_key:
                    result.append(k)
                elif k > end_key:
                    return result
            leaf = leaf.next_leaf
        return result

    # DELETE (stub – next milestone) 
    def delete(self, key):
        raise NotImplementedError("Deletion / rebalancing still TODO")

    # pretty‑print 
    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        print("    " * level + str(node))
        if not node.is_leaf:
            for child in node.children:
                self.print_tree(child, level + 1)
