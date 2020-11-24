FROM kdb32
COPY producer.q .
CMD q producer.q