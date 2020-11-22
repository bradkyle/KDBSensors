FROM kdb32
COPY tick.q .
CMD q tick.q