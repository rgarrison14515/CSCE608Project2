import random

def generate_records(num_records=10000, min_val=100000, max_val=200000):
    return sorted(random.sample(range(min_val, max_val + 1), num_records))

if __name__ == "__main__":
    keys = generate_records()
    print("Generated record keys:")
    print(keys[:20])  # preview first 20
