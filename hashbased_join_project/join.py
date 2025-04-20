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

def two_pass_hash_join(R_disk: VirtualDisk, S_disk: VirtualDisk, 
                       mem_blocks: int = VirtualMemory.MAX_BLOCKS) -> Tuple[List[Tuple[int, int, int]], int]:
    """
    Performs two pass hash join on relations R(A, B) and S(B, C) using B as the join key.
    Returns (joined tuples, total disk/IOs)
    """
    # Pass 1: partition phase 
    num_partitions = mem_blocks - 1   # Leave oe block for input buffering
    R_parts = [VirtualDisk() for _ in range(num_partitions)]
    S_parts = [VirtualDisk() for _ in range(num_partitions)]

    vm = VirtualMemory()  # Will reuse this across both relations

    # partition R: hash each (A, B) tuple based on B into one of the R partitions
    for blk_idx in range(len(R_disk)):
        vm.read(R_disk, blk_idx)
        blk = vm.blocks[-1]
        for (a, b) in blk:
            pid = h(b, num_partitions)
            dst_blk = (R_parts[pid].blocks[-1]
                       if R_parts[pid].blocks and not R_parts[pid].blocks[-1].is_full()
                       else Block())
            dst_blk.add((a, b))
            if dst_blk not in R_parts[pid].blocks:
                vm.write(R_parts[pid], dst_blk)  # write block to disk and remove from memory
        vm.blocks.pop()   # remove processed input block from memory

    # partition S: hash each (B, C) tuple based on B into one of the S partitions
    for blk_idx in range(len(S_disk)):
        vm.read(S_disk, blk_idx)
        blk = vm.blocks[-1]
        for (b, c) in blk:
            pid = h(b, num_partitions)
            dst_blk = (S_parts[pid].blocks[-1]
                       if S_parts[pid].blocks and not S_parts[pid].blocks[-1].is_full()
                       else Block())
            dst_blk.add((b, c))
            if dst_blk not in S_parts[pid].blocks:
                vm.write(S_parts[pid], dst_blk)
        vm.blocks.pop()

    pass1_io = vm.io_counter  # Save number of IOs so far
    vm = VirtualMemory()   #Reset memory and IO counter for next pass

    # Pass 2: probe each partition pair 
    result = []
    for pid in range(num_partitions):
        Rp, Sp = R_parts[pid], S_parts[pid]
        if len(Rp) == 0 or len(Sp) == 0:
            continue   # Nothing to join

        # decide which partition is small enough to build a hash table on
        if len(Rp) <= len(Sp) and len(Rp) <= mem_blocks:
            small, large, build_R = Rp, Sp, True
        elif len(Sp) <= mem_blocks:
            small, large, build_R = Sp, Rp, False
        else:
            raise RuntimeError("Partition still too large for one-pass")

        # Read the smaller side into memory and build the hash table
        hash_t = defaultdict(list)
        for blk_idx in range(len(small)):
            vm.read(small, blk_idx)
        for blk in vm.blocks:
            for tup in blk:
                if build_R:
                    a, b = tup
                    hash_t[b].append(a) # map B to all matching A's
                else:
                    b, c = tup
                    hash_t[b].append(c) # mab B to all matching C's

        # scan larger side and probe the hash table
        for blk_idx in range(len(large)):
            vm.read(large, blk_idx)
            blk = vm.blocks[-1]
            for tup in blk:
                if build_R:
                    b, c = tup
                    for a in hash_t.get(b, []):
                        result.append((a, b, c))
                else:
                    a, b = tup
                    for c in hash_t.get(b, []):
                        result.append((a, b, c))
            vm.blocks.pop()  # remove block after processing

        vm.blocks.clear()  # clear memory before next partition

    total_io = pass1_io + vm.io_counter
    return result, total_io