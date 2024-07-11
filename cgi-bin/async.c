#include <fcgi_stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

// Функция для обработки запроса
void* handle_request(void* arg) {
    int count = *((int*)arg);
    free(arg);

    // Отправляем заголовки и тело ответа
    printf("Content-type: text/html\r\n\r\n");
    printf("Hello world!<br>\r\n");
    printf("Request number %d.", count);
    fflush(stdout);

    return NULL;
}

int main(void) {
    int count = 0;

    while (FCGI_Accept() >= 0) {
        pthread_t thread;
        int* count_ptr = malloc(sizeof(int));
        if (count_ptr == NULL) {
            perror("Failed to allocate memory");
            exit(EXIT_FAILURE);
        }
        *count_ptr = count++;

        // Создаем новый поток для обработки запроса
        if (pthread_create(&thread, NULL, handle_request, count_ptr) != 0) {
            perror("Failed to create thread");
            free(count_ptr);
            exit(EXIT_FAILURE);
        }

        // Отсоединяем поток, чтобы не нужно было ожидать его завершения
        pthread_detach(thread);
    }

    return 0;
}
