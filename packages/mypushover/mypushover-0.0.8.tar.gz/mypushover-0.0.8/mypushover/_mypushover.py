# coding=utf-8
import time
import os
import requests
import ipaddress
from icmplib import multiping
import configparser
import codecs
import sys
from outdated import check_outdated


On_Red='\033[41m' # red background
NC='\033[0m' # No Color
timezone = time.timezone
timezone_str = time.strftime("%z", time.localtime(timezone))
timezone_str = timezone_str[0:3] + ":" + timezone_str[3:5]
here = os.path.abspath(os.path.dirname(__file__))
# conf_path = os.path.join(here, 'pushover_conf.conf')

def get_conf(conf_path):
    if not os.path.exists(conf_path):
        print(f'{On_Red}Error: {conf_path} not exists!{NC}\nplease input your conf info...\n')
        gen_conf(conf_path)
    is_conf_ok = check_conf(conf_path)
    if is_conf_ok == False:
        print(f'{On_Red}Error: {conf_path} error!{NC}\nplease input correct info...\n')
        os.remove(conf_path)
        gen_conf(conf_path)
    config = configparser.ConfigParser()
    config.read(conf_path)
    host_server_name = config['Host_server_info']['name']
    host_server_ip = config['Host_server_info']['ip_addr']
    max_fail_times = config['Host_server_info']['max_fail_times']
    sleep_time_seconds = config['Host_server_info']['sleep_time_seconds']
    APP_TOKEN = config['Pushover_token']['APP_TOKEN']
    USER_KEY = config['Pushover_token']['USER_KEY']
    Clients_info = config['Clients_info']
    server_ip_name_dict = {}
    for host in Clients_info:
        ip = Clients_info[host]
        if '/' in ip:
            subnet = ip.split('/')[0]
            cidr = ip.split('/')[1]
            cidr = int(cidr)
            ip_list = ipaddress.ip_network(ip,False).hosts()
            for i,ip_i in enumerate(ip_list):
                ip_str = ip_i.__str__()
                server_ip_name_dict[ip_str] = f'{host} {i+1}'
        else:
            server_ip_name_dict[ip]=host

    max_fail_times = int(max_fail_times)
    sleep_time_seconds = int(sleep_time_seconds)

    return host_server_name,APP_TOKEN,USER_KEY,server_ip_name_dict,max_fail_times,host_server_ip,sleep_time_seconds
    pass

def gen_conf(conf_path):
    # host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict,
    # max_fail_times, host_server_ip, sleep_time_seconds
    while 1:
        host_server_name = input('host_server_name:')
        if host_server_name != '':
            break
        print(f'Error: host_server_name can not be empty, please input again...')
    while 1:
        host_server_ip = input('host_server_ip:')
        if len(host_server_ip.split('.')) == 4:
            break
        print(f'Error: host_server_ip error, please input again...')
    while 1:
        max_fail_times = input('max_fail_times (default:1):')
        if len(max_fail_times) == 0:
            max_fail_times = 1
            break
        try:
            max_fail_times = int(max_fail_times)
            break
        except:
            print(f'Error: max_fail_times error, please input again...')
    while 1:
        sleep_time_seconds = input('sleep_time_seconds (default:600):')
        if len(sleep_time_seconds) == 0:
            sleep_time_seconds = 600
            break
        try:
            sleep_time_seconds = int(sleep_time_seconds)
            break
        except:
            print(f'Error: sleep_time_seconds error, please input again...')

    while 1:
        APP_TOKEN = input('APP_TOKEN:')
        if len(APP_TOKEN) > 20:
            break
        print(f'Error: APP_TOKEN error, please input again...')

    while 1:
        USER_KEY = input('USER_KEY:')
        if len(USER_KEY) > 20:
            break
        print(f'Error: USER_KEY error, please input again...')

    Clients_info = {}
    flag = 1
    while 1:
        host = input(f'host_name {flag} (leave blank to exit) :')
        if host == '' and flag > 1:
            break
        if host == '':
            print(f'Error: You need at least add one host, please input again...')
            continue
        while 1:
            ip = input(f'ip_addr {flag}:')
            if len(ip.split('.')) == 4:
                break
            print(f'Error: ip_addr error, please input again...')
        Clients_info[host] = ip
        flag += 1
    with open(conf_path,'w') as f:
        f.write(f'[Host_server_info]\nname={host_server_name}\nip_addr={host_server_ip}\nmax_fail_times={max_fail_times}\nsleep_time_seconds={sleep_time_seconds}\n')
        f.write('\n')
        f.write(f'[Pushover_token]\nAPP_TOKEN={APP_TOKEN}\nUSER_KEY={USER_KEY}\n')
        f.write('\n')
        f.write(f'[Clients_info]\n')
        for host in Clients_info:
            f.write(f'{host}={Clients_info[host]}\n')

