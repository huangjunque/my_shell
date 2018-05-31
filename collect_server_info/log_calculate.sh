#!/bin/bash
#Name: log_calculate.sh
#Version Number: 1.0.0
#Type:calculate log
#Language: bash shell
#Date: 2016-01-19
#Author: 2015-01-10

start_hour=`date --date "-2 hour" "+%H"`
end_hour=`date --date "-1 hour" "+%H"`
echo $end_hour


current_time=`date "+%Y%m%d%H%M"`
log_filename="$1"
result="$2"
echo '' > $result


start_log_filename="${log_filename}-`date --date "-2 hour -15 min" "+%Y%m%d%H%M"`"   #计算初始日期
middle_log_filename="${log_filename}-`date --date " -2 hour " "+%Y%m%d%H"`*"	     #计算中间端时间
end_log_filename="${log_filename}-`date --date " -1 hour " "+%Y%m%d%H%M"`"	     #计算末尾日期

(
	echo "$start_log_filename: `grep  -c -E "$start_hour:[0-9]{2}:[0-9]{2}" $start_log_filename`" >> $result
	grep  -c -E "($start_hour|$end_hour):[0-9]{2}:[0-9]{2}" $middle_log_filename >> $result
	echo "$end_log_filename: `grep  -c -E "$end_hour:00:[0-9]{2}" $end_log_filename`"  >> $result

)



wait
