import socket
import sys
import os
import time
import multiprocessing
import select

BUFFER_SIZE = 1024

def message_response(data):
    # simulate work
    time.sleep(5)
    return data

def worker(data, result_queue):
    result = message_response(data)
    result_queue.put(result)

def server(socket_path):
    # Remove the socket file if it already exists
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise

    queue = []

    # Create a Unix domain socket
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(socket_path)
        s.listen(1)
        s.setblocking(False)
        print(f"Server listening on {socket_path}")

        while True:
            # accept a client from the socket with a timeout of 0.0001 seconds
            ready, _, _ = select.select([s], [], [], 0.0001)
            
            if ready:
                conn, addr = s.accept()
                print(f"Connected by {addr}")
                data = conn.recv(BUFFER_SIZE)
                
                if data:
                    print(f"job {str(conn)} started")

                    # start a job with multiprocessing on a new process
                    result_queue = multiprocessing.Queue()
                    p = multiprocessing.Process(target=worker, args=(data, result_queue))
                    p.start()
                    
                    # add the job and connection info to the list queue
                    queue.append((p, conn, result_queue))

            # loop through all jobs in the queue
            for job in queue[:]:  # Create a copy of the list to iterate over
                p, conn, result_queue = job
                if not p.is_alive():

                    # if the job is done, remove it from the queue and sendall data back to the client
                    result = result_queue.get()
                    conn.sendall(result)
                    conn.close()
                    queue.remove(job)
                    p.join()  # Clean up the process

            # sleep for 0.001 seconds
            time.sleep(0.001)

if __name__ == "__main__":
    socket_path = sys.argv[1]
    server(socket_path)
