#ifndef __SOCKET_H__
#define __SOCKET_H__

#include <sys/socket.h>
#include <iostream>
#include <cstring>
#include <sys/un.h>
#include <unistd.h>

#define BUFFER_SIZE 1024

struct Message {
    char data[BUFFER_SIZE];
    size_t length;
};

// Create a Unix domain socket
int new_socket(){
    int socket_fd = socket(AF_UNIX, SOCK_STREAM, 0);

    // AF_UNIX: Unix domain socket - other possibilities include:
    //  * AF_INET: For IPv4 Internet protocols - with SOCK_STREAM for TCP or
    //             with SOCK_DGRAM for UDP
    //  * AF_INET6: For IPv6 Internet protocols
    //  * AF_NETLINK: For kernel user interface device
    //  * AF_PACKET: For low-level packet interface

    // SOCK_STREAM - a stream socket that provides two-way, connection-based communication
    //  Alternatives include:
    //  * SOCK_DGRAM: For datagram (connectionless) sockets
    //  * SOCK_RAW: For raw network protocol access
    //  * SOCK_SEQPACKET: For sequential, reliable, connection-based packet streams
    
    // The 3rd argument, 0, is the protocol. For domain sockets there is only
    // one protocol, so this is always 0.

    if (socket_fd == -1) {
        std::cerr << "Error creating socket\n";
        return 1;
    }

    return socket_fd;
}

struct sockaddr_un new_server_addr(const char* SOCKET_PATH){
    // Set up the server address structure
    struct sockaddr_un server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sun_family = AF_UNIX;
    strncpy(server_addr.sun_path, SOCKET_PATH, sizeof(server_addr.sun_path) - 1);
    return server_addr;
}

int new_server(const char* SOCKET_PATH){

    int server_fd = new_socket();

    struct sockaddr_un server_addr = new_server_addr(SOCKET_PATH);

    // Remove any existing socket file
    unlink(SOCKET_PATH);

    // Bind the socket to the address
    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        std::cerr << "Error binding socket\n";
        close(server_fd);
        return 1;
    }

    // Listen for connections
    if (listen(server_fd, 1) == -1) {
        std::cerr << "Error listening on socket\n";
        close(server_fd);
        return 1;
    }

    return server_fd;
}

int accept_client(int server_fd){
    // Accept a connection
    int client_fd = accept(server_fd, nullptr, nullptr);
    return client_fd;
}

Message get(int client_fd){
    struct Message result;
    result.length = recv(client_fd, result.data, BUFFER_SIZE, 0);
    return result;
}

void send_data(int client_fd, const Message& msg){
  send(client_fd, msg.data, msg.length, 0);
}

void close_socket(int socket_fd){
  close(socket_fd);
}


Message ask(const char* socket_path, const Message& message){
    struct Message result;
    result.length = 0;

    int client_fd = new_socket();

    struct sockaddr_un server_addr = new_server_addr(socket_path);

    // Connect to the server
    if (connect(client_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        close(client_fd);
        return result;
    }

    // Send a message
    send(client_fd, message.data, message.length, 0);

    // Receive response
    result.length = recv(client_fd, result.data, BUFFER_SIZE, 0);

    close(client_fd);

    return result;
}


#endif
