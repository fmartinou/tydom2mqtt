FROM python:3.8-slim-buster
COPY . /data
WORKDIR /data
RUN pip3 install -r requirements.txt

# add s6-overlay
RUN tar xzf /tmp/s6-overlay-amd64.tar.gz -C / --exclude="./bin" && \
    tar xzf /tmp/s6-overlay-amd64.tar.gz -C /usr ./bin

RUN DEBIAN_FRONTEND=noninteractive apt-get update -yqq > /dev/null && \
    apt-get install -yqq --no-install-recommends unzip          \
                                                 libuv1-dev     \
                                                 libssl1.0-dev  \
                                                 libc-dev       \
                                                 gcc            \
                                                 curl           \
                                                 > /dev/null && \
    apt-get -y autoclean




CMD [ "python", "-u", "./main.py" ]