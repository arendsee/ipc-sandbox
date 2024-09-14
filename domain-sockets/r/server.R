dyn.load("socketr.so")

main <- function(socket_path) {
  # Setup a new server that uses a given path for the socket address
  server_fd <- .Call("R_new_server", socket_path)

  if (server_fd == -1) {
    cat("Error creating server\n")
    return(1)
  }

  # Listen for clients
  tryCatch({
    while (TRUE) {
      # Accept a connection from the top available client
      client_fd <- .Call("R_accept_client", server_fd)
      if (client_fd == -1) {
        cat("Error accepting connection\n")
        next
      }

      # Pull data from the client
      data <- .Call("R_get", client_fd)

      # If any data was pulled, operate on it
      if (data[[2]] > 0) {
        # Do some work on the data if desired
        # For now, we'll just echo it back

        # Return the result to the client
        .Call("R_send_data", client_fd, data)
      }

      # Close the current client
      .Call("R_close_socket", client_fd)
    }
  }, finally = {
    # Close the server
    .Call("R_close_socket", server_fd)

    # Remove the socket file
    unlink(socket_path)
  })

  # Exit with success
  return(0)
}


args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) {
  cat("Usage: Rscript script.R <socket_path>\n")
  quit(status = 1)
}

socket_path <- args[1]
result <- main(socket_path)
quit(status = result)
