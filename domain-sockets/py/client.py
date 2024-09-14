import socket
import sys

BUFFER_SIZE = 1024

def client(socket_path, message):

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(socket_path)
        s.sendall(message.encode())
        data = s.recv(BUFFER_SIZE)
    
    return data.decode()

if __name__ == "__main__":
    socket_path = sys.argv[1]
    message = sys.argv[2]

    response = client(socket_path, message)
    print(response)
