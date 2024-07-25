import struct

class Header:
    def __init__(self, size: int, qid: int):
        self.size = size
        self.qid = qid

    def encode(self):
        # pack struct with two uint16
        return struct.pack('<HH', self.size, self.qid)

    @staticmethod
    def decode(data):
        # unpack struct with two uint16
        size, qid = struct.unpack('<HH', data)
        return Header(size, qid)
