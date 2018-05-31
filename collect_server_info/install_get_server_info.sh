#!/bin/bash
mkdir -p /data/scripts
cd /data/scripts
in_main_url='http://10.1.213.1:18088/server_info/get_linux_server_info.py'
in_fuc_url='http://10.1.213.1:18088/server_info/rms_functions_linux.py'
in_raid_url='http://10.1.213.1:18088/server_info/MegaCli-8.07.10-1.noarch.rpm'
out_main_url=" -u imogo_ops:ULumo$=av%(tFO -H "HOST:os-manage.ops.imogo.com"  -k  https://211.151.133.53:8443/os-manage/scripts/get_linux_server_info.py -o /data/scripts/get_linux_server_info.py"
out_fuc_url="  -u imogo_ops:ULumo$=av%(tFO -H "HOST:os-manage.ops.imogo.com"  -k  https://211.151.133.53:8443/os-manage/scripts/rms_functions_linux.py -o /data/scripts/rms_functions_linux.py"
out_raid_url=" -u imogo_ops:ULumo$=av%(tFO -H "HOST:os-manage.ops.imogo.com"  -k  https://211.151.133.53:8443/os-manage/scripts/MegaCli-8.07.10-1.noarch.rpm -o /data/scripts/MegaCli-8.07.10-1.noarch.rpm"

yum install -y pciutils
yum install -y dmidecode
yum install -y lldpad
yum install -y lshw

wget $in_main_url
if [ $? -eq 0 ];then
    wget $in_fuc_url
    wget $in_raid_url
    /bin/rpm -ivh /data/scripts/MegaCli-8.07.10-1.noarch.rpm
    echo   "1 4 * * * /usr/bin/python /data/scripts/get_linux_server_info.py " >>  /var/spool/cron/root
else
    http_code=`curl -s -w "%{http_code}" $out_main_url`
    if [ "a$http_code" == "a200" ];then
        `curl -s $out_raid_url`
        `curl -s $out_fuc_url`
        /bin/rpm -ivh /data/scripts/MegaCli-8.07.10-1.noarch.rpm
        grep 'get_linux_server_info.py'  /var/spool/cron/root ;
    if [ $? != 0 ];then
            echo   "1 4 * * * /usr/bin/python /data/scripts/get_linux_server_info.py " >>  /var/spool/cron/root
    fi
    else
        echo "please check 211.151.133.53 iptables set "
        exit 1

    fi
fi