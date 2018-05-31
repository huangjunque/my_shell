import subprocess
import re
import sys
import getopt
import time
import urllib2
import os
import json
import urllib
import cookielib
ISOTIMEFORMAT='%Y-%m-%d %H:%M:%S'
RAIINFOS =  {
    "LSI": {
            "raidcmd":'/opt/MegaRAID/MegaCli/MegaCli64',
            "param_es":'-EncInfo -aALL',
            "param_level":'-AdpAllInfo -aALL',
            "param_pdlist":'-PDList -aALL',
            "param_cls":'-CfgClr -Force -aAll ',
            "params_cfg":'-cfgdsply -aALL',
            "raid_default_params":{
                                    'name':'create',
                                    'write_cache_policy':'WB',
                                    'strip_size':'128',
                                    'read_cache_policy':'Direct',
                                    'read_ahead_pllicy':'RA',
                                    'Hotspare_status':None,
                                    'Hotspare_position':'',
                                    'action_status':'Old',
                                    'service_type':None,
                                 },
          },
}
 
def check_raid_vender():
    pcicwd='/sbin/lspci'
    try:info=get_cmd_info(pcicwd,'-b')
    except OSError,e:
        fer= " %s: %s " % (e,pcicwd)
        #post_install(fer,'running')
        print fer
        #sys.exit(1)
    else:
        vender=re.findall(r'RAID bus controller:\s+(LSI).*',info)
        if 'LSI' in vender:
            return RAIINFOS.get('LSI', {})


