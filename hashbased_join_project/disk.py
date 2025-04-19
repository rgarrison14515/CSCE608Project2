class Block:
    MAX_TUPLES = 8  # each block can hold 8 tuples 

    def __init__(self):
        self.records = []   # tuples are stored here

    def is_full(self):
        return len(self.records) >= Block.MAX_TUPLES

    def add(self, tup):
        if self.is_full():
            raise ValueError("Block full")
        self.records.append(tup)

    def __iter__(self):
        return iter(self.records)

    def __len__(self):
        return len(self.records)


class VirtualDisk:
    def __init__(self):
        self.blocks: list[Block] = [] # "Unlimited disk storage"

    def write_block(self, blk: Block):
        self.blocks.append(blk)  # write a block to the disk

    def read_block(self, idx: int) -> Block:
        return self.blocks[idx] # read a block by index

    def __len__(self):
        return len(self.blocks)


class VirtualMemory:
    MAX_BLOCKS = 15  # memory can hold up to 15 blocks at once
    def __init__(self):
        self.blocks: list[Block] = [] # buffer in main memory
        self.io_counter = 0    # count IO operatoins


    def read(self, disk: VirtualDisk, blk_idx: int):
        if len(self.blocks) >= VirtualMemory.MAX_BLOCKS:
            raise RuntimeError("Main memory full")
        # simulate disk to memory read
        self.blocks.append(disk.read_block(blk_idx))
        self.io_counter += 1

    def write(self, disk: VirtualDisk, blk: Block):
        # simulate memory to disk write
        disk.write_block(blk)
        self.io_counter += 1
        self.blocks.remove(blk)  # clear the slot from memory
