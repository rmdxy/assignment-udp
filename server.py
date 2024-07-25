import datetime
import random
import sys
import socket
import time
import threading

from helper import *

class Server:
    def __init__(self, server_port):
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.server_port))
        self.ns = {}
        self.addr = {}
        self.cname = {}

        self.load_master_file("master.txt")

    def load_master_file(self, file_path):
        with open(file_path) as f:
            for line in f:
                domain_name, r_type, data = line.split()
                self.process_record(domain_name, r_type, data)

    def process_record(self, domain_name, r_type, data):
        if r_type == "A":
            self.addr.setdefault(domain_name, set()).add(data)
        elif r_type == "CNAME":
            self.cname.setdefault(domain_name, set()).add(data)
        elif r_type == "NS":
            self.ns.setdefault(domain_name, set()).add(data)
        else:
            print("ERROR: It is not in master file")

    def run(self):
        print(f'Server listening at PORT:{self.server_port}')
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                header, question = decode_request(data)
                threading.Thread(target=self.process_request, args=(header, question, addr)).start()
            except ConnectionError:
                print(f"ERROR: Connection closed by PORT: {addr[1]}")

    def process_request(self, header, question, addr):
        delay = random.randrange(5)
        date = datetime.datetime.now()
        print(f"{date} rcv {addr[1]}: {header.qid} {question.r_data} {question.str_type} (delay: {delay}s)")

        #delay period
        time.sleep(delay)
        ans_str, auth_str, add_str = self.find_record(question.r_data, question.str_type)
        response = create_response(header, question, ans_str, auth_str, add_str)

        # send response
        print(f"{date} snd {addr[1]}: {header.qid} {question.r_data} {question.str_type}")
        self.sock.sendto(response, addr)

    def find_record(self, q_name, q_type, ans_str="", auth_str="", add_str=""):        
        if q_type == "A" and q_name in self.addr:
            return self.append_multiple_ans(q_name, "A", self.addr[q_name], ans_str, auth_str, add_str)
        elif q_type == "CNAME" and q_name in self.cname:
            return self.append_ans(q_name, "CNAME", self.cname[q_name], ans_str, auth_str, add_str)
        elif q_type == "NS" and q_name in self.ns:
            return self.append_multiple_ans(q_name, "NS", self.ns[q_name], ans_str, auth_str, add_str)
        elif q_type != "CNAME" and q_name in self.cname:
            ans_str = self.append_ans(q_name, "CNAME", self.cname[q_name], ans_str, auth_str, add_str)
            return self.find_record(list(self.cname[q_name])[0], q_type, ans_str, auth_str, add_str)
        else:
            ancestor = self.find_closest_ancestor(q_name)
            auth_str, add_str = self.append_ns_and_addr(ancestor, auth_str, add_str)

        ans_str = ''.join(ans_str)
        auth_str = ''.join(auth_str)
        add_str = ''.join(add_str)
        
        return ans_str, auth_str, add_str

    def append_ans(self, q_name, q_type, val, ans_str, auth_str, add_str):
        if (isinstance(val, set)):
            val = list(val)[0]
        ans_str = ''.join(ans_str)
        ans_str += f"{q_name}\t{q_type}\t{val}\n"
        return ans_str, auth_str, add_str

    def append_multiple_ans(self, q_name, q_type, vals, ans_str, auth_str, add_str):        
        for val in sorted(vals):
            ans_str = ''.join(ans_str)
            ans_str += f"{q_name}\t{q_type}\t{val}\n"
        return ans_str, auth_str, add_str

    def find_closest_ancestor(self, q_name):
        section = q_name.split(".")
        while section and ".".join(section) not in self.ns:
            section.pop(0)
        return ".".join(section) if section else "."

    def append_ns_and_addr(self, ancestor, auth_str, add_str):
        auth_str = ''.join(auth_str)
        add_str = ''.join(add_str)
        for val in self.ns[ancestor]:
            auth_str += f"{ancestor}\tNS\t{val}\n"
            if val in self.addr:
                for addr in self.addr[val]:
                    add_str += f"{val}\tA\t{addr}\n"
        return auth_str, add_str

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('ERROR USAGE: python3 server.py <server_port>')
        exit(1)
    server = Server(int(sys.argv[1]))
    try:
        server.run()
    except KeyboardInterrupt:
        exit(0)