set -x

DATA='{"hello":"pymicro-flask"}'
GET=$(curl -d "$DATA" -s $PYMICRO/microservice)

RET_CODE=$(echo $GET | python -c "import sys, json; print(json.load(sys.stdin)['pymicro.ret'])")
[[ $RET_CODE == 0 || $RET_CODE == -1 ]]


if [ "$PYMICRO_SEND_METRICS" = "true" ]; then
    METRICS=$(curl -s $PYMICRO_STATSD_WEB/metrics | grep -i pymicro_)
    UWSGI_METRICS=$(curl -s $PYMICRO_STATSD_WEB/metrics | grep -i uwsgi_pymicro_)
    [[ ! -z "$METRICS" ]]
    [[ ! -z "$UWSGI_METRICS" ]]
else
    METRICS=$(curl -s $PYMICRO/metrics | grep -i pymicro_)
    [[ ! -z "$METRICS" ]]
fi
