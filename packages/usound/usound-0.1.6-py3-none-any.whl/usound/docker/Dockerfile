#{FROM}

ARG MKUSER

#{COPY_CMDBOX}
#{COPY_USOUND}
#{COPY_USOUND_START}

RUN groupadd ${MKUSER} && \
    useradd -m -g ${MKUSER} -s /usr/bin/bash ${MKUSER} && \
    cp /etc/skel/.bash_logout /home/${MKUSER}/ && \
    cp /etc/skel/.bashrc /home/${MKUSER}/ && \
    cp /etc/skel/.profile /home/${MKUSER}/
RUN chown -R ${MKUSER}:${MKUSER} /home/${MKUSER}
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo
RUN apt-get update && \
    apt-get install -y libgl1-mesa-dev libglib2.0-0 git wget
#{INSTALL_PYTHON}
RUN apt-get install -y pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl build-essential libopencv-dev && \
    apt-get install -y iputils-ping net-tools
RUN apt-get install -y pulseaudio libpulse0 ffmpeg portaudio19-dev && \
    adduser root pulse-access && \
    pulseaudio --verbose --exit-idle-time=-1 --system --disallow-exit -D > /dev/null 2>&1
RUN pip install --upgrade pip && \
    pip install xmlsec==1.3.13 python3-saml && \
    pip install #{INSTALL_CMDBOX} && cmdbox --version && \
    pip install #{INSTALL_USOUND} && usound --version
#{INSTALL_CTRANSLATE2}
RUN mkdir -p /home/${MKUSER}/.usound && chown -R ${MKUSER}:${MKUSER} /home/${MKUSER}/.usound

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=password
ENV SVNAME=server#{INSTALL_TAG}
ENV MKUSER=${MKUSER}
ENV LISTEN_PORT=8081
ENV SVCOUNT=${SVCOUNT}

CMD bash /home/${MKUSER}/scripts/start.sh
