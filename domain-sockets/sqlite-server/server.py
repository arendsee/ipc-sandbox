import os
import socket
import threading
import sqlite3
import struct

## Constants
PUT_SOCKET_PATH = "put_socket"
GET_SOCKET_PATH = "get_socket"
DB_PATH = "mlc_data.db"


## SQLite Setup
def setup_sqlite() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS kv_store
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     value BLOB)''')
    conn.close()


def get_db_connection():
    return sqlite3.connect(DB_PATH)


## Create domain socket
def create_socket(path: str) -> socket.socket:
    if os.path.exists(path):
        os.unlink(path)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(path)
    sock.listen(1)
    return sock


# Message prefix indicating a 4-byte length in network byte order
MSGPREFIX = b">I"


# Send a message with a length prefix
def send_message(sock, data):
    message = struct.pack(MSGPREFIX, len(data)) + data
    sock.sendall(message)


# Read exactly n bytes from the socket
def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


# Read a message with a length prefix
def recv_message(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack(MSGPREFIX, raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


# Listen to a socket for put requests. Each put request contains an arbitrary
# amount of data. Generate a key for each request, insert the data, and return
# the key.
def handle_put(conn: socket.socket) -> None:
    db = get_db_connection()
    cursor = db.cursor()
    try:
        while True:
            # Receive the value to be stored
            value = recv_message(conn)
            if value is None:
                break
            
            try:
                # Insert the value into the database
                cursor.execute("INSERT INTO kv_store (value) VALUES (?)", (value,))
                db.commit()
                
                # Get the auto-generated key (id)
                key = cursor.lastrowid
                
                # Send the key back to the client
                send_message(conn, str(key).encode())
            except sqlite3.Error as e:
                # If there's a database error, send an error message
                send_message(conn, f"Database error: {str(e)}".encode())
    finally:
        db.close()


# Listen to a socket for get requests. Each get request contains a key. The key
# should have be one of the keys previously inserted with a put request. If the
# key does not exist, return an error. Otherwise, full the data blob and send it
# back to the client.
def handle_get(conn: socket.socket) -> None:
    db = get_db_connection()
    cursor = db.cursor()
    try:
        while True:
            key = recv_message(conn)
            if key is None:
                break
            try:
                key_int = int(key.decode())
                cursor.execute("SELECT value FROM kv_store WHERE id = ?", (key_int,))
                result = cursor.fetchone()
                if result:
                    send_message(conn, result[0])
                else:
                    send_message(conn, b"Key not found")
            except ValueError:
                send_message(conn, b"Invalid key format")
    finally:
        db.close()


def accept_connections(sock: socket.socket, handler: callable) -> None:
    while True:
        conn, _ = sock.accept()
        threading.Thread(target=handler, args=(conn,)).start()


## Main Function
def main():
    setup_sqlite()
    
    put_socket = create_socket(PUT_SOCKET_PATH)
    get_socket = create_socket(GET_SOCKET_PATH)
    
    put_thread = threading.Thread(target=accept_connections, args=(put_socket, handle_put))
    get_thread = threading.Thread(target=accept_connections, args=(get_socket, handle_get))
    
    put_thread.start()
    get_thread.start()
    
    try:
        put_thread.join()
        get_thread.join()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        put_socket.close()
        get_socket.close()
        os.unlink(PUT_SOCKET_PATH)
        os.unlink(GET_SOCKET_PATH)
        os.unlink(DB_PATH)

if __name__ == "__main__":
    main()
