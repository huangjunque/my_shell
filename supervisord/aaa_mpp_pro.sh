#!/bin/sh
SUPER=/usr/bin/supervisord
DIR_NAME=`dirname $0`
SUPERVISORD_CONF=/data/www/aaa_mpp/confs/pro.supervisor.conf

start() {
    echo "start"
    $SUPER -c $SUPERVISORD_CONF
    echo "          [Done]"
}

usage() {
    echo "Usage: sh ${DIR_NAME}/pro.sh start|stop|restart"
}


stop() {
    echo "stop"
    if [ -f /tmp/supervisord_aaa_mpp.pid ]; then
        cat /tmp/supervisord_aaa_mpp.pid | xargs kill
    else
        pgrep -lf 'aaa_mpp/confs/pro.supervisor.conf' | grep supervisord  | awk  '{print $1}'|xargs kill
    fi
    sleep 3
    echo "          [Done]"
}


restart() {
    echo "restart"
    if [ -f /tmp/supervisord_aaa_mpp.pid ]; then 
        pid=`cat /tmp/supervisord_aaa_mpp.pid`
        kill -HUP $pid
    else
        $SUPER -c $SUPERVISORD_CONF
    fi
    echo "          [Done]"
}

###################
#      main              
###################
if [ $# -eq 0 ] ; then
    usage
    exit -1
fi

case $1 in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    *)
        usage
        exit -1
        ;;
esac
