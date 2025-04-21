from data_gen import build_relation_S, build_relation_R
from join import one_pass_hash_join
from join import two_pass_hash_join

# one hash join test
'''
print("One pass hash join:")
S = build_relation_S()                 # 5,000 tuples / 625 blocks
Rsmall = build_relation_R(100, S, True)  # 100 tuples =  13 blocks
print("blocks   S:", len(S), "  Rsmall:", len(Rsmall))

out, ios = one_pass_hash_join(Rsmall, S)
print("joined tuples:", len(out), "   disk I/Os:", ios)
'''

'''
# two pass hash join test
print("Two pass hash join:")
S = build_relation_S()                   # 5,000 tuples / 625 blocks
Rlarge = build_relation_R(1200, S, False)  # 1,200 tuples, B vals not guaranteed to match
print("blocks   S:", len(S), "  Rlarge:", len(Rlarge))

out, ios = two_pass_hash_join(Rlarge, S)
print("joined tuples:", len(out), "   disk I/Os:", ios)
'''