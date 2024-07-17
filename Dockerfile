FROM httpd:2.4
RUN apt update && apt-get install libapache2-mod-fcgid libcgi-fast-perl procps wget -yqq
RUN wget https://mirrors.edge.kernel.org/ubuntu/pool/multiverse/liba/libapache-mod-fastcgi/libapache2-mod-fastcgi_2.4.7~0910052141-1.2_amd64.deb && \
    dpkg -i libapache2-mod-fastcgi_2.4.7~0910052141-1.2_amd64.deb

RUN mkdir /var/lib/apache2/fastcgi/dynamic && chmod 777 -R /var/lib/apache2/fastcgi
