# Ubuntu Python 3
FROM ubuntu:latest

WORKDIR /root

# Install dependences 

RUN apt-get update; \ 
    apt-get install -qy \
    iputils-ping \
    net-tools \
    python3 \
    python3-pip \
    python3-venv \
    vim \
    git; \
    rm -rf /tmp/* /var/tmp/* /var/lib/{apt,dpkg,cache,log}/

CMD ["/bin/bash"]