# CGI->FCGI Explore

В данном репозитории рассматривается CGI/FCGI и его реализация в Apache - CGI/CGID/FastCGI/FCGID.

## CGI (Common Gateway Interface)

CGI (Common Gateway Interface) — это протокол, по которому веб-сервер может передавать запрос от клиента скрипту и получать ответ.

### Как работает CGI:

- Apache Worker форкается и выполняет указанный в запросе скрипт.

#### Пример:

```bash
curl http://172.20.138.4:8080/cgi-bin/env
```

На сервере увидим следующую ситуацию:

```bash
root@44a413dfa6b3:/usr/local/apache2# ps -ef
UID          PID    PPID  C STIME TTY          TIME CMD
root           1       0  0 15:19 pts/0    00:00:00 httpd -DFOREGROUND
www-data       8       1  0 15:19 pts/0    00:00:00 httpd -DFOREGROUND
www-data       9       1  0 15:19 pts/0    00:00:00 httpd -DFOREGROUND
www-data      10       1  0 15:19 pts/0    00:00:00 httpd -DFOREGROUND
root          92       0  0 15:19 pts/1    00:00:00 bash
www-data      98      10  0 15:19 pts/0    00:00:00 /usr/bin/sh /usr/local/apache2/cgi-bin/env <-- наш cgi скрипт, который форкнул Apache
www-data      99      98  0 15:19 pts/0    00:00:00 sleep 10 <-- часть скрипта. нужна чтобы увидеть процесс в дереве процессов, иначе просто быстро выполняется
www-data     100       1  0 15:19 pts/0    00:00:00 httpd -DFOREGROUND
root         128      92  0 15:19 pts/1    00:00:00 ps -ef
```

### Конфигурация

Рабочий файл конфигурации: `httpd.conf_cgi`

Запустить можно так:

```bash
docker run --name test -v $(pwd)/cgi-bin:/usr/local/apache2/cgi-bin  -v $(pwd)/httpd.conf_cgi:/usr/local/apache2/conf/httpd.conf -it --rm -p 8080:80 httpd:latest
```
> Образ билдится из Dockerfile файла

Документация: [Apache модуль CGI](https://httpd.apache.org/docs/current/mod/mod_cgi.html)

Необходимые для запуска директивы конфига:

```
ScriptAlias /cgi-bin/ "/usr/local/apache2/cgi-bin/"
LoadModule cgi_module modules/mod_cgi.so
```

Для запуска скриптов ничего не нужно. Можно запустить обычный bash скрипт.

Пример скрипта: `cgi-bin/env`

## CGID - демон

CGID слушает на сокете. Отличается от CGI только тем, что процессы форкает не Apache, а демон, который форкает процессы с запускаемыми скриптами и слушает на сокете.

### Конфигурация

Добавляется директива:

```
ScriptSock /var/run/cgid.sock
```

Собственно сокет на сервере:

```bash
root@c5b9d45772b5:/usr/local/apache2# ls -la /var/run/cgid.sock.1
srwx------ 1 www-data root 0 Jul 15 15:25 /var/run/cgid.sock.1
```

Документация: [Apache модуль CGID](https://httpd.apache.org/docs/current/mod/mod_cgid.html)

### Сравнение с CGI:

- Использует сокет для соединения.
- Также на каждый запрос запускает скрипт.
- Судя по документации, снижен оверхед при создании форка процесса со скриптом благодаря демону, т.к. когда форкает сам Apache, то копируются все потоки (threads) процесса воркера, что создает оверхед. А демон работает обособленно, и создает "чистые" форки процессов только с нужным окружением.

Рабочий файл конфигурации: `httpd.conf_cgid`

Для запуска скриптов ничего не нужно. Можно запустить обычный bash скрипт.

Пример скрипта: `cgi-bin/env`

## FCGID

Дальнейшее развитие CGID. Также слушает на сокете.

При старте веб-сервера, запускает определенное в параметре конфига число скриптов, которые будут обрабатывать запросы.
1 скрипт - 1 запрос.
Для написания скрипта нужны соответствующие библиотеки.

### Сравнение с CGID:

- Может запускаться удаленно, и быть доступен по TCP/IP (именно сам протокол. В конфиге Apache просто создается сокет, к которому обращается веб-сервер. Как такового URL до сервера FCGI указать нельзя).
- Запускает одновременно несколько скриптов.
- После выполнения 1 запроса, скрипт не закрывается, в отличие от CGID, а обрабатывает новый запрос.
- Скрипты работают параллельно только с 1 запросом.

Конфигурационный файл: `httpd.conf_fcgid`
Пример скрипта: `cgi-bin/while.c` (while.fcgi - скомпилированный)

## FastCGI

Основное отличие этого модуля от FCGID - многопоточность.
В скриптах или приложениях можно реализовать многопоточность, и 1 скрипт сможет обрабатывать множество запросов одновременно.

### Основное отличие от FCGID:

- Многопоточность

Конфигурационный файл: `httpd.conf`
Пример скрипта: `cgi-bin/async.c` (async.fcgi)

# Тестирование
Варианты fcgid/fastcgi можно протестировать через http_load(бинарник в репе).
варианты тестировани тут есть https://stackoverflow.com/questions/5829869/multi-threaded-fastcgi-app


fcgi спецификация - https://www.mit.edu/~yandros/doc/specs/fcgi-spec.html
перевод - https://docs.google.com/document/d/1mPZXERcJ_ouG5H0ZDqP_Fg2NXgfUvHJOKCD8F61xf5w/edit
