import socket
import sys
import os
import json

BUFFER_SIZE = 1024

def server(socket_path):

    # Remove the socket file if it already exists
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise

    # Create a Unix domain socket
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(socket_path)
        s.listen(1)
        print(f"Server listening on {socket_path}")

        while True:
            conn, addr = s.accept()
            with conn:
                print("Connected by", addr)
                while True:
                    data = conn.recv(BUFFER_SIZE)
                    if not data:
                        break
                    response = json.dumps(eval(data), indent=1).encode('utf-8')
                    conn.sendall(response)

if __name__ == "__main__":
    socket_path = sys.argv[1]
    server(socket_path)
