import struct

from header import *
from question import *
from rr import *

def decode_request(data):
    # decode header
    header = Header.decode(data[:4])
    # decode header of variable length segment
    q_size, q_type = Question.decode_header(data[4:8])
    # decode data of variable length segment
    q_name = Question.decode_rdata(q_size, data[8:8 + q_size])
    return header, Question(q_type, q_name)


def decode_response(data):
    # pointer for how many bytes have been read
    cur = 0

    # decode header
    header = Header.decode(data[cur:cur + 4])
    cur += 4

    # decode question
    q_size, q_type = Question.decode_header(data[cur:cur + 4])
    cur += 4
    q_name = Question.decode_rdata(q_size, data[cur:cur + q_size])
    cur += q_size
    question = Question(q_type, q_name)

    rrs = []
    for i in range(3):
        if header.size == cur - 4:
            # no more resource records
            return header, question, rrs
        # decode resource record
        r_size, r_type = ResourceRecord.decode_header(data[cur:cur + 4])
        cur += 4
        records = ResourceRecord.decode_rdata(r_size, data[cur:cur + r_size])
        cur += r_size
        rrs.append(ResourceRecord(r_type, records))

    return header, question, rrs

def create_response(header, question, ans, auth, add):

    def encode_section(str_type, data, req_data, total_size):
        if data:
            encoded_sec = ResourceRecord(str_type, data).encode()
            req_data.extend(encoded_sec)
            total_size += len(encoded_sec)
        return total_size

    # Encode the question section
    q_encoded = question.encode()
    total_size = len(q_encoded)

    # Create byte object
    req_data = bytearray()
    req_data.extend(Header(total_size, header.qid).encode())
    req_data.extend(q_encoded)

    # Encode other sections and update size
    total_size = encode_section("Answer", ans, req_data, total_size)
    total_size = encode_section("Authority", auth, req_data, total_size)
    total_size = encode_section("Additional", add, req_data, total_size)

    # Update header
    req_data[0:len(Header(total_size, header.qid).encode())] = Header(total_size, header.qid).encode()

    return bytes(req_data)
