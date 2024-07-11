#include <fcgi_stdio.h>
#include <unistd.h> // Для функции sleep

int main(void) // main должен возвращать int, а не void
{
    int count = 0;
    while(FCGI_Accept() >= 0) {
        printf("Content-type: text/html\r\n");
        printf("\r\n");
        printf("Hello world!<br>\r\n");
        printf("Request number %d.", count++);
        sleep(5); // Добавляем задержку в 60 секунд
    }
    return 0; // Используем return вместо exit
}
