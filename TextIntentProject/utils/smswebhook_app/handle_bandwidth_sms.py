from requests import request as SEND_REQUEST
import json 
from time import sleep


class BANDWIDTH:
    def __init__(self):
        self.headers = {
                'Authorization': 'Basic RGhhdmFsOjVpZW5RbFl6MW5lRFUxVW1ZeU5DRXRMU28=',
                'Content-Type': 'application/json'
            }
        self.messaging_url = 'https://messaging.bandwidth.com/api/v2/users/5006890/messages'
        
        
    def SendSMS(self, data):
        for i in range(3):
            payload = json.dumps(data)
            response = SEND_REQUEST("POST", self.messaging_url, headers=self.headers, data=payload)
            if response.status_code == 202: return True
            sleep(2)
            continue
        return False 
    
    
    