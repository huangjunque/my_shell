#!/bin/bash

# argv vars
host_ip=$1
path=$2

# some vars
ymdhms=$(date +%Y%m%d%H%M%S)

# check_http exec
check_http="/usr/lib64/nagios/plugins/check_http"

# check_http_options
check_logs="/data/logs/zabbix/check_http_pay.log"
hostname="$host_ip"
head="Host: $host_ip"

# echo time
#echo "$ymdhms" #>> $check_logs
#curl -i -XGET http://$hostname$u_path

usage()
{
    echo "Usage: $(basename $0) host_ip path"
    echo -e "\tpath: health"
    echo -e "\thost_ip: 127.0.0.1"
}

if [ "$#" -ne 2 ]
then
    usage
    exit
fi

case "$path" in
    health)
    u_path="/health.php"
    r_regex='"error":0'
    w_timeout="1"; c_timeout="3"
    $check_http -I "$hostname" -u "$u_path" -k "$head" -r "$r_regex" -w $w_timeout -c $c_timeout
    ;;
    *)
    echo "ZBX_NOTSUPPORTED"
    ;;
esac

