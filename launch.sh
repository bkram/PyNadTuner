#!/bin/sh

if [ -z "${TUNER_PORT}" ]; then
    TUNER_PORT=/dev/ttyUSB0
fi

echo Starting WebTuner on serial port "${TUNER_PORT}"
python3 WebTuner.py
