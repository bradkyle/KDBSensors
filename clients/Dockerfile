FROM ubuntu:18.04 as deps 

# Install kdb+
RUN \
	apt-get update && \
	apt-get install -y curl rlwrap unzip gcc-multilib g++-multilib make build-essential 

# Basic build tools
# RUN apt-get -y install gcc
# RUN apt-get -y install g++
# RUN apt-get -y install cmake
# RUN apt-get -y install make
# RUN apt-get -y install vim
# RUN apt-get -y install wget
# RUN apt-get -y install dos2unix

# # Required to build protobuf
# RUN apt-get -y install git
# RUN apt-get -y install autoconf
# RUN apt-get -y install automake
# RUN apt-get -y install libtool

RUN apt-get clean all

FROM deps as kdbbuild 
ENV QHOME /q
ENV PATH ${PATH}:${QHOME}/l32/

ADD q32.zip . 
RUN unzip q32.zip && \
	rm q32.zip && \
	alias q='rlwrap q' # Ensure we have your our zipped version of q for linux 

FROM kdbbuild as prombuild 
ENV QHOME /q
ENV QOST=l
ENV QMACH=32
ENV PATH ${PATH}:${QHOME}/l32/
ADD prometheuskdb prometheuskdb

RUN cd prometheuskdb && chmod +x install.sh && ./install.sh

FROM prombuild as kafkabuild 
ENV QHOME /q
ENV PATH ${PATH}:${QHOME}/l32/
add librdkafka librdkafka

# TODO add -lssl -lz
RUN cd librdkafka && \
    make clean && \
    ./configure --prefix=$HOME --disable-sasl --disable-lz4 --mbits=32 && \
    make && \
    make install 

ADD kafka kafka
# TODO add openssl, zlib
RUN cd kafka && \
		curl -s -O -L https://github.com/KxSystems/kdb/raw/master/c/c/k.h && \ 
		cc kfk.c -m32 -DKXVER=3 -shared -fPIC -Wall -Wno-strict-aliasing -Wno-parentheses -Wextra -Werror -Wsign-compare -L /root/lib/ -lrdkafka -lpthread -g -O2 -I /root/include -lrt -o libkfk.so && \
    install libkfk.so ${QHOME}/l32 && \
    make clean


FROM continuumio/miniconda3 AS anaconda
FROM kafkabuild as srcbuild

COPY --from=anaconda /opt/conda /opt/conda

RUN . /opt/conda/etc/profile.d/conda.sh \
	&& conda update -n base conda \
	&& conda clean -y --all

COPY docker/profile.sh /etc/profile.d/kx.sh

USER kx

RUN . /opt/conda/etc/profile.d/conda.sh \
	&& conda create -y -n kx python=3 --no-default-packages \
	&& conda install -n kx -c jmcmurray qutil ws-client ws-server req -y 

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/root/lib
