#include <iostream>
#include <iomanip>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <cstring>

#include "socket.h"

void print_message(struct Message msg) {
    std::cout << std::hex << std::setfill('0');
    for (size_t i = 0; i < msg.length; ++i) {
        std::cout << std::setw(2) << (static_cast<unsigned int>(static_cast<unsigned char>(msg.data[i])) & 0xFF) << " ";
    }
    std::cout << std::dec << std::endl;  // Reset to decimal mode
}

size_t str_size(const char* str){
  size_t size = 0;
  while(str[size] != '\0') size++;
  size++; // plus for the null
  return size;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <socket_path> <message>\n";
        return 1;
    }

    const char* socket_path = argv[1];
    const char* message_str = argv[2];

    struct Message message;
    message.length = str_size(message_str);
    std::memcpy(message.data, message_str, BUFFER_SIZE);

    struct Message result = ask(socket_path, message);

    print_message(result);

    return 0;
}
