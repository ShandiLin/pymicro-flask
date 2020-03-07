set -x

DATA='{"hello":"pymicro-flask"}'
GET=$(curl -d "$DATA" -s $PYMICRO/microservice)

RET_DATA=$(echo $GET | python -c "import sys, json; print(json.load(sys.stdin)['hello'])")
if [[ $RET_DATA != "pymicro-flask" ]] ; then exit 1; fi


if [ "$PYMICRO_SEND_METRICS" = "true" ]; then
    METRICS=$(curl -s $PYMICRO_STATSD_WEB/metrics | grep -i pymicro_)
    UWSGI_METRICS=$(curl -s $PYMICRO_STATSD_WEB/metrics | grep -i uwsgi_pymicro_)
    if [[ -z "$METRICS" ]] ; then exit 1; fi
    if [[ -z "$UWSGI_METRICS" ]] ; then exit 1; fi
else
    METRICS=$(curl -s $PYMICRO/metrics | grep -i pymicro_)
    if [[ -z "$METRICS" ]] ; then exit 1; fi
fi
