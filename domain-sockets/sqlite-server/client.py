iport socket
import time
import random
import string
import struct
import sys

## Constants
PUT_SOCKET_PATH = "put_socket"
GET_SOCKET_PATH = "get_socket"
MSGPREFIX = b">I"

def generate_random_data(size=1024):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size)).encode()

def connect_socket(path):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(path)
    return sock

def send_message(sock, data):
    message = struct.pack(MSGPREFIX, len(data)) + data
    sock.sendall(message)

def recv_message(sock):
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack(MSGPREFIX, raw_msglen)[0]
    return recvall(sock, msglen)

def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def put_operation(sock, data):
    send_message(sock, data)
    return recv_message(sock)

def get_operation(sock, key):
    send_message(sock, key)
    return recv_message(sock)

def run_benchmark(ntrials, nbytes):
    put_sock = connect_socket(PUT_SOCKET_PATH)
    get_sock = connect_socket(GET_SOCKET_PATH)

    keys = []

    data = generate_random_data(nbytes)

    # PUT benchmark
    start_time = time.time()
    for _ in range(ntrials):
        key = put_operation(put_sock, data)
        keys.append(key)
    put_time = time.time() - start_time

    # GET benchmark
    start_time = time.time()
    for key in keys:
        get_operation(get_sock, key)
    get_time = time.time() - start_time

    put_sock.close()
    get_sock.close()

    return put_time, get_time

def main():

    ntrials = int(sys.argv[1])
    nbytes = int(sys.argv[2]) 

    put_time, get_time = run_benchmark(ntrials, nbytes)

    print(f"Time taken for {str(ntrials)} PUT operations of {str(nbytes)} bytes: {put_time:.2f} seconds")
    print(f"Time taken for {str(ntrials)} GET operations of {str(nbytes)} bytes: {get_time:.2f} seconds")
    print(f"Average PUT time: {put_time/ntrials*1000:.2f} ms")
    print(f"Average GET time: {get_time/ntrials*1000:.2f} ms")
    print(f"Average PUT time / kb: {put_time/ntrials*1000/nbytes*1000:.2f} ms")
    print(f"Average GET time / kb: {get_time/ntrials*1000/nbytes*1000:.2f} ms")

if __name__ == "__main__":
    main()
