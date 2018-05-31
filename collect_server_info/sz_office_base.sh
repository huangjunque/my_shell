#!/bin/bash
Usage()
{
if [ $# -ne 1 ];then
  echo "Usage:$0 hostname. Example: $0 192.168.2.2"
  exit 1
fi
}
Usage $#
echo $1 | egrep -q '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$' || Usage
IP=$1
host_1=`echo $IP|awk -F. '{print $3}'`
host_2=`echo $IP|awk -F. '{print $4}'`
Hostname="app-sz-$host_1-$host_2.sz.chosk.net"
echo $Hostname

#config hostname
sed -i '/HOSTNAME/d' /etc/sysconfig/network
sed -i '/NETWORKING/aHOSTNAME='''$Hostname'''' /etc/sysconfig/network 

#config IP
sed -i 's/BOOTPROTO="dhcp"/BOOTPROTO="static"/' /etc/sysconfig/network-scripts/ifcfg-eth0   
sed -i '/IPADDR/d' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i '/NETMASK/d' /etc/sysconfig/network-scripts/ifcfg-eth0
sed -i '/GATEWAY/d' /etc/sysconfig/network-scripts/ifcfg-eth0
cat <<EOF >> /etc/sysconfig/network-scripts/ifcfg-eth0
IPADDR=$IP
NETMASK=255.255.255.0
GATEWAY=192.168.2.1
EOF
#config dns
cat <<EOF > /etc/resolv.conf 
nameserver 192.168.2.131
nameserver 114.114.114.114
EOF

cat <<EOF >> /var/spool/cron/root 
#ntpdate
0 0 * * * /usr/sbin/ntpdate ntp.l99.com;/sbin/hwclock -w
EOF
hostname $Hostname
/etc/init.d/network restart
/etc/init.d/iptables stop
chkconfig iptables off

/usr/sbin/ntpdate ntp.l99.com;/sbin/hwclock -w
hostname
ping -c 2 qq.com
echo "###########################"
echo "Base set is ok!"
echo "###########################"
