# Pymicro-flask

> Python micro web service using uwsgi and flask, with prometheus metrics<br/>

Pymicro-flask accepts POST requests with json format data and return with json format result.<br/>

# APIs
* Service: `http://HOST:8080/microservice`
* Prometheus:
    * when PYMICRO_SEND_METRICS=true, `http://HOST:9102/metrics`
    * when PYMICRO_SEND_METRICS=false, `http://HOST:8080/metrics`

## API Query Example
process logic in [`pymicro_flask/msg_handler.py`](pymicro_flask/msg_handler.py)

```bash
$ curl -X POST -d '{"hello":"pymicro-flask"}' http://HOST:8080/microservice
{
    "pymicro.s_time":"1582092922.6149724",
    "pymicro.e_time":"1582092924.6151698",
    "pymicro.ret":0,
    "hello":"pymicro-flask"
}
```

## Start Service
```bash
$ cd pymicro-flask
$ docker-compose -f docker/docker-compose.yml up -d
```

## ENV Config
* check env setting in [`docker/docker-compose.yml`](docker/docker-compose.yml)
```ini
# Dirpath to temporarily store pdf files
PYMICRO_DATADIR=/tmp

# Server config (default: "http://0.0.0.0:8080")
PYMICRO=http://0.0.0.0:8080

# How many reuquests can be handled concurrently (defulat: 4)
PYMICRO_CONCURRENCY=4

# Timeout for pymicro service (default: 60s)
PYMICRO_TIMEOUT=60

# If sending metrics to statsd server (default: false)
PYMICRO_SEND_METRICS=true

# Statsd server config (default: http://0.0.0.0:9125)
# Used when PYMICRO_SEND_METRICS=true
PYMICRO_STATSD=http://pymicro-metrics:9125

# Log level for pymicro (default: INFO)
PYMICRO_LOGLEVEL=WARN

# Log config file for pymicro (default: "conf/logging_config.ini")
PYMICRO_LOGCONFIG=<path to your log config file>
```

# Prometheus Metrics
Metric update logic: [`pymicro_flask/server/metrics.py`](pymicro_flask/server/metrics.py).<br/>

----------

## metrics
* `pymicro_req_total` (counter) The total counts of requests
* `pymicro_ret_req_total{pymicro_ret}` (counter) The total counts of different ret code requests

# Pymicro Service
## How to run in local
* requirements: `python>=2.7, >=3.6`
* if using `virtualenv` for python, make sure commands below is running within venv.
```shell
$ cd pymicro-flask
$ export PYMICRO_DATADIR=<path to temporarily hold pdf files>
$ ./run_build.sh
$ pymicro_uwsgi
```

## Config
default configs are in `conf/`
* `conf/service.toml`
    * default config of pymicro service, such as server config, statsd server config, ...
* `conf/logging_config.ini`
    * default log config of pymicro service, can be override by `$PYMICRO_LOGCONFIG`
    * log level can be override by `$PYMICRO_LOGLEVEL`(default:`INFO`) without override log config file
* `conf/uwsgi.ini`
    * default uwsgi config, define such as master node, workers num, app callable, ...
    * `process` parameter which can control the number of uwsgi workers can be override by `$PYMICRO_CONCURRENCY`(default: `4`)


## Bin executable
Service executables are in [`bin/`](bin/). After running [`run_build.sh`](run_build.sh), executables would be copyed to system executable path. (defined by `scripts` parameter in [`setup.py`](setup.py))
```
$ which pymicro_server
/usr/local/bin/pymicro_server

$ which pymicro_uwsgi
/usr/local/bin/pymicro_uwsgi
```

### [`pymicro_uwsgi`](bin/pymicro_uwsgi)
> bash script

The script parses envs and config [`conf/uwsgi.ini`](conf/uwsgi.ini) which let uwsgi knows where flask callable is. Finally, invoke uwsgi command below to start uwsgi service.
```bash
uwsgi --ini $(which pymicro_server)/conf/uwsgi.ini
```
flask related config in  [`conf/uwsgi.ini`](conf/uwsgi.ini)
```ini
# let uwsgi call pymicro_server
file = @(exec://which pymicro_server)
# pymicro_uwsgi will set $PYMICRO_CALLABLE based on $PYMICRO_SEND_METRICS. DO NOT set it yourself
callable = $(PYMICRO_CALLABLE)
```

### [`pymicro_server`](bin/pymicro_server)
> python script

It's being invoked by [`pymicro_uwsgi`](bin/pymicro_uwsgi). However, it can be run directly to start flask service without uwsgi.<br/>
It's useful for testing application logic.

## Debug Log
Defined in [`conf/logging_config.ini`](conf/logging_config.ini). Only one handler to output pymicro logs to `stdout` in default logging config.
It you need to change logging setting (e.g., add handlers), you can either
1. Modify [`conf/logging_config.ini`](conf/logging_config.ini)
2. Replace the whole logging config file by setting `$PYMICRO_LOGCONFIG` to the path of your `logging_config.ini`

## Tests
`./run_tests.sh` will run the tests with coverage and term missing.