def check_conf(conf_path):
    config = configparser.ConfigParser()
    config.read(conf_path)
    try:
        host_server_name = config['Host_server_info']['name']
        host_server_ip = config['Host_server_info']['ip_addr']
        max_fail_times = config['Host_server_info']['max_fail_times']
        sleep_time_seconds = config['Host_server_info']['sleep_time_seconds']
        APP_TOKEN = config['Pushover_token']['APP_TOKEN']
        USER_KEY = config['Pushover_token']['USER_KEY']
        Clients_info = config['Clients_info']
        assert len(host_server_name) > 0
        assert len(host_server_ip.split('.')) == 4
        assert int(max_fail_times) > 0
        assert int(sleep_time_seconds) > 0
        assert len(APP_TOKEN) > 20
        assert len(USER_KEY) > 20
        assert len(Clients_info) > 0
        return True
    except Exception as e:
        print(e)
        return False

    pass

def pushover(title,message,conf_path):
    # return
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf(conf_path)
    print('title----------',title)
    print('message----------',message)
    # return

    try:
        r = requests.post(
            'https://api.pushover.net/1/messages.json',
            data={
                'token': APP_TOKEN,
                'user': USER_KEY,
                'message': message,
                'title': title,
                'html': 1,
            },
        )
        # print(r.content)
    except Exception as e:
        os.system(f'echo "{On_Red}{e}{NC}"')

def gen_message(message_dict,host_status_dict,fail_num_dict,switch_dict,is_init_message,conf_path):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    Down = html_add_color_red('Down')
    Up = html_add_color_green('Up')
    status_str_dict = {True:Up,False:Down}
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,host_server_ip,sleep_time_seconds = get_conf(conf_path)
    # title = f''
    content = f'[{now}]' + ' ' + f'Timezone: {timezone_str}' + '\n\n'

    if is_init_message == True:
        title = 'Init'
        for host in host_status_dict:
            switch_status = switch_dict[host].replace('True', Up).replace('False', Down)
            host_name = server_ip_name_dict[host]
            host_name = html_add_color_blue(host_name)
            content += f'{host_name} {host} : {switch_status}\n'
        host_server_name = html_add_color_blue(host_server_name)
        content += f'\nFrom {host_server_name}:{host_server_ip}'
        content += f'\nsleep {sleep_time_seconds} seconds'
        return title, content

    if len(message_dict) == 0:
        return None, None
    current_status_str = ''
    for host in message_dict:
        message = message_dict[host]
        fail_time = fail_num_dict[host]
        if fail_time > 0:
            current_status_str += f'{message}, fail times:{fail_time}\n'
        else:
            current_status_str += f'{message}\n'
    if 'Recover' in current_status_str and 'Down' in current_status_str:
        title = 'Recover and Down'
    elif 'Down' in current_status_str:
        title = 'Down'
    elif 'Recover' in current_status_str:
        title = 'Recover'
    else:
        raise Exception
    # content += '\n------Clients status------\n'
    for host in host_status_dict:
        host_name = server_ip_name_dict[host]
        host_name = html_add_color_blue(host_name)
        switch_status = switch_dict[host].replace('True',Up).replace('False',Down)
        content += f'{host_name} {host} : {switch_status}\n'
    host_server_name = html_add_color_blue(host_server_name)
    content += f'\nFrom {host_server_name}:{host_server_ip}'
    content += f'\nsleep {sleep_time_seconds} seconds'
    print(content)
    return title, content

