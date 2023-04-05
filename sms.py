import requests
import json
import time
from datetime import datetime
import base64

import logging

USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1'

class PauseException(Exception):
    def __init__(self,msg):
        self.msg = msg

    def __str__(self):
        return f'PauseException: {self.msg}'


class NetworkException(Exception):
    def __init__(self,msg):
        self.msg = msg

    def __str__(self):
        return f'NetworkException: {self.msg}'

class LoginException(Exception):
    def __init__(self,msg):
        self.msg = msg

    def __str__(self):
        return f'LoginException: {self.msg}'

class DeleteException(Exception):
    def __init__(self,msg):
        self.msg = msg

    def __str__(self):
        return f'DeleteException: {self.msg}'


class SMS:

    def __init__(self, ip_address, password):
        self.password = password
        self.ip_address = ip_address
        self.form_headers = {
                        'Content-type': 'application/x-www-form-urlencoded',
                        'User-Agent': USER_AGENT,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'Accept-Encoding':'gzip, deflate, br',
                        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                        'Referer': f'http://{self.ip_address}/index.html'
                        }
        self.session = requests.session()

    def login(self):
        response = self.session.post(url=f'http://{self.ip_address}/goform/goform_set_cmd_process',
                            data = {
                            'goformId': 'LOGIN',
                            'password': base64.b64encode(self.password.encode("ascii")),
                            'isTest': 'false',
                            }, headers = self.form_headers)

        #logging.info(response.status_code)
        if (json.loads(response.text)['result'] != '0'):
            raise LoginException('Incorrect Password')
        return 0


    def send_sms(self,phone,message):
        umessage = message.encode('utf-16').hex()

        response = self.session.post(url=f'http://{self.ip_address}/goform/goform_set_cmd_process',
                data = {
                        'goformId': 'SEND_SMS',
                        'Number': phone,
                        'MessageBody':umessage,
                        'encode_type' : 'UNICODE',
                        'notCallback':'true',
                        'ID':'-1',
                        'isTest': 'false',
                        }, headers = self.form_headers)


        #logging.info(response.status_code)
        return json.loads(response.text)

    def get_sms(self):
        response = self.session.post(url=f'http://{self.ip_address}/goform/goform_get_cmd_process',
                            data = {
                            'order_by': 'order by id desc',
                            'tags': '10',
                            'mem_store':'1',
                            'data_per_page' : '500',
                            'page':'0',
                            'cmd':'sms_data_total',
                            'isTest': 'false',
                            }, headers = self.form_headers)
        #logging.info(response.status_code)
        return json.loads(response.text)

    def del_sms(self, id):
        response = self.session.post(url=f'http://{self.ip_address}/goform/goform_set_cmd_process',
                        data = {'isTest': 'false',
                                'goformId': 'DELETE_SMS',
                                'msg_id': id,
                                'notCallback': 'true'}, headers = self.form_headers)

        if (json.loads(response.text)['result'] != 'success'):
            raise DeleteException(f'Failed to Delete SMS id {id}')

        return 0




def main():
    logging.basicConfig(format='%(name)s %(levelname)s: %(asctime)s: %(message)s', level=logging.INFO)

    try:

        sms = SMS('192.168.0.1','admin')
        response = sms.login()
        logging.info(f"Login Response {response}")
        res = sms.send_sms('07753xxxxx','I HOPE THIS WORKS!')
        logging.info(f"{res}")
        messages = sms.get_sms()
        #logging.info(f"{messages}")
        for msg in messages['messages']:
            id = msg['id']
            try:
                number = msg['number']
                content = bytes.fromhex(msg['content']).decode('utf-8')
                logging.info(f"id: {id} number: {number} message: '{content}'")
            except Exception as de:
                logging.info(f"????{de} id = {id}")

            print("Deleting...",id)
            dresponse = sms.del_sms(id)
            logging.info(f"Delete Response {dresponse}")


    except Exception as e:
        logging.info(f"????{e}")
    finally:
        exit()

if __name__ == '__main__':
    main()
