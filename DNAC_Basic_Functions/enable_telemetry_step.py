
import requests
import json
from requests.auth import HTTPBasicAuth
import time
from colorama import init, Fore, Back, Style
import warnings
requests.packages.urllib3.disable_warnings()


init(convert=True)
class Test_API_DNA():



    def __init__(self):
        self.username = 'admin'
        self.password = 'Maglev123'
        self.server_dna_ip = '10.56.216.87'
        self.test_api_telemetry()



    def test_api_telemetry(self):

        ### Login ####
        login = requests.get('https://' + self.server_dna_ip + '/api/system/v1/auth/login', auth=HTTPBasicAuth(username=self.username,password=self.password), verify= False )
        response = requests.post('https://' + self.server_dna_ip+ '/api/system/v1/auth/token' ,  auth=HTTPBasicAuth(username=self.username,password=self.password), verify= False )
        response_dict = json.loads(response.text)
        self.sessionId = response_dict['Token']

        # Enable Telemetry #
        url = 'https://' + self.server_dna_ip+ '/api/v1/commonsetting/global/-1'
        headers = {"Content-Type": "application/json", "X-Auth-Token": self.sessionId}
        parent_site = requests.get(url=url, headers=headers, verify=False,params={"groupNameHierarchy":"Global"}).content
        instance_uuid = json.loads(parent_site)['response'][6]['instanceUuid']

        params_telemetry =  [{"instanceType":"netflow","instanceUuid":instance_uuid,"namespace":"global",
                              "type":"netflow.setting","key":"netflow.collector","version":7,"value":[{"configureDnacIP":true,"ipAddress":"","port":""}],
                              "groupUuid":"-1","inheritedGroupUuid":"","inheritedGroupName":""}]

        create_a_site = requests.post(url=url, headers=headers, verify=False,data=json.dumps(params_telemetry))




if __name__== "__main__":
    Test_API_DNA()