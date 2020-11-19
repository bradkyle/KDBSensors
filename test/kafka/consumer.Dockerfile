FROM kdb32
COPY consumer.q .
CMD q consumer.q -p 8080