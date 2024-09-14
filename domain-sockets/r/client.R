dyn.load("socketr.so")

# Function to print a message in hexadecimal format
print_message <- function(msg) {
  data <- msg[[1]]
  length <- msg[[2]]
  hex_string <- paste(sprintf("%02x", as.integer(data[1:length])), collapse = " ")
  cat(hex_string, "\n")
}

# Main function
main <- function(socket_path, message_str) {
  message <- list(
    # convert the string to a raw byte sequence
    charToRaw(message_str),
    # the size of the message including null terminator
    as.integer(nchar(message_str) + 1)
  )
  
  # Send the message over the socket and receive the response
  result <- .Call("R_ask", socket_path, message)
  
  print_message(result)
}


args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  cat("Usage: Rscript client.R <socket_path> <message>\n")
  quit(status = 1)
}

socket_path <- args[1]
message_str <- args[2]

main(socket_path, message_str)
