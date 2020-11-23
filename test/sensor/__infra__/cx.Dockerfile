FROM kdb32
COPY cx.q .
COPY u.q .
CMD q cx.q