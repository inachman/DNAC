
import requests
import json
from requests.auth import HTTPBasicAuth
import time
from colorama import init, Fore, Back, Style
import warnings
requests.packages.urllib3.disable_warnings()


init(convert=True)


class Test_API_DNA():

    # ascii_banner = pyfiglet.figlet_format("Assurance TS !!")
    print(Fore.CYAN, "Basic Tool To Control DNAC Via REST API Based on Python Script !!, __author__ = inachman@cisco.com/idan.nachmani@gmail.com")
    username = input('Please Insert Your DNA Username(Required admin user that using for the GUI:')
    password = input('Please Insert your DNA Password:')
    server_dna_ip = input('Enter your DNA Cluster IP: ')

    def __init__(self):
        print(Fore.RED, "Multiple Choices - Please following the instructions user guide provided:")
        #### Credentials IP/Username/Password
        print(Fore.WHITE ,"1. Create Your Building Site in DNA Cluster:")
        print(Fore.WHITE ,"2. Add Mult+iple Devices from the ip_address_pool.txt file " )
        print(Fore.WHITE ,"3. Add Multiple Devices To the Site")
        print(Fore.WHITE ,"4. To Exit Application Just Press 4")


        selection = int(input("Enter Choice: "))
        if selection == 1:
            self.test_api_create_a_building_site()
            anykey = input("Enter anything to return to main menu")
            self.__init__()
        elif selection == 2:
            self.test_api_add_device()
            anykey = input("Enter anything to return to main menu")
            self.__init__()
        elif selection == 3:
            self.test_api_add_device_to_site()
            anykey = input("Enter anything to return to main menu")
            self.__init__()
        elif selection == 4:
            print("Exit From Script")
        else:
            print("Invalid Choice.Enter 1-4")
            self.__init__()

    def test_api_create_a_building_site(self):
        self.building_site_name = input('Enter Your Building Site Name:')
        login = requests.get('https://' + self.server_dna_ip + '/api/system/v1/auth/login', auth=HTTPBasicAuth(username=self.username,password=self.password), verify= False )
        response = requests.post('https://' + self.server_dna_ip+ '/api/system/v1/auth/token' ,  auth=HTTPBasicAuth(username=self.username,password=self.password), verify= False )
        response_dict = json.loads(response.text)
        self.sessionId = response_dict['Token']
        # With This Function We will crate a Area Site to the Global Hierarchy "
        # To check if the parent site exist if not create one
        url = 'https://' + self.server_dna_ip+ '/api/v1/group/'
        headers = {"Content-Type": "application/json", "X-Auth-Token": self.sessionId}
        parent_site = requests.get(url=url, headers=headers, verify=False,params={"groupNameHierarchy":"Global"}).content
        site_id = json.loads(parent_site)['response'][0]['id']
        params_site = {"groupTypeList":["SITE"],"parentId":site_id,"childIds":[""],"name":self.building_site_name,"id":"",
        "additionalInfo":[{"nameSpace":"Location","attributes":{"latitude": "1", "longitude": "1",
        "type": "building", "country": "UNKNOWN"}}]}
        create_a_site = requests.post(url=url, headers=headers, verify=False,data=json.dumps(params_site))
        print(Fore.GREEN,'Site {} Has Been Created'.format(self.building_site_name))
        Fore.WHITE


    def test_api_add_device(self):
        login = requests.get('https://' + self.server_dna_ip + '/api/system/v1/auth/login', auth=HTTPBasicAuth(username=self.username,password=self.password), verify= False )
        response = requests.post('https://' + self.server_dna_ip+ '/api/system/v1/auth/token' ,  auth=HTTPBasicAuth(username=self.username,password=self.password), verify= False )
        response_dict = json.loads(response.text)
        self.sessionId = response_dict['Token']
        ips = [i.strip() for i in open("ip_address_pool.txt")]
        username = input('Please Insert the general username of the devices ,Please note that this user need to be unique for al the devices you adding:')
        password = input('Please Insert the general password of the devices, Please note that this user need to be unique for al the devices you adding):')
        enable_password =  input('Please Insert the general enable password of the devices, Please note that this user need to be unique for al the devices you adding):')

        for ip in ips:
            Fore.WHITE
            try:
                url = 'https://' + self.server_dna_ip+ '/api/v1/network-device?onlyValidateCredential =false'
                headers = {"Content-Type": "application/json", "X-Auth-Token": self.sessionId}
                date_device  = {"ipAddress":[ip],"type":"NETWORK_DEVICE","computeDevice":"false","snmpVersion":
                    "v2","snmpROCommunity":"public","snmpRWCommunity":"","snmpRetry":"3","snmpTimeout":"5","cliTransport":
                    "ssh","userName":username,"password":password,"enablePassword":enable_password,"ipv6Enabled":'false'}
                add_device_to_dna = requests.post(url=url, headers=headers, verify=False,data=json.dumps(date_device))
                print(Fore.GREEN,'Device  {} Has Been Added To The Cluster'.format(ip))
                time.sleep(3)

            except AssertionError as error:
                print(Fore.RED,'The Device {} not added'.format(ip) )



    def test_api_add_device_to_site(self):

        # Example API's #
        # 1. Check Site ID - https://10.x.x.x/api/v1/group?groupName?groupNameHierarchy:%Global/Test_Site_Building

        # 2. Check the UUID Device -https://10.x.x.x/api/v1/network-device?instanceUuid

        # 3. Send Post Request - https://10.x.x.x/api/v1/group/3b86bf6d-2d0c-4cd6-9048-356f4443863b/member
        # Body - {"networkdevice":["02f1d97c-b7cb-4e99-8f0f-604f51ba2e1f","0e6c8784-a732-4bed-b1da-6f511b8832a7"]}

        login = requests.get('https://' + self.server_dna_ip + '/api/system/v1/auth/login', auth=HTTPBasicAuth(username=self.username,password=self.password), verify= False )
        response = requests.post('https://' + self.server_dna_ip+ '/api/system/v1/auth/token' ,  auth=HTTPBasicAuth(username=self.username,password=self.password), verify= False )
        response_dict = json.loads(response.text)
        self.sessionId = response_dict['Token']

        #### Get the SiteID ####
        url = 'https://' + self.server_dna_ip + '/api/v1/group/'
        headers = {"Content-Type": "application/json", "X-Auth-Token": self.sessionId}
        response = requests.get(url=url, headers=headers, verify=False,
                                params={"groupNameHierarchy": "Global/" + self.building_site_name}).content
        site_id = json.loads(response)['response'][0]['id']

        #### Get the Device UUID ####
        ips = [i.strip() for i in open("ip_address_pool.txt")]
        url = 'https://' + self.server_dna_ip + '/api/v1/network-device?instanceUuid'
        response = requests.get(url=url, headers=headers, verify=False, ).content
        devices = json.loads(response)
        for device in devices['response']:
            device_uuid = device['instanceUuid']
            device_ip = device['managementIpAddress']
            if device_ip in ips:
                #### Add Device To Site Based on the UUID + SiteID ####
                url = 'https://' + self.server_dna_ip + '/api/v1/group/' + site_id + '/member'
                data_device_uuid = {"networkdevice": [device_uuid]}
                add_device_to_site = requests.post(url=url, headers=headers, verify=False,
                                                   data=json.dumps(data_device_uuid))
                print(Fore.GREEN,'Device  {} Has Been Added To The Site'.format(device_ip))




if __name__== "__main__":
    Test_API_DNA()