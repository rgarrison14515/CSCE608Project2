# Final experiment for hash based joins
import random
from data_gen import build_relation_S, build_relation_R
from join import one_pass_hash_join, two_pass_hash_join
from disk import VirtualMemory

rng = random.Random(7)

# Selects best join method based on size of input relations
def smart_join(R, S):
    if len(R) <= VirtualMemory.MAX_BLOCKS or len(S) <= VirtualMemory.MAX_BLOCKS:
        return "ONE-PASS", *one_pass_hash_join(R, S)
    return "TWO-PASS", *two_pass_hash_join(R, S)

# prints list of tuples
def pretty_print_tuples(tups):
    for t in tups:
        print("   ", t)

def main():
    # Generate shared relation S and two R datasets (R1, R2)
    S = build_relation_S()
    R1 = build_relation_R(1_000, S, True) # B-values guaranteed to match S
    R2 = build_relation_R(1_200, S, False) # Randomly chosen B values

    for name, R in [("R1", R1), ("R2", R2)]:
        algo, out, ios = smart_join(R, S)
        print(f"\n{name} Natural Join S  |  {algo}  |  output tuples: {len(out)}  |  disk I/Os: {ios}")

        if name == "R1":
            # pick 20 random B‑values from the join output to sample
            Bs = [t[1] for t in out]
            sample_B = rng.sample(Bs, 20) if len(Bs) >= 20 else Bs
            print("  Sampled B-values:", sample_B)
            print("  Matching tuples:")
            pretty_print_tuples([t for t in out if t[1] in sample_B])
        else:
            # print all the results for R2 join (smaller output so it's fine)
            print("  All result tuples:")
            pretty_print_tuples(out)

if __name__ == "__main__":
    main()
