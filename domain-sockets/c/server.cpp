#include <iostream>
#include <unistd.h>
#include <cstring>
#include <vector>
#include <sys/wait.h>
#include <algorithm>

#include "socket.h"

struct Job {
    int client_fd;
    Message message;
    pid_t pid;

    Job(int fd, const Message& msg) : client_fd(fd), message(msg), pid(-1) { }
};

std::vector<Job> children;

void finish_job(const Job& job, const Message& result) {
    // return the result to the client
    send_data(job.client_fd, result);

    // close the current client
    close_socket(job.client_fd);
}


Message do_work(const Message& msg){

    // Simulate some work
    sleep(5);

    // for now, just copy the input message to the output message
    return msg;
}

Message process_job(const Job& job) {
    
    pid_t pid = getpid();
    std::cout << "start job " << pid << std::endl;

    Message result = do_work(job.message); 

    std::cout << "end job " << pid << std::endl;

    return result;
}


void start_new_job(int client_fd) {
    // pull data from the client
    Message data = get(client_fd);

    // store the job info
    Job new_job(client_fd, data);

    // if any data was pulled, operate on it
    if (data.length > 0) {
        pid_t pid = fork();
        if (pid == 0) {
            // Entered by the child process
            // Run the job
            Message result = process_job(new_job);

            // Close the connecction
            finish_job(new_job, result);

            // And kill the child
            exit(0);
        } else if (pid > 0) {
            // Entered by the parent process
            new_job.pid = pid;
            children.push_back(new_job);
        } else {
            std::cerr << "Fork failed\n";
            close_socket(client_fd);
        }
    } else {
        // Close the connection if no data was received
        close_socket(client_fd);
    }
}



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
        // listen for a limited time (100 us) before timing out
        int client_fd = accept_client(server_fd, 0.0001);

        // start a new job if a message was received
        if (client_fd > 0) {
            start_new_job(client_fd);
        }
    }

    // close the server
    close_socket(server_fd);

    // remove the socket file
    unlink(SOCKET_PATH);

    // exit with success
    return 0;
}
