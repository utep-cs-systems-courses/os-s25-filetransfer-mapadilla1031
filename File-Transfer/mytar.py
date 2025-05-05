#marko padilla OS 4375 Version 1.3 updated
#!/usr/bin/env python3
import os
import sys

def c_archive(files):
    # Create archive and write to std output
    stdout_fd = 1  # standard output

    for file_path in files:
        file_fd = os.open(file_path, os.O_RDONLY)
        file_stat = os.fstat(file_fd)
        file_size = file_stat.st_size
        filename_bytes = file_path.encode('utf-8')
        filename_length = len(filename_bytes)
        # os.write header info: filename length 6 bytes, filename, file size 6 bytes
        os.write(stdout_fd, ("%06d" % filename_length).encode('ascii')) #Write filename length as 6 byte ASCII string with zero such as 000012
        os.write(stdout_fd, filename_bytes)
        os.write(stdout_fd, ("%06d" % file_size).encode('ascii'))
        # Write file content in chunks/parts
        while True:#buffered reader
            chunk = os.read(file_fd, 10000)  # read it in parts
            if not chunk:
                break
            os.write(stdout_fd, chunk)
        os.close(file_fd)

def x_archive():
    # Extract files from archive, read from standard input
    stdin_fd = 0  # standard input
    while True:
        # Read filename len 6 bytes
        len_bytes = os.read(stdin_fd, 6)
        if not len_bytes or len(len_bytes) < 6:  # End of archive
            break
        
        filename_len = int(len_bytes.decode('ascii'))
        filename_bytes = os.read(stdin_fd, filename_len)
        filename = filename_bytes.decode('utf-8')
        size_bytes = os.read(stdin_fd, 6)# read file size 6 bytes.
        file_size = int(size_bytes.decode('ascii'))
        # create and open output file.
        file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
        # Read and write file content in parts until file size 
        bytes_remaining = file_size
        while bytes_remaining > 0:
            bytes_to_read = min(10000, bytes_remaining)
            chunk = os.read(stdin_fd, bytes_to_read)
            if not chunk:
                break
            os.write(file_fd, chunk)
            bytes_remaining -= len(chunk)
        os.close(file_fd)

def main():
    mode = sys.argv[1]  # mode c or x

    if mode == 'c':  # create archive
        if len(sys.argv) < 3:
            sys.exit(1)  # Exit if there are no files for archiving
        c_archive(sys.argv[2:])
    elif mode == 'x':  # extract archive
        x_archive()
    else:
        sys.exit(1)  # else just exit

if __name__ == "__main__":
    main()
    