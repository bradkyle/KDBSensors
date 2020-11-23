FROM kdb32
COPY tick.q .
COPY u.q .
COPY sym.q .
CMD q tick.q