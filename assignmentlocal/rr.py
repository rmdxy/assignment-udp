from parent import *

RTYPE_TO_ID = {"Answer": 1, "Authority": 2, "Additional": 3}
ID_TO_RTYPE = {1: "Answer", 2: "Authority", 3: "Additional"}

class ResourceRecord:
    def __init__(self, str_type: str, r_data: str):
        self.str_type = str_type
        self.r_data = r_data

    def encode(self):
        # call the encoding function with resource type -> id mapping
        return encode_message(self.str_type, self.r_data, RTYPE_TO_ID)

    @staticmethod
    def decode_header(data):
        # call the decoding function with id -> resource type mapping
        return decode_header(data, ID_TO_RTYPE)

    @staticmethod
    def decode_rdata(size, data):
        return decode_rdata(size, data)