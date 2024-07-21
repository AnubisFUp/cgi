#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define PATH_MAX 4096
#define PORT 5555
#define BACKLOG 10

void print_fd_table() {
    char fd_path[PATH_MAX];
    char link_path[PATH_MAX];
    ssize_t link_len;
    DIR *dir;
    struct dirent *entry;

    // Get the PID of the current process
    pid_t pid = getpid();
    snprintf(fd_path, sizeof(fd_path), "/proc/%d/fd", pid);

    // Open the directory
    dir = opendir(fd_path);
    if (!dir) {
        perror("opendir");
        exit(EXIT_FAILURE);
    }

    printf("File Descriptor Table for PID %d:\n", pid);
    printf("%-10s %-10s %-10s\n", "FD", "Mode", "Path");

    // Read each entry in the directory
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') {
            continue; // Skip . and ..
        }

        snprintf(fd_path, sizeof(fd_path), "/proc/%d/fd/%s", pid, entry->d_name);
        link_len = readlink(fd_path, link_path, sizeof(link_path) - 1);
        if (link_len == -1) {
            perror("readlink");
            continue;
        }

        link_path[link_len] = '\0'; // Null-terminate the link path

        // Get file descriptor number
        int fd = atoi(entry->d_name);

        // Determine file descriptor mode (read, write, etc.)
        char mode[20] = "UNKNOWN";
        int flags = fcntl(fd, F_GETFL);
        if (flags != -1) {
            if ((flags & O_ACCMODE) == O_RDONLY) strcpy(mode, "READ");
            else if ((flags & O_ACCMODE) == O_WRONLY) strcpy(mode, "WRITE");
            else if ((flags & O_ACCMODE) == O_RDWR) strcpy(mode, "READ/WRITE");
        }

        // Print file descriptor information
        printf("%-10d %-10s %-10s\n", fd, mode, link_path);
    }

    closedir(dir);
}

int create_listening_socket(int port) {
    int sockfd;
    struct sockaddr_in serv_addr;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = INADDR_ANY;
    serv_addr.sin_port = htons(port);

    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("bind");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    if (listen(sockfd, BACKLOG) < 0) {
        perror("listen");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    return sockfd;
}

int main() {
    int sockfd = create_listening_socket(PORT);
    printf("Listening socket created on port %d\n", PORT);

    print_fd_table();

    close(sockfd);
    return 0;
}

