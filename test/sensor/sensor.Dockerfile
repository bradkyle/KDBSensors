FROM kdb32
COPY sensor.q .
CMD q producer.q -p 8080