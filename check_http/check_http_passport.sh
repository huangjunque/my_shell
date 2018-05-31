#!/bin/bash

# some vars
ymdhms=$(date +%Y%m%d%H%M%S)

# check_http exec
check_http="/usr/lib64/nagios/plugins/check_http"

# check_http options
check_logs="/data/logs/zabbix/check_http_passport.log"
hostname="127.0.0.1"
head='Host: idp.hifuntv.com'
r_regex='"err": 0'

# post data
u_path_1="/login"
p_data_1='invoker=hunantvphone&sign=1d20e99a7d635ce256d364e7bbfbaa51d5350819&data=%7B%22username%22%3A%22monitor%22%2C%22password%22%3A%22Uf%2BzouJbQpYTn7PrNWdao0YTF1UwaosZCycLA4TqOMZEWISzz%5C%2Fnvi1ZgyP41zFYRJ936SMLYj05xNqIgsidZAn9IhVbVTwCdky7CNVkm75thPe97lULL7XzwJ9Ye1XZrnXE%2B9RH0cqnhFwrBWraE3xGrgwwMkTnrftfF9xuHYPA%3D%22%2C%22mac%22%3A%22%22%2C%22version%22%3A%22%22%2C%22license%22%3A%22%22%2C%22os%22%3A%22%22%2C%22phone_type%22%3A%22%22%2C%22read%22%3A%22%22%2C%22uip%22%3A%22127.0.0.1%22%2C%22seqid%22%3A%2231fab3f17b5f46e02d319551391a7a58%22%2C%22is_sign%22%3A1%7D'

# echo time
#echo "$ymdhms" #>> $check_logs

case "$1" in
  # check idp login
  login)
    w_timeout="1"; c_timeout="3"
#    curl -s -XPOST http://$hostname$u_path_1 -d "$p_data_1" -H "$head"
#    echo "test"
    $check_http -I "$hostname" -u "$u_path_1" -k "$head" -P "$p_data_1" -r "$r_regex" -w $w_timeout -c $c_timeout #>> $check_logs
    ;;
  # check idp getuser
  getuser)
    w_timeout="0.2"; c_timeout="1"
    ticket=$(curl -s -XPOST http://$hostname$u_path_1 -d "$p_data_1" -H "$head" | awk -F'"' '{print $6}')
    u_path_2="/getuser"
    p_data_2="invoker=hunantvphone&sign=076df8dbeae6df91c94253f60351cd46669f0f56&data=%7B%22ticket%22%3A%22${ticket}%22%2C%22mac%22%3A%22%22%2C%22version%22%3A%22%22%2C%22license%22%3A%22%22%2C%22uip%22%3A%22127.0.0.1%22%2C%22seqid%22%3A%228424e5efedbae6f4ddd8db5f6f36c0d4%22%2C%22is_sign%22%3A1%7D"
#	curl -s -XPOST http://$hostname$u_path_2 -d "$p_data_2" -H "$head"
#	echo "test_2"
    $check_http -I "$hostname" -u "$u_path_2" -k "$head" -P "$p_data_2" -r "$r_regex" -w $w_timeout -c $c_timeout #>> $check_logs
    ;;
  *)
    echo "ZBX_NOTSUPPORTED"
    ;;
esac
