#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 5050
#define NUM_CHILDREN 10

void send_pid_to_server(int sockfd) {
    pid_t pid = getpid();
    char message[256];
    snprintf(message, sizeof(message), "PID: %d\n", pid);
    send(sockfd, message, strlen(message), 0);
}

int main() {
    struct sockaddr_in server_addr;
    int sockfd;

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr);

    // Connect to server
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("connect");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    // Create child processes
    for (int i = 0; i < NUM_CHILDREN; i++) {
        if (fork() == 0) {
            // Child process
            sleep(10);
            send_pid_to_server(sockfd);
            close(sockfd);
            exit(0);
        }
    }

    // Close the socket in the parent process
    close(sockfd);
    return 0;
}

