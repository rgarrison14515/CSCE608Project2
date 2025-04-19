class BPlusTreeNode:
    def __init__(self, order, is_leaf=False, parent=None):
        self.order = order
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []          
        self.next_leaf = None       # for range queries
        self.parent = parent        # used for splits

    def is_full(self):
        return len(self.keys) > self.order - 1  # max keys = order - 1

    def insert_key_sorted(self, key): # inserts key in sorted order and returns the key's index
        idx = 0
        while idx < len(self.keys) and key > self.keys[idx]:
            idx += 1
        self.keys.insert(idx, key)
        return idx

    # string for debugging/printing
    def __str__(self): 
        typ = "Leaf" if self.is_leaf else "Internal"
        return f"{typ} Node(keys={self.keys})"

    # change repr to act like str
    __repr__ = __str__


class BPlusTree:
    # constructor
    def __init__(self, order):
        self.order = order
        self.root = BPlusTreeNode(order, is_leaf=True)

    # walk down to correct leaf
    def _find_leaf(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        return node

    # leaf split: create right sibling, return (new_leaf, key to promote)
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

    # internal split: make new internal node, retur (new_right, key to promote)
    def _split_internal(self, internal):
        mid_idx = len(internal.keys) // 2
        promoted_key = internal.keys[mid_idx]

        right = BPlusTreeNode(self.order, is_leaf=False, parent=internal.parent)

        # distribute keys
        right.keys = internal.keys[mid_idx + 1:]
        internal.keys = internal.keys[:mid_idx]

        right.children = internal.children[mid_idx + 1:]
        internal.children = internal.children[:mid_idx + 1]

        # update parent pointers
        for child in right.children:
            child.parent = right

        return right, promoted_key

    
    def insert(self, key):
        # Insert key into correct leaf
        leaf = self._find_leaf(key)
        leaf.insert_key_sorted(key)

        # if no overflow we're done
        if not leaf.is_full():
            return

        # leaf overflow -> split and push the promoted key up
        new_leaf, promo = self._split_leaf(leaf)
        self._propagate_split(leaf, new_leaf, promo)
 
    def _propagate_split(self, left, right, promo_key):
        # Insert promoted key into parent of split node
        parent = left.parent

        if parent is None:
            # No parent means we're splitting the root, create new root
            new_root = BPlusTreeNode(self.order, is_leaf=False)
            new_root.keys = [promo_key]
            new_root.children = [left, right]
            left.parent = right.parent = new_root
            self.root = new_root
            return

        # insert promoted key and new right sibling into parent
        insert_pos = parent.insert_key_sorted(promo_key)
        parent.children.insert(insert_pos + 1, right)
        right.parent = parent

        # if parent overflows, split it (recursive)
        if parent.is_full():
            new_right, promo_up = self._split_internal(parent)
            self._propagate_split(parent, new_right, promo_up)

    
    # search for a key by walking to the correct leaf and checking
    def search(self, key):
        leaf = self._find_leaf(key)
        return key in leaf.keys

    #return all keys in [start key, end key] by scanning the leaf nodes
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



     # returns smalllest amount of keys lalowed in non root node (used for underflow check)
    def _min_keys(self):
        return (self.order + 1) // 2 - 1          # ceil(order/2) − 1

    # Get left/right sibling of a node and its separator info (used in rebalacing)
    def _sibling(self, node, want_left=True):
        parent = node.parent
        if parent is None:
            return None, -1, -1
        idx = parent.children.index(node)
        if want_left and idx > 0:
            return parent.children[idx - 1], idx - 1, idx - 1
        if not want_left and idx < len(parent.children) - 1:
            return parent.children[idx + 1], idx + 1, idx
        return None, -1, -1

    # merge right into left and delete separator key from parent (used when borrowing fails)
    def _merge_nodes(self, left, right, sep_idx):
        parent = left.parent
        if not left.is_leaf:
            # bring down separator key
            left.keys.append(parent.keys[sep_idx])
            left.keys.extend(right.keys)
            left.children.extend(right.children)
            for child in right.children:
                child.parent = left
        else:
            # merge keys + next pointers
            left.keys.extend(right.keys)
            left.next_leaf = right.next_leaf

        # remove sep key and right child pointer from parent
        parent.keys.pop(sep_idx)
        parent.children.pop(sep_idx + 1)

        # if parent under‑flows, recurse
        if parent is self.root and len(parent.keys) == 0:
            self.root = left
            self.root.parent = None
        elif parent is not self.root and len(parent.keys) < self._min_keys():
            self._rebalance(parent)

    # Make sure parent's separator key matches first key in this child (used in deletion)
    def _refresh_parent_key(self, node):
        parent = node.parent
        if parent is None:
            return
        idx = parent.children.index(node)
        if idx > 0:                       
            parent.keys[idx - 1] = node.keys[0]

    
    def delete(self, key):
            # Walk to correct leaf
            leaf = self._find_leaf(key)
            if key not in leaf.keys:
                return False

            # remove the key from the leaf
            leaf.keys.remove(key)

            if leaf is self.root:
                # shrink to empty leaf or single child
                if len(self.root.keys) == 0 and not self.root.is_leaf:
                    self.root = self.root.children[0]
                    self.root.parent = None
                return True

            if len(leaf.keys) >= self._min_keys():
                if leaf.keys:  #leaf isn't empty
                    self._refresh_parent_key(leaf) # check if parent separator is still valid
                return True

            self._rebalance(leaf)
            return True

    def _rebalance(self, node):
        min_k = self._min_keys()

        # try borrowing a key from left sibling
        left, left_idx, sep_idx = self._sibling(node, want_left=True)
        if left and len(left.keys) > min_k:
            if node.is_leaf:
                # Move last key from left to front of kurrent node, update parent separator
                borrow_key = left.keys.pop(-1)
                node.keys.insert(0, borrow_key)
                node.parent.keys[sep_idx] = node.keys[0]
            else:
                # Move child + separator from left to current node, update parent
                borrow_key = left.keys.pop(-1)
                borrow_child = left.children.pop(-1)
                node.keys.insert(0, node.parent.keys[sep_idx])
                node.children.insert(0, borrow_child)
                borrow_child.parent = node
                node.parent.keys[sep_idx] = borrow_key
            return

        # 2. try borrowing a key from right sibling
        right, right_idx, sep_idx = self._sibling(node, want_left=False)
        if right and len(right.keys) > min_k:
            if node.is_leaf:
                # Take the first key from right sibling, update parent separator
                borrow_key = right.keys.pop(0)
                node.keys.append(borrow_key)
                node.parent.keys[sep_idx] = right.keys[0]
            else:
                # Move separator and child from righ sibling into current node
                borrow_key = right.keys.pop(0)
                borrow_child = right.children.pop(0)
                node.keys.append(node.parent.keys[sep_idx])
                node.children.append(borrow_child)
                borrow_child.parent = node
                node.parent.keys[sep_idx] = borrow_key
            return

        # 3. can't borrow, so merge
        if left:    
            self._merge_nodes(left, node, sep_idx)
        else:
            self._merge_nodes(node, right, sep_idx)
            
    # print tree function: prints tree level by level
    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        print("    " * level + str(node))
        if not node.is_leaf:
            for child in node.children:
                self.print_tree(child, level + 1)
