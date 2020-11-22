FROM kdb32
COPY hdb.q .
CMD q hdb.q