def get_cmd_info(cmd,param):
    plist=[cmd]+param.split()
    #print plist
    try: info_list=subprocess.Popen(plist,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    except OSError,e:
        msg= " %s: %s " % (e,plist)
        #post_install(msg,'running')
        print msg
        return None
    else:
        info=info_list.communicate()
    return info[0]



def get_server_sn():
    cmd='/usr/sbin/dmidecode'
    sys_params='-t system'
    system_info=get_cmd_info(cmd,sys_params)
    for info in system_info.split('\n'):
        sys_info=re.match(r'\s+Serial Number:\s+(\w+)',info)
        if sys_info:
            sn=sys_info.group(1)
    return sn

def get_server_vender():
    cmd='/usr/sbin/dmidecode'
    sys_params='-t system'
    system_info=get_cmd_info(cmd,sys_params)
    for info in system_info.split('\n'):
        sys_info=re.match(r'\s+Manufacturer:\s+(\w+)',info)
        if sys_info:
            vender=sys_info.group(1)
    return vender


class  rms_https(object):

    def __init__(self):
        self.cj = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(self.opener)
        #basestr = encodestring('%s:%s' % (username,password))[:-1]
        self.headers={'User-Agent':'Python Urllib',
                      'Content-Type': 'application/json',
                      'Accept':'application/json',
                      }

    def get(self,url):
        req=urllib2.Request(url,None,self.headers)
        try:  pp=self.opener.open(req)
        except urllib2.URLError,e:
            if hasattr(e,"reason"):
                print "Failed to reach the server"
                print "The reason:",e.reason,url
                return None
            elif hasattr(e,"code"):
                print "Error code:",e.code,url
                print "Return content:",e.read()
                return None

        else:
            return pp.read()

    def post(self,post_url,param):
        param=json.dumps(param)
        p_req=urllib2.Request(post_url,param,self.headers)
        try:  pp=self.opener.open(p_req)
        except urllib2.URLError,e:
            if hasattr(e,"reason"):
                print "Failed to reach the server"
                print "The reason:",e.reason,url
                return None
            elif hasattr(e,"code"):
                print "Error code:",e.code,url
                print "Return content:",e.read()
                return None

        else:
            return pp



def get_cpu_info():
    py_id_list=[]
    cpu_model_list=[]
    with open('/proc/cpuinfo') as f:
        cpuinfo=f.read()
    for cpu in cpuinfo.split('\n'):
        cpu_name=re.match(r'model name\s+:\s(.*)',cpu)
        py_id=re.match(r'physical\s+id\s+:\s(\d)',cpu)
        if cpu_name and cpu_name.group(1) not in cpu_model_list:
            cpu_model_list.append(cpu_name.group(1))
        if py_id and py_id.group(1) not in py_id_list:
            py_id_list.append(py_id.group(1))
    cpu_count=len(py_id_list)
    cpu_model=''.join(cpu_model_list)
    return ('%s *%s'% (cpu_model,cpu_count))
                     


def get_disk_info(raid_cmd_dict):
    if isinstance(raid_cmd_dict,dict):
        cmd=raid_cmd_dict.get('raidcmd',{})
        params=raid_cmd_dict.get('param_pdlist',{})
        info=get_cmd_info(cmd,params)
        hdinfo=[]
        if info:
            for i in info.split('Enclosure Device'):
                es_id=re.match(r' ID:\s+(\d+)',i)
                hd_size=re.search(r'Raw Size: (.*) \[(.*)',i)
                solt_number=re.search(r'Slot Number: (\d+)',i)
                hd_stat=re.search(r'Firmware state: (.*)',i)
                hd_type=re.search(r'Media Type:\s+(.*)',i)
                pd_type=re.search(r'PD Type:\s+(.*)',i)
                if  hd_size and solt_number and hd_stat:
                    hdinfo.append((hd_size.group(1), hd_stat.group(1),solt_number.group(1),es_id.group(1),hd_type.group(1),pd_type.group(1)))
            return  hdinfo
        else:
            return None
    else:
        return None



def format_disk(disk_info_list):
    disk_class={
                'SAS 300GB':0,
                'SAS 600GB':0,
                'SAS 900GB':0, 
                'SATA 500GB':0,
                'SATA 1TB':0,
                'SATA 2TB':0,
                'SATA 3TB':0,
                'SATA 4TB':0,
                'SSD 256GB':0,
                'SSD 400GB':0,
                'SSD 512GB':0,
                }
    disk_other=[]

    for disk_info in disk_info_list:
        disk_cap,disk_unit=disk_info[0].split()
        if disk_info[4] == 'Hard Disk Device':
           if disk_unit == 'TB':
               if float(disk_cap) < 2:
                   disk_class['SATA 2TB']+=1
               elif float(disk_cap) >2 and float(disk_cap) <3:
                   disk_class['SATA 3TB']+=1
               elif float(disk_cap) >3 and float(disk_cap) <4:
                   disk_class['SATA 4TB']+=1 
               else:
                   disk_other.append(disk_info[0]+' SATA')
           elif disk_unit == 'GB':
               if float(disk_cap) < 500 and float(disk_cap) >400:
                   disk_class['SATA 500GB']+=1                     
               elif float(disk_cap) >900 and float(disk_cap) <1000:
                   disk_class['SATA 1TB']+=1 
               elif float(disk_cap) < 300 and float(disk_cap)>200 :
                    disk_class['SAS 300GB']+=1
               elif float(disk_cap) >500 and float(disk_cap) <600:
                    disk_class['SAS 600GB']+=1
               elif float(disk_cap) >800 and float(disk_cap) <900:
                    disk_class['SAS 900GB']+=1
               else:
                    disk_other.append(disk_info[0]+' SAS')
        elif disk_info[4] == 'Solid State Device':
            if disk_unit == 'GB':
                if float(disk_cap) < 256:
                    disk_class['SSD 256GB']+=1
                elif float(disk_cap) >256 and float(disk_cap) <400:
                    disk_class['SSD 400GB']+=1
                elif float(disk_cap) >400 and float(disk_cap) <512:
                    disk_class['SSD 512GB']+=1
                else:
                    disk_other.append(disk_info[0]+' SSD')
    str=''
    for a,w in disk_class.items():
        if w !=0:
            str='%s *%s ' % (a,w)+str
    if disk_other:
        return str+','.join(disk_other)
    else:
        return str
                     
def get_memory_info():
    cmd='/usr/sbin/dmidecode'
    params='-t memory'
    info=get_cmd_info(cmd,params)
    mem_dict={}
    mem_str=''
    if info:
        for i in info.split('Memory Device'):
            mem_size=re.search(r'\s+Size:\s+(\d+)\s+MB',i)
            mem_type=re.search(r'\s+Type:\s+(.*)',i)
            mem_speed=re.search(r'\s+Speed:\s+(\d+\s+MHz)',i)
            if mem_size:
                 mem_unit=str(int(mem_size.group(1))/1024)+'GB '+ ' '+mem_type.group(1)+' '+mem_speed.group(1)
                 if mem_dict.get(mem_unit,{}):
                    mem_dict[mem_unit]+=1
                 else:
                    mem_dict[mem_unit]=1
    for k,v in mem_dict.items():
        mem_str='%s *%s ' % (k,v)+mem_str
    return mem_str

def get_server_fullvender():
    cmd='/usr/sbin/dmidecode'
    sys_params='-t system'
    system_info=get_cmd_info(cmd,sys_params)
    vender=''
    for info in system_info.split('\n'):
        sys_info=re.match(r'\s+Manufacturer:\s+(\w+)',info)
        sys_product=re.match(r'\s+Product Name:\s+(.*)',info)
        if sys_info:
            vender=sys_info.group(1)+vender
        elif sys_product:
            vender=vender+ ' '+sys_product.group(1)
    return vender



def get_server_NIC_info():
    cmd='/sbin/ip'
    ip_params='link show'
    if_link=get_cmd_info(cmd,ip_params)
    if_list=[]
    mac_list=[]
    if if_link:
        for link in if_link.split('\n'):
                linfo=re.match(r'\d+:\s+(.*):\s+<.*BROADCAST.*',link)
                minfo=re.match(r'\s+link\/ether\s+(.*)\s+brd',link)
                if linfo :
                    if_list.append(linfo.group(1))
                if minfo:
                    mac_list.append(minfo.group(1))
    info=zip(if_list,mac_list)
    return info


def ip_sorting(ip_addr):
    addr=ip_addr.strip().split('.')
    for i in range(4):
        addr[i]=int(addr[i])
    if addr[0]==10:
        return "1"
    if addr[0]==172:
       if addr[1]>=16 and addr[1]<=31:
           return "1"
    if addr[0]==192:
       if addr[1]==168:
           return "1"
    return "2"





def get_server_ip_info():
    cmd='/sbin/ip'
    ip_params='addr show'
    if_addr=get_cmd_info(cmd,ip_params)
    ip_ext=[]
    in_ip_flag=0
    out_ip_flag=0
    ip_in=""
    ip_out=""
    if if_addr:
        for addr in if_addr.split('\n'):
            ip_info=re.match(r'\s+inet\s+(.*)\s+brd.*',addr)
            if ip_info:
                ip=ip_info.group(1).split('/')[0]
                if ip_sorting(ip) == '1' and in_ip_flag == 0:
                    ip_in=ip
                    in_ip_flag=1
                elif ip_sorting(ip) == '2' and out_ip_flag == 0:
                     ip_out=ip
                     out_ip_flag=1
                else:
                   ip_ext.append(ip)
    if ip_ext:
       ip_ext= ','.join(ip_ext)
    ip_dict={'ip' : ip_in,
             'ip_out' : ip_out,
             'ip_ext' : ip_ext
             }
    return ip_dict
                 


def get_switch_info(NIC_info):
    cmd='/usr/sbin/lldptool'
    nic_dict={}
    param='set-lldp -i %s adminStatus=rxtx'    
    switch_param='-t -n -i %s -V %s'
    for nic in NIC_info:
        params=param % nic[0]
        get_cmd_info(cmd,params)
        nic_dict[nic[0]]={'mac':nic[1]}
        switch_sysname_param= switch_param % (nic[0],'sysName')
        switch_portid_param= switch_param % (nic[0],'portID')
        switch_model_param= switch_param % (nic[0],'sysDesc')
        result_name=get_cmd_info(cmd,switch_sysname_param)
        switch_name=re.findall(r'System Name TLV\s+(.*)',result_name)
        result_port=get_cmd_info(cmd,switch_portid_param)
        switch_port=re.findall(r'\s+Ifname:\s+(.*)',result_port)
        result_model=get_cmd_info(cmd,switch_model_param)
        switch_model=re.search(r'\w+-.*(-\w+)?',result_model)
        try:nic_dict[nic[0]]['switch_name']=switch_name[0]
        except IndexError,e:
            nic_dict[nic[0]]['switch_name']=''
        try:nic_dict[nic[0]]['switch_port']=switch_port[0]
        except IndexError,e:
            nic_dict[nic[0]]['switch_port']=''
        try:nic_dict[nic[0]]['switch_model']=switch_model.group().strip()
        except AttributeError,e:
            nic_dict[nic[0]]['switch_model']=''
    return nic_dict


def ipmi_mod_load():
    mod_cmd='/sbin/modprobe'
    mod_params=['ipmi_devintf','ipmi_watchdog','ipmi_poweroff']
    for param in mod_params:
        get_cmd_info(mod_cmd,param)




def ipmi_boot_ctl(boot_dev,Persistent=None):
    ipmi_mod_load()
    ipmi_cmd='/usr/bin/ipmitool'
    if boot_dev in ['disk','pxe','cdrom']:
       if Persistent:
           ipmi_boot='-I open chassis bootdev %s options=persistent' % boot_dev
       else:
           ipmi_boot='-I open chassis bootdev %s' % boot_dev
       cmd_result=get_cmd_info(ipmi_cmd,ipmi_boot)
    else:
        cmd_result=None
        print 'ipmi boot device  is error'
    return cmd_result        


def get_single_disk():
    cmd='/usr/sbin/lshw'
    params='-class disk -quiet'
    disk_list=[]
    disk_info=get_cmd_info(cmd,params)
    for disk in disk_info.split('*-'):
        size=re.search(r'\s+size:\s+(.*)',disk)
        if size:
            disk_desc=re.search(r'\s+description:\s+(.*)',disk)
            if disk_desc:
                disk_class=disk_desc.group(1)
            disk_list.append(size.group(1)+disk_class)

    return disk_list



