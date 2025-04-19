import random
from disk import Block, VirtualDisk

rng = random.Random(42)

def build_relation_S() -> VirtualDisk:
    """Builds relation S(B, C) with 5000 tuples. B is unique integer, C is random value"""
    disk = VirtualDisk()
    for b in rng.sample(range(10_000, 50_001), 5_000):
        # Use the last block if it's not full: else start a new one
        blk = Block() if (len(disk) == 0 or disk.blocks[-1].is_full()) else disk.blocks[-1]
        tup = (b, rng.randint(0, 999_999))  #(B, C)
        blk.add(tup)
        if blk not in disk.blocks:
            disk.write_block(blk)
    return disk

def build_relation_R(size: int, S_disk: VirtualDisk,
                     restrict_to_S_values=True) -> VirtualDisk:
    """Build relation R(A, B) with given size. 
        If restrict_to_S_values: B is sampled from S(B, C)
        Else: B is a random integer in [20,000, 30,000] range """
    if restrict_to_S_values:
        # Extract B-values from S to overlap
        S_B_vals = [t[0] for blk in S_disk.blocks for t in blk]
    else:
        S_B_vals = list(range(20_000, 30_001))
    disk = VirtualDisk()
    for _ in range(size):
        b = rng.choice(S_B_vals)
        a = rng.randint(0, 999_999)
        blk = Block() if (len(disk) == 0 or disk.blocks[-1].is_full()) else disk.blocks[-1]
        blk.add((a, b))
        if blk not in disk.blocks:
            disk.write_block(blk)
    return disk

if __name__ == "__main__":
    # Generate base, test relations
    S = build_relation_S()
    R1 = build_relation_R(1_000, S, True)
    R2 = build_relation_R(1_200, S, False)
    print("Disk blocks:  S =", len(S), "  R1 =", len(R1), "  R2 =", len(R2))
