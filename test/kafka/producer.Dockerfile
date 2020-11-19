FROM kdb32
COPY producer.q .
CMD q producer.q -p 8080