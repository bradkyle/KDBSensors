FROM kdb32
COPY sensor.q .
CMD q sensor.q