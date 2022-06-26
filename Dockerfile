FROM alpine:latest
LABEL org.opencontainers.image.source=https://github.com/bkram/PyNadTuner
LABEL org.opencontainers.image.description="Nad WebTuner"
ENV PYTHONUNBUFFERED=1

RUN adduser webtuner -D -h /webtuner && addgroup webtuner dialout
COPY launch.sh requirements.txt WebTuner.py /webtuner/
COPY templates/*.html /webtuner/templates/
COPY NadSerial/__init__.py /webtuner/NadSerial/

RUN apk add --no-cache python3 py-pip  && \
    pip install -r /webtuner/requirements.txt

USER webtuner
WORKDIR /webtuner
ENTRYPOINT ["/webtuner/launch.sh"]
