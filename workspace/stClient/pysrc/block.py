# -*- coding: utf-8 -*-
class Block:
    def __init__(self):
        self.offset = 0
        self.type = ""

class Compare_Block(Block):
    def __init__(self):
        self.sha_hash = 0

class Transfer_Block(Block):
    def __init__(self):
        self.str = ""
        self.src_offset = ""
        self.dst_offset = ""
