import os
import select
import traceback
import time
import sys

def create_pipe(pipe_path):
    if not os.path.exists(pipe_path):
        os.mkfifo(pipe_path)

def execute_command(command):
    try:
        exec(command, globals())
    except Exception as e:
        print(f"Error executing command: {e}")
        print(traceback.format_exc())

def main():
    pipepath = sys.argv[1]
    create_pipe(pipepath)
    
    with open(pipepath, 'r') as pipe_file:
        readable = [pipe_file]
        
        while True:
            ready, _, _ = select.select(readable, [], [], 0.1)

            # Without this sleep step, an entire CPU will be 100% used
            time.sleep(0.001)

            if ready:
                command = pipe_file.readline().strip()
                if command:
                    if command.lower() == 'exit':
                        print("Exiting...")
                        break
                    execute_command(command)
            else:
                # This branch was never entered in my experience
                print("!", end="")
                # No data available, sleep briefly to reduce CPU usage
                time.sleep(0.001)


if __name__ == "__main__":
    main()
