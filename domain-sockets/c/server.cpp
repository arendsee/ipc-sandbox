#include <iostream>

#include "socket.h"

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <socket_path>\n";
        return 1;
    }
    const char* SOCKET_PATH = argv[1];

    // setup a new server that uses a given path for the socket address
    int server_fd = new_server(SOCKET_PATH);

    // listen for clients
    while (true) {

        // accept a connection from the top available client
        int client_fd = accept_client(server_fd);
        if (client_fd == -1) {
            std::cerr << "Error accepting connection\n";
            continue;
        }

        // pull data from the client
        Message data = get(client_fd);

        // if any data was pulled, operate on it
        if(data.length > 0){

            // do some work on the data if desired
  
            // return the result to the client
            send_data(client_fd, data);
        }

        // close the current client
        close_socket(client_fd);
    }

    // close the server
    close_socket(server_fd);

    // remove the socket file
    unlink(SOCKET_PATH);

    // exit with success
    return 0;
}
