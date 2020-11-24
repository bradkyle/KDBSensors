FROM kdb32
COPY consumer.q .
CMD q consumer.q