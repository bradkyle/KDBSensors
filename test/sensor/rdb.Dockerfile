FROM kdb32
COPY rdb.q .
CMD q rdb.q