def is_server_online(conf_path):
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf(conf_path)

    server_ip_list = list(server_ip_name_dict.keys())
    ping_results = multiping(server_ip_list, privileged=False, count=5, interval=1)
    status_dict = {}

    for host in ping_results:
        addr = host.address
        received = host.packets_received
        if received == 0:
            status = False
        else:
            status = True
        status_dict[addr] = status
    return status_dict

def init_is_server_online(conf_path):
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf(conf_path)

    server_ip_list = list(server_ip_name_dict.keys())
    # print(server_ip_list);exit()
    status_dict = {}
    for ip in server_ip_list:
        status_dict[ip] = None
    return status_dict

def fail_message(host,conf_path):
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf(conf_path)
    hostname = server_ip_name_dict[host]
    Down = 'Down'
    content = f'{hostname}:{host} {Down}'
    return content

def recover_message(host,conf_path):
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf(conf_path)

    hostname = server_ip_name_dict[host]
    Recover = 'Recover'
    content = f'{hostname}:{host} {Recover}'
    return content

def html_add_color_blue(text):
    text = f'<b>{text}</b>'
    text = f'<font color="#0000ff">{text}</font>'
    return text

def html_add_color_red(text):
    text = f'<b>{text}</b>'
    text = f'<font color="#ff0000">{text}</font>'
    return text

def html_add_color_green(text):
    text = f'<b>{text}</b>'
    text = f'<font color="#00ff00">{text}</font>'
    return text

def run(conf_path):
    init_status_dict = init_is_server_online(conf_path)
    host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf(conf_path)
    fail_num_dict = {}
    for host in server_ip_name_dict:
        fail_num_dict[host] = 0
    is_init_message = True
    while 1:
        host_status_dict = is_server_online(conf_path)
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        message_dict = {}
        switch_dict = {}
        for host in host_status_dict:
            online = host_status_dict[host]
            if not host in fail_num_dict:
                fail_num_dict[host] = 0
            if not host in init_status_dict:
                init_status_dict[host] = None
            init_online = init_status_dict[host]

            init_status_dict[host] = online
            if init_online == None:
                switch_dict[host] = f'{online}'
            else:
                if online != init_online:
                    # switch_dict[host] = f'{init_online} -> {online}'
                    switch_dict[host] = f'{init_online} &#8594 {online}'
                else:
                    switch_dict[host] = f'{online}'
            fail_num = fail_num_dict[host]
            if not online:
                os.system(f'echo "[{now}] {host} is {On_Red}offline{NC}"')
                fail_num += 1
                fail_num_dict[host] = fail_num
                if fail_num <= max_fail_times:
                    fail_content = fail_message(host,conf_path)
                    message_dict[host] = fail_content
            else:
                os.system(f'echo "[{now}] {host} is online"')
                if fail_num > 0:
                    fail_num = 0
                    fail_num_dict[host] = fail_num
                    recover_content = recover_message(host,conf_path)
                    message_dict[host] = recover_content
        title, content = gen_message(message_dict,host_status_dict,fail_num_dict,switch_dict,is_init_message,conf_path)
        is_init_message = False
        # print(title, content)
        if title is not None and content is not None:
            content_lines = content.split('\n')
            split_content_dict = {}
            split_content_block_flag = 1
            line_len_sum = 0
            split_content = ''
            for line in content_lines:
                line_len = len(line)
                line_len_sum += line_len
                split_content += line + '\n'

                if line_len_sum >= 900:
                    split_content_dict[split_content_block_flag] = split_content
                    split_content_block_flag += 1
                    line_len_sum = 0
                    split_content = ''
                    continue

            if not len(split_content) == 0:
                split_content_dict[split_content_block_flag] = split_content
            if len(split_content_dict) == 1:
                pushover(title,content,conf_path)
            else:
                for i in range(len(split_content_dict)):
                    content = split_content_dict[i+1]
                    new_title = title + f' ({i+1}/{len(split_content_dict)})'
                    pushover(new_title,content,conf_path)
                    time.sleep(1)
        _, _, _, _, _, _, sleep_time_seconds = get_conf(conf_path)
        os.system(f'echo ------sleep {sleep_time_seconds} seconds------')
        time.sleep(sleep_time_seconds)
