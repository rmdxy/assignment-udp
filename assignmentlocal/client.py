import random
import sys
import socket

from helper import *

def create_request(q_name: str, q_type: str):
    # create DNS question section
    question = Question(q_type, q_name).encode()

    # create DNS header section
    qid = random.randint(0,65535)
    header = Header(len(question), qid).encode()

    # combine header and question into byte array
    req_data = bytearray()
    req_data.extend(header)
    req_data.extend(question)

    return bytes(req_data), qid


def client_run(server_port, q_name, q_type, timeout):
    data, qid = create_request(q_name, q_type)
    # UDP socket for communication
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    sock.sendto(data, ("localhost", server_port))
    try:
        # receive response from server
        res, _ = sock.recvfrom(4096)
        header, question, rrs = decode_response(res)
        print(f"ID: {qid}\n")
        print("QUESTION SECTION:")
        print(q_name, q_type, "\n")
        for rr in rrs:
            print(f"{rr.str_type.upper()} SECTION:")
            print(rr.r_data)
        # if no response, timeout
    except socket.timeout:
        print(f"timed out")


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('ERROR USAGE: python3 client.py <server_port> <q_name> <q_type> <timeout>')
        exit(1)
    client_run(int(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4]))