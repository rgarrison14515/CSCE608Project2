from collections import defaultdict
from typing import List, Tuple
from disk import Block, VirtualDisk, VirtualMemory

# Hash function using modulo division
def h(val: int, buckets: int = 101) -> int:
    return val % buckets

# One pass hash join between R(A, B) and S(B, C)
def one_pass_hash_join(R_disk: VirtualDisk, S_disk: VirtualDisk) -> Tuple[List[Tuple[int, int, int]], int]:
    """Performs one pass natural join between R and S on attribute B. 
        Assumes smaller relation fits entirely in memory (<= 15 blocks)
        Returns the resulting tuples and the number of disk IOs used"""
    
    # Choose smaller relation to build the hash table on
    if len(R_disk) <= len(S_disk):
        small_disk, large_disk = R_disk, S_disk
        build_side = 'R'
    else:
        small_disk, large_disk = S_disk, R_disk
        build_side = 'S'

    mem = VirtualMemory()  # Resets IO counter

    # Read the small relation into memory and build hash table
    hash_table = defaultdict(list) # maps B to a list of tuples
    for blk_idx in range(len(small_disk)):
        mem.read(small_disk, blk_idx)
    for blk in mem.blocks:
        for tup in blk:
            if build_side == 'R':   # tuple is (A, B)
                a, b = tup
                hash_table[h(b)].append(tup)
            else:   # tuple is (B, C)
                b, c = tup
                hash_table[h(b)].append(tup)

    # Scan the large relation and probe hash table
    result = []
    for blk_idx in range(len(large_disk)):
        mem.read(large_disk, blk_idx)   # load one block
        blk = mem.blocks[-1]
        for tup in blk:
            if build_side == 'R': # tuple is (B, C)
                b, c = tup
                for (a_build, b_build) in hash_table[h(b)]:
                    if b_build == b:
                        result.append((a_build, b, c))
            else: # tuple is (A, B)
                a, b = tup
                for (b_build, c_build) in hash_table[h(b)]:
                    if b_build == b:
                        result.append((a, b, c_build))
        mem.blocks.pop()  # clear one block from memory after processing

    return result, mem.io_counter
