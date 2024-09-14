## Create named pipe
fifo_path <- "roo"
if (!file.exists(fifo_path)) {
  system(paste("mkfifo", fifo_path))
}

## Function to evaluate code and capture output
evaluate_code <- function(code) {
  eval(parse(text = code), envir = .GlobalEnv)
}

# WARNING: This will sometimes skip lines
# I have not found a solution that doesn't
isdone = FALSE
while (!isdone) {
  Sys.sleep(0.0001)
  con <- file(fifo_path, "r")
  open(con)
  for (line in readLines(con)){
    evaluate_code(line)
  }
  close(con)
}
