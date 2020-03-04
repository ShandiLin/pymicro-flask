FROM python:3.8-alpine

RUN apk add bash curl
COPY test/test.sh /

ENTRYPOINT ["/bin/bash", "/test.sh"]
