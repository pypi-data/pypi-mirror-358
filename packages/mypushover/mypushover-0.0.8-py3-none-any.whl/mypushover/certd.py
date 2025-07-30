# coding=utf-8
import os
import requests

def pushover():
    # return
    # host_server_name, APP_TOKEN, USER_KEY, server_ip_name_dict, max_fail_times,_,_ = get_conf(conf_path)
    print('title----------','Certd')
    print('message----------','Certd completed')
    # return

    try:
        r = requests.post(
            'https://api.pushover.net/1/messages.json',
            data={
                'token': 'acbxawo8uw1t6yfzkwgcvtmdgr2us3',
                'user': 'ui8on6iedb3t7e4n1dgh22q6524m52',
                'message': 'Certd completed',
                'title': 'Certd',
            },
        )
        # print(r.content)
    except Exception as e:
        os.system(f'echo "{e}"')

pushover()
