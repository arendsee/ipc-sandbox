dyn.load("socketr.so")

# Number of seconds to wait during each loop
LISTENER_TICK = 0.001

# Number of seconds to listen to the pipe during each loop
ACCEPT_READ_TIME = 0.0001

# The parallelism strategy (see documentation for the R `future` package)
# NOTE: This will not work on Windows, but it is the fastest option for local
# compute on a UNIX machine
future::plan(future::multicore)

processMessage <- function(data){
  # simulate work
  cat("Starting:", rawToChar(data[[1]][0:data[[2]]]), "\n")
  Sys.sleep(10)
  cat("Finished:", rawToChar(data[[1]][0:data[[2]]]), "\n")
  data
}

check_for_new_client <- function(queue, server_fd){
  # Accept a connection from the top available client if one exists
  client_fd <- .Call("R_accept_client", server_fd, ACCEPT_READ_TIME)

  if (client_fd == -1) {
    # An error occurred, don't worry about it
    return(queue)
  } else if (client_fd == -2) {
    # A timeout occurred, certainly don't worry about
    return(queue)
  }

  # Pull data from the client
  data <- .Call("R_get", client_fd)

  # If any data was pulled, operate on it
  if (data[[2]] > 0) {

    print(paste("job", length(queue)+1, "starts"))
    # Run the job in a newly forked process in the backgroun
    work <- future::future({ processMessage(data) })

    # Add the job to the queue
    queue[[length(queue)+1]] <- list( client_fd = client_fd, data = data, work = work)

  }

  queue
}

job_has_finished <- function(job){
  future::resolved(job$work) 
}

handle_finished_client <- function(job){
  # get the result of the calculation
  result <- future::value(job$work)

  # Return the result to the client
  .Call("R_send_data", job$client_fd, result)

  # Close the current client
  .Call("R_close_socket", job$client_fd)
}

main <- function(socket_path) {
  # Setup a new server that uses a given path for the socket address
  server_fd <- .Call("R_new_server", socket_path)

  if (server_fd == -1) {
    cat("Error creating server\n")
    return(1)
  }

  queue <- list()

  # Listen for clients
  tryCatch({
    while (TRUE) {
      queue <- check_for_new_client(queue, server_fd)

      job_idx = 1
      while(job_idx <= length(queue)){
        # check is the job has finished
        if(job_has_finished(queue[[job_idx]])){
          print(paste("job", job_idx, "is finished"))

          # send data back to the client and close the socket
          handle_finished_client(queue[[job_idx]])

          # remove this completed job from the queue
          # job_idx will now point to the next job
          queue[[job_idx]] <- NULL
        } else {
          # if this job is still running, move onto the next one
          job_idx <- job_idx + 1
        }
      }

      # sleep to avoid busy waiting
      Sys.sleep(LISTENER_TICK)
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
