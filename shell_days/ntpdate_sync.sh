#!/bin/bash
#备份源文件
mv /etc/localtime /etc/localtimebak
#修改时区为东八区
ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
#安装ntp服务
yum -y install ntpdate ntp
#修改/etc/ntp.conf 
cat << EOF  >> /etc/ntp.conf 
server cn.pool.ntp.org
server time-a.nist.gov
server time.windows.com
server time.nist.gov
EOF
#调试查看时间差异
ntpdate -d cn.pool.ntp.org
#同步时间
ntpdate cn.pool.ntp.org && echo "SYNC_HWCLOCK=yes" >>/etc/sysconfig/ntpd || echo "Setting Filed!"
#自启动
chkconfig --levels 235 ntpd on
/etc/init.d/ntpd start
echo `date`
