#!/bin/bash
## This script is for record Filesystem Use%,IUse% everyday and send alert mail when % is more than 90%.
## author: junque

log=/data/logs/disk/`date +%F`.log
date +'%F %T' > $log
df -h >> $log
echo >> $log
df -i >> $log

for i in `df -h |grep -v 'Use%' | sed 's/%/ /' | awk '{print $5}'`; do
    if [ $i -gt 90 ]; then
        use=`df -h|grep -v 'Use%'|sed 's/%//'|awk '$5=='$i' {print $1,$5}'`
        echo "$use" >> use
    fi
done

if [ -e use ]; then
  ##这里可以使用咱们之前介绍的mail.py发邮件
  main -s "Filesystem Use% check" root@localhost < use
  rm -rf use
fi

for j in `df -i|grep -v 'IUse%'|sed 's/%//'|awk '{print $5}'`; do
    if [ $j -gt 90 ]; then
        iuse=`df -i |grep -v 'IUse%'|sed 's/%/ /'|awk '%5=='$j' {print $1,%5}'`
        echo "$iuse" >> iuse
    fi
done 
   
if [ -e  iuse ]; then
    mail -s "Filesystem IUse% check" root@localhost < iuse
    rm -rf iuse
fi

 