def getVersion():
    # firstline = read("__init__.py").splitlines()[0]
    fr = codecs.open(os.path.join(here, "__init__.py"), 'r')
    firstline = fr.readline()
    fr.close()
    ver = firstline.split("'")[1]
    return ver

def getUsage():
    fr = codecs.open(os.path.join(here, "__init__.py"), 'r').read()
    st = False
    usage = ""
    for line in fr.splitlines():
        if st and not line.startswith('"""'):
            usage += line + "\n"
        if line.startswith('__usage__'):
            st = True
        if st and line.startswith('"""'):
            break
    if not st:
        raise RuntimeError("Unable to find usage string.")
    else:
        return usage

def create_service(conf_path):
    if not conf_path.startswith('/'):
        cwd = os.getcwd()
        conf_path = os.path.join(cwd, conf_path)
    if not os.path.exists(conf_path):
        gen_conf(conf_path)
    bin_path = os.popen('which mypushover').read().strip()
    os.system(f'rm -rf /etc/systemd/system/mypushover.service')
    os.system(f'rm -rf /usr/lib/systemd/system/mypushover.service')
    service_path = '/usr/lib/systemd/system/mypushover.service'
    content = f'''[Unit]
Description=mypushover Startup Script
After=network.target
[Service]
Type=simple
ExecStart={bin_path} -c {conf_path}
[Install]
WantedBy=multi-user.target'''
    with open(service_path,'w') as f:
        f.write(content)

    os.system(f'systemctl daemon-reload')
    os.system(f'systemctl enable mypushover')
    os.system(f'systemctl start mypushover')
    pass

def stop_service():
    os.system(f'systemctl stop mypushover')

def disable_service():
    os.system(f'systemctl stop mypushover')
    os.system(f'systemctl disable mypushover')
    os.system(f'rm -rf /etc/systemd/system/mypushover.service')
    os.system(f'rm -rf /usr/lib/systemd/system/mypushover.service')
    os.system(f'systemctl daemon-reload')
    os.system(f'systemctl reset-failed')

def status_service():
    os.system(f'systemctl status mypushover')

def restart_service():
    os.system(f'systemctl restart mypushover')

def main():
    ver = getVersion()
    print(f'Version: {ver}')
    print(getUsage())
    is_outdated, latest = check_outdated("mypushover", ver)
    if is_outdated:
        print("The package mypushover is out of date. Your version is %s, the latest is %s." % (ver, latest))
    if "-c" in sys.argv:
        conf_path = sys.argv[sys.argv.index("-c") + 1]
    else:
        conf_path = conf_path = os.path.join(here, 'pushover_conf.conf')

    if "-start" in sys.argv:
        create_service(conf_path)
        exit()

    if "-stop" in sys.argv:
        stop_service()
        exit()

    if "-disable" in sys.argv:
        disable_service()
        exit()

    if "-status" in sys.argv:
        status_service()
        exit()

    if "-restart" in sys.argv:
        restart_service()
        exit()

    run(conf_path)

if __name__ == '__main__':
    main()