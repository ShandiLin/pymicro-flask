From python:3.8-alpine

# install pymicro_flask
ENV PYMICRO_UWSGI_PLUGIN_DIR "/usr/local/lib/uwsgi_plugins"

ADD . /pymicro_flask/
WORKDIR /pymicro_flask

# install dependencies: bash, uwsgi
# libuuid and pcre-dev for 'uwsgi' package
RUN apk add --update --no-cache --no-cache bash libuuid libcap pcre

# build pymicro_flask
# uwsgi dogstasd plugin: linux-headers libcap-dev openssl-dev pcre-dev zlib-dev git
RUN apk add --no-cache --virtual .build-deps gcc musl-dev g++ \
    libc-dev linux-headers openssl-dev pcre-dev libcap-dev zlib-dev git && \
    ./run_build.sh &&  \
    apk del .build-deps

# default command
CMD ["pymicro_uwsgi"]
