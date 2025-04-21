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

    # Tracks nodes accessed/modified during operations, used because the project requires we do that
    def _record(self, tracer, *nodes):
        if tracer is not None:
            tracer.extend(nodes)

    # walk down to correct leaf
    def _find_leaf(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        return node

    # Split a full leaf node into two and return the new right node + key
    def _split_leaf(self, leaf):
        mid = (self.order) // 2
        new_leaf = BPlusTreeNode(self.order, is_leaf=True, parent=leaf.parent)

        # Distribute keys across the two leaf nodes
        new_leaf.keys = leaf.keys[mid:]
        leaf.keys = leaf.keys[:mid]

        # link the leaf chain
        new_leaf.next_leaf = leaf.next_leaf
        leaf.next_leaf = new_leaf

        # promote the first key of new leaf to the parent
        promoted_key = new_leaf.keys[0]
        return new_leaf, promoted_key

    # internal split: make new internal node, retur (new_right, key to promote)
    def _split_internal(self, internal):
        mid_idx = len(internal.keys) // 2
        promoted_key = internal.keys[mid_idx]

        right = BPlusTreeNode(self.order, is_leaf=False, parent=internal.parent)

        # split the keys and redistribute children
        right.keys = internal.keys[mid_idx + 1:]
        internal.keys = internal.keys[:mid_idx]

        right.children = internal.children[mid_idx + 1:]
        internal.children = internal.children[:mid_idx + 1]

        # update parent pointers
        for child in right.children:
            child.parent = right

        return right, promoted_key

    
    def insert(self, key, tracer=None):
        # Insert key into correct leaf
        leaf_path = []  # to collect nodes before split
        leaf = self._find_leaf(key)
        self._record(tracer, leaf)
        before = str(leaf)
        leaf.insert_key_sorted(key)

        # if the leaf overflows, split it and send the promoted key up
        if leaf.is_full():
            new_leaf, promo = self._split_leaf(leaf)
            self._record(tracer, new_leaf)  # new node created
            self._propagate_split(leaf, new_leaf, promo, tracer)

        if tracer is not None and before != str(leaf):
            tracer.append(("UPDATED", before, str(leaf)))
 
    # handle split propogation up a tree, create a new root if necessary
    def _propagate_split(self, left, right, promo_key, tracer=None):
        parent = left.parent

        # if there's no parent, the root was split so we need to create a new root node
        if parent is None:                            
            new_root = BPlusTreeNode(self.order, is_leaf=False)
            new_root.keys = [promo_key]
            new_root.children = [left, right]
            left.parent = right.parent = new_root
            self.root = new_root
            self._record(tracer, new_root)
            return

        # Insert the promoted key and right sibling into the parent
        self._record(tracer, parent)
        before = str(parent)

        insert_pos = parent.insert_key_sorted(promo_key)
        parent.children.insert(insert_pos + 1, right)
        right.parent = parent

        # Track changes
        if tracer is not None and before != str(parent):
            tracer.append(("UPDATED", before, str(parent)))

        # If the parent overflows, keep splitting upward (recursion)
        if parent.is_full():
            new_right, promo_up = self._split_internal(parent)
            self._record(tracer, new_right)           # new internal node
            self._propagate_split(parent, new_right, promo_up, tracer)


    
    # search for a key by walking to the correct leaf and checking
    def search(self, key, tracer=None):
        node = self.root
        while True:
            self._record(tracer, node) # track nodes touched
            if node.is_leaf:
                return key in node.keys
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]

    #return all keys in [start key, end key] by scanning the leaf nodes
    def range_search(self, start_key, end_key):
        result = []
        leaf = self._find_leaf(start_key)

        while leaf is not None:
            for k in leaf.keys:
                if start_key <= k <= end_key:
                    result.append(k)
                elif k > end_key:
                    return result # early exit if keys exceed the range
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

        try:
            idx = parent.children.index(node)
        except ValueError:  # nodes already been detached
            return None, -1, -1

        if want_left and idx > 0:
            return parent.children[idx - 1], idx - 1, idx - 1
        if not want_left and idx < len(parent.children) - 1:
            return parent.children[idx + 1], idx + 1, idx
        return None, -1, -1

    # merge right into left and delete separator key from parent (used when borrowing fails)
    def _merge_nodes(self, left, right, sep_idx, tracer=None):
        parent = left.parent
        self._record(tracer, left, right, parent)
        before_left, before_parent = str(left), str(parent)

        if not left.is_leaf:   
            #For internal nodes: bring down separator key and merge
            left.keys.append(parent.keys[sep_idx])
            left.keys.extend(right.keys)
            left.children.extend(right.children)
            for child in right.children:
                child.parent = left
        else:  
            # Leaft nodes: merge keys and update next_leaf pointer
            left.keys.extend(right.keys)
            left.next_leaf = right.next_leaf

        # Remove separator key and right child pointer from the parent
        parent.keys.pop(sep_idx)
        parent.children.pop(sep_idx + 1)

        # Record changes
        if tracer is not None:
            tracer.append(("UPDATED", before_left, str(left)))
            tracer.append(("UPDATED", before_parent, str(parent)))

        # If the parent is empty and is the root, shrink the tree height
        if parent is self.root and len(parent.keys) == 0:
            self.root = left
            self.root.parent = None
        elif parent is not self.root and len(parent.keys) < self._min_keys():
            # parent underflow, recurse upward
            self._rebalance(parent, tracer)


    # Ensure paren'ts separator key amtches first key of child node. Used during deletion to keep keys correct
    def _refresh_parent_key(self, node):
        parent = node.parent
        if parent is None:
            return
        idx = parent.children.index(node)
        if idx > 0:                       
            parent.keys[idx - 1] = node.keys[0]

    
    def delete(self, key, tracer=None):
        leaf = self._find_leaf(key)
        self._record(tracer, leaf)

        if key not in leaf.keys: # key isn't present in the tree to begin with
            return False

        before_leaf = str(leaf)
        leaf.keys.remove(key)

        # log update for tracing
        if tracer is not None and before_leaf != str(leaf):
            tracer.append(("UPDATED", before_leaf, str(leaf)))

        # Tree has only one node (root)
        if leaf is self.root:
            if len(self.root.keys) == 0 and not self.root.is_leaf:
                self.root = self.root.children[0]
                self.root.parent = None
            return True

        # leaf has enough keys to stay valid
        if len(leaf.keys) >= self._min_keys():
            if leaf.keys:
                self._refresh_parent_key(leaf) # maintain parent key correctness
            return True

        # Leaf underflows, needs rebalancing
        self._rebalance(leaf, tracer)
        return True

    # Rebalances tree after node drops below minimum key count, tries to borrow from siblings and merges if needed
    def _rebalance(self, node, tracer=None):
        min_k = self._min_keys()

         # If the node has been merged out during an earlier step, stop
        if node.parent is None:
            return
        try:
            _ = node.parent.children.index(node)
        except ValueError:
            return
        
        # Try borrowing key from left sibling
        left, _, sep_idx = self._sibling(node, want_left=True)
        if left and len(left.keys) > min_k:
            self._record(tracer, left, node, node.parent)
            before_left, before_node = str(left), str(node)

            if node.is_leaf:
                node.keys.insert(0, left.keys.pop(-1))
                node.parent.keys[sep_idx] = node.keys[0]
            else:
                borrow_key = left.keys.pop(-1)
                borrow_child = left.children.pop(-1)
                node.keys.insert(0, node.parent.keys[sep_idx])
                node.children.insert(0, borrow_child)
                borrow_child.parent = node
                node.parent.keys[sep_idx] = borrow_key

            if tracer is not None:
                tracer.append(("UPDATED", before_left, str(left)))
                tracer.append(("UPDATED", before_node, str(node)))
            return

        # Try borrowing from right sibling
        right, _, sep_right = self._sibling(node, want_left=False)
        if right and len(right.keys) > min_k:
            self._record(tracer, node, right, node.parent)
            before_right, before_node = str(right), str(node)

            if node.is_leaf:
                node.keys.append(right.keys.pop(0))
                node.parent.keys[sep_right] = right.keys[0]
            else:
                borrow_key = right.keys.pop(0)
                borrow_child = right.children.pop(0)
                node.keys.append(node.parent.keys[sep_right])
                node.children.append(borrow_child)
                borrow_child.parent = node
                node.parent.keys[sep_right] = borrow_key

            if tracer is not None:
                tracer.append(("UPDATED", before_right, str(right)))
                tracer.append(("UPDATED", before_node, str(node)))
            return

        # Can't borrow, merge with a sibling
        if left:
            self._merge_nodes(left, node, sep_idx, tracer)
        else:
            self._merge_nodes(node, right, sep_right, tracer)

            
    # print tree function: prints tree level by level
    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        print("    " * level + str(node))
        if not node.is_leaf:
            for child in node.children:
                self.print_tree(child, level + 1)
