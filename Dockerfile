FROM alpine:latest
LABEL org.opencontainers.image.source=https://github.com/bkram/PyNadTuner
LABEL org.opencontainers.image.description="Nad WebTuner"
ENV PYTHONUNBUFFERED=1

RUN mkdir /webtuner
COPY launch.sh /
COPY requirements.txt /webtuner
COPY WebTuner.py /webtuner
COPY NadSerial/__init__.py /webtuner/NadSerial/
COPY templates/* /webtuner/templates/

RUN apk add --no-cache python3  py-pip  && \
    pip install --upgrade pip wheel && \
    pip install -r /webtuner/requirements.txt && \
    rm -rf /var/cache/apk/*

WORKDIR /webtuner
ENTRYPOINT ["/launch.sh"]
