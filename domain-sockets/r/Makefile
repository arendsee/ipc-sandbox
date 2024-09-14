all:
	R CMD SHLIB socketr.c

server:
	Rscript server.R pipe

client:
	Rscript client.R pipe "hi"

clean:
	rm -f socketr.so socketr.o pipe
