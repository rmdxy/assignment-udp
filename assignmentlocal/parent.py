import struct

def encode_message(str_type, r_data, type_to_id):
    req_data = bytearray()
    req_data.extend(struct.pack('<H', len(r_data)))
    req_data.extend(struct.pack('<H', type_to_id[str_type]))
    req_data.extend(struct.pack(f'<{len(r_data)}s', r_data.encode()))
    return bytes(req_data)

def decode_header(data, id_to_type):
    # unpack struct with uint16
    size = struct.unpack_from('<H', data, 0)[0]
    type_id = struct.unpack_from('<H', data, 2)[0]
    return size, id_to_type[type_id]

def decode_rdata(size, data):
    # unpack struct with variable length string
    r_data = struct.unpack_from(f'<{size}s', data, 0)[0]
    return r_data.decode()