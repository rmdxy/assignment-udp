from parent import *

QTYPE_TO_ID = {"A": 1, "NS": 2, "CNAME": 5}
ID_TO_QTYPE = {1: "A", 2: "NS", 5: "CNAME"}

class Question:
    def __init__(self, str_type: str, r_data: str):
        self.str_type = str_type
        self.r_data = r_data

    def encode(self):
        # call the encoding function with question type -> id mapping
        return encode_message(self.str_type, self.r_data, QTYPE_TO_ID)

    @staticmethod
    def decode_header(data):
        # call the decoding function with id -> question type mapping
        return decode_header(data, ID_TO_QTYPE)

    @staticmethod
    def decode_rdata(size, data):
        return decode_rdata(size, data)

