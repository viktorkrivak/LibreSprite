FROM debian:bullseye as builder

RUN mkdir -p /root/src
COPY . /root/src
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y git cmake g++ libcurl4-gnutls-dev libfreetype6-dev libgif-dev libgtest-dev libjpeg-dev liblua5.4-dev libpixman-1-dev libpng-dev libsdl2-dev libsdl2-image-dev libtinyxml-dev libnode-dev ninja-build zlib1g-dev
RUN cd /root/src && git submodule update --init --recursive
RUN mkdir -p /root/build && cd /root/build && cmake /root/src
RUN cd /root/build && make libresprite

FROM debian:bullseye-slim
RUN mkdir -p /opt/libresprite && apt-get update && \
DEBIAN_FRONTEND=noninteractive apt-get --no-install-recommends -y install libcurl3-gnutls libxcb1 libsdl2-2.0-0 libsdl2-image-2.0-0 libpixman-1-0 libtinyxml2.6.2v5 libgif7 liblua5.4-0 libnode72 libfreetype6 python3-minimal python3-flask
COPY docker/server.py /opt/server.py
COPY --from=builder /root/build/bin/libresprite /opt/libresprite
COPY --from=builder /root/build/bin/data /opt/libresprite/data
ENV FLASK_APP=/opt/server.py
CMD flask run --host=0.0.0.0
#RUN mkdir -p /opt/libresprite/data
#RUN apt-get update && apt-get install libcurl3-gnutls libxcb1 libsdl2-2.0-0 libsdl2-image-2.0-0 libpixman-1-0 libtinyxml2.6.2v5 libgif7 liblua5.4-0 libnode72 libfreetype6
#COPY ../build/bin/libresprite /opt/libresprite
#COPY ../build/bin/libresprite/data /opt/libresprite/data/gui.xml
