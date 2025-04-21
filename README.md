# CSCE 608 Project 2: B+ Trees and Hash-Based Join Algorithms

This project implements key algorithms used in database systems, including:
- **B+ Tree operations** (search, range search, insertion, deletion)
- **One-pass and two-pass hash-based natural join algorithms**

All components are implemented in **Python**, and the environment simulates virtual disk and memory using custom classes to enforce block-based I/O and memory limits.

## How to Run
### B+ Tree Demo
1. Navigate to the `bplustree/` directory.
2. Run:
   python main.py
   python experiment.py
Output will include: Tree construction (dense/sparse) Insertions, deletions, Searches and Range Queries.
You'll have to uncomment the test cases in main.py, but experiment.py has the project deliverables.

### Hash Join Demo
Navigate to the hashbased_join_project/ directory.

Run:
  python driver.py
You can also run python test.py but you'll have to uncomment test cases. driver.py has the project deliverables.

## Requirements
Python 3.7

## Notes
Virtual memory is capped at 15 blocks; each block holds up to 8 tuples.

Disk reads/writes are tracked for evaluating I/O efficiency.

The project is self-contained and does not use a real DBMS or SQL engine.
