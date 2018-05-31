import urllib2
import re
import json
import subprocess
import cookielib
import time
import socket
import os
from rms_functions_linux import *
api_token='cee48674b45d2acc54476382c294295d'

fnull = open(os.devnull, 'w')
net_result = subprocess.call('ping -c 1 www.baidu.com', shell = True, stdout = fnull, stderr = fnull)
if net_result:
    Server='10.100.1.109'
else:
    Server='agent.rms.ops.hunantv.com'

post_server_info_url='http://%s/hrm/server/agent_server_post?token=%s'

def boot_dev(dev):
    cmd='/usr/bin/ipmitool'
    ipmi_params='-I open chassis bootdev %s' % dev
    ipmi_info=get_cmd_info(cmd,ipmi_params)

def get_server_status(rms,url,server_sn):
    surl=url % (Server,server_sn,api_token)
    result=rms.get(surl)
    all_result={}
    if result:
        sdict=json.loads(result)
        all_result['server_hard_status'] = True
        if sdict['status'] == 0:
            all_result['server_soft_status'] = True
        else:
            all_result['server_soft_status'] = None
    else:
        all_result['server_hard_status'] = None
    return all_result



def post_server_info(rms,url,post_data):
    surl=url % (Server,api_token)
    for i in range(5):
        result=rms.post(surl,post_data)
        time.sleep(5)
        if  result:
            print result.read()
            break




def main():
    post_params={'sn':'',
                 'mac':'',
                 'cpu':'',
                 'memory':'',
                 'disks':'',
                 'vendor':'',
                 'switch':''
                }
    raid_config = check_raid_vender()
    if not raid_config:
        print "error: no raid config found"
        #sys.exit(1)
    server_sn=get_server_sn()
    server_mac=get_server_NIC_info()[0][1]
    cpu_info=get_cpu_info()           
    dlist=get_disk_info(raid_config)
    post_data_list=[]
    if dlist:
        disk_info=format_disk(dlist)
    else:
        disk_info=get_single_disk()
    memory_info=get_memory_info()
    nic_info=get_server_NIC_info()
    switch_info=get_switch_info(nic_info)
    server_vendor_info= get_server_fullvender()
    post_params['mac']=server_mac
    post_params['sn']=server_sn
    post_params['memory']=memory_info
    post_params['cpu']=cpu_info
    post_params['disks']=disk_info
    post_params['switch']=switch_info
    post_params['vendor']=server_vendor_info
    post_params.update(get_server_ip_info())
    post_params.update({'hostname':socket.gethostname()})
    post_data_list.append(post_params)
    rms=rms_https()
    post_server_info(rms,post_server_info_url,post_data_list)
  

if __name__ == '__main__':
    main()
