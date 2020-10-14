import paramiko
from elasticsearch import Elasticsearch, exceptions
import json, time
import re
import time
import datetime
import subprocess
import sys
#from netmiko import ConnectHandler
from colorama import init, Fore, Back, Style
import getpass
init(convert=True)


__author__ = 'inachman'


class Assurance_Troubleshoting:
    def __init__(self):


        # ascii_banner = pyfiglet.figlet_format("Assurance TS !!")
        print(Fore.CYAN ,"Assurance TS !!, __author__ = inachman@cisco.com")
        #### Credentials IP/Username/Password

        print(Fore.GREEN ,"1. Elastic Search - Collect Flowmetric By 5 minutes Label- nfAppMetricAggregation_5_min/nfMetricAggregation_5_min")
        print(Fore.WHITE,"2. TCPDUMP FNF Traffic - Confirm and Capture Traffic on Port 6007")
        print(Fore.WHITE,"3. Confirm That Performance Monitory / Flow Monitor Is Implemented on Device Switch/Router")
        print(Fore.GREEN,"4. Collect Elastic Search Information by 1 Hour Label -nfAppMetricAggregation_element_PT1H_PT1H ")
        print(Fore.WHITE,"5. Confirm that Clock is Sync on Both Device & DNA Cluster ")
        print(Fore.WHITE,"6. CAPTURE Traffic with TCPDUMP command on the DNAC Server ")
        print(Fore.WHITE,"7. Exit from Assurance Script")

        selection = int(input("Enter Choice: "))
        if selection == 1:
            self.collect_flowmetrics_from_elastic()
            anykey = input("Enter anything to return to main menu")
            self.__init__()
        elif selection == 2:
            self.capture_fnf_traffic_confirm_that_received_traffic_port6007()
            anykey = input("Enter anything to return to main menu")
            self.__init__()
        elif selection == 3:
            self.fnf_confirm_on_device()
            anykey = input("Enter anything to return to main menu")
            self.__init__()
        elif selection == 4:
            self.collect_flowmetrics_from_elastic_1_hour()
            anykey = input("Enter anything to return to main menu")
            self.__init__()
        elif selection == 5:
            self.ntp_confirm_on_devices()
            anykey = input("Enter anything to return to main menu")
            self.__init__()
        elif selection == 6:
            self.capture_fnf_traffic_confirm_that_capture_traffic_port6007()
            anykey = input("Enter anything to return to main menu")
            self.__init__()
        elif selection == 7:
            print("Exit From Script")
        else:
            print("Invalid Choice.Enter 1-7")
            self.__init__()


    def ssh_expose_port_elastic(self):
        # Step1: SSH To the DNA Server #
        ssh_client = paramiko.SSHClient()
        # ssh_client
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(self.ipdna, self.port, self.username, self.password)  # This is used to establish a connection
        except Exception:
            print(Fore.RED,"Connection Error , please check your DNA IP/ Username/Password")
            self.__init__()

        ### Present Connectivity ####
        remote_connection = ssh_client.invoke_shell()
        output = remote_connection.recv(1000).decode("utf-8")
        print(output)

        # Step2: Expose port for connecting the Grafana Service #
        remote_connection = ssh_client.invoke_shell()
        remote_connection.send("magctl service expose elasticsearch-0 --appstack ndp 9200\n")
        time.sleep(10)
        output = remote_connection.recv(10240)
        output_expose = output.decode("utf-8")
        print(output_expose)
        find_exposed_port = re.search(r"(?<=port:)(\d.*)",output_expose)
        if find_exposed_port:
            exposed_port = find_exposed_port.group(1)
        print('The Expose port for Elastic Search is:' +exposed_port)
        return exposed_port.rstrip()

### Step 1 Troubleshoting to confirm that Elastic Serach have the information Required ###
    def collect_flowmetrics_from_elastic(self):
        # ascii_banner = pyfiglet.figlet_format("Step 1 - ElasticSearch ")
        print("Step 1 - ElasticSearch ")
        self.ipdna =input("Enter Your DNA Cluster IP Address:")
        self.username = input("Enter Your Username:")
        # self.password = getpass.getpass(prompt="Please Enter Your Password:")
        self.password =  getpass.getpass("Enter your Password:")
        self.port = 2222
        self.application_names = input("Please Insert Specific ApplicationName or Just Press Enter For All Applications:")
        self.exporterIpAddress = input("Insert the Exporter IP Address Device or Just Press Enter For All Exporters:")
        self.range_range_gte = input("Insert Start Range(Convention Need to Be Year-Month-Day & Hours:Minutes:Seconds) or Just Press Enter For Getting Existing Applications in the Last 15 Minutes:")
        self.range_range_lte = input("Insert End Range(Convention Need to Be Year-Month-Day & Hours:Minutes:Seconds)or Just Press Enter For Getting Existing Applications in the Last 15 Minutes:")
        self.numberofresults = input("Insert the Number of Results you are looking for(Example: 5,10 ,20 ,50) or Just Press Enter For Getting 10 Results:")
        self.label = input("Insert label nfAppMetricAggregation_5_min or Just press Enter for nfMetricAggregation_5_min:")

        # create a timestamp using the time() method
        start_time = time.time()
        DOMAIN = self.ipdna
        PORT = self.ssh_expose_port_elastic()
        # concatenate a string for the client's host paramater
        host = str(DOMAIN) + ":" + str(PORT)
        # declare an instance of the Elasticsearch library
        client = Elasticsearch(host)



        try:
            # use the JSON library's dump() method for indentation
            info = json.dumps(client.info(), indent=4)

            # pass client object to info() method
            print("Elasticsearch client info():", info)

        except exceptions.ConnectionError as err:

            # print ConnectionError for Elasticsearch
            print("\nElasticsearch info() ERROR:", err)
            print("\nThe client host:", host, "is invalid or cluster is not running")

            # change the client's value to 'None' if ConnectionError
            client = None



        # valid client instance for Elasticsearch
        if client != None:

            # get all of the indices on the Elasticsearch cluster
            all_indices = client.indices.get_alias("*")

            # keep track of the number of the documents returned
            all_docs = {}
            # iterate over the index names
            for ind in all_indices:
                # Check if the FlowMetric Index Existing
                if "flowmetric"  in ind.lower():
                    try:
                        all_docs = {ind}
                        print("\nindex name:", ind)
                        doc_count = 0

                        for num, index in enumerate(all_docs):
                            # declare a filter query dict object
                            if self.application_names == "":
                                application_names = {"match_all": {}}
                            else:
                                application_names = {"match":{ "applicationName": self.application_names}}

                            if self.exporterIpAddress == "":
                                exporter_address = {"match_all": {}}
                            else:
                                exporter_address = {"match": {"exporterIpAddress": self.exporterIpAddress}}

                            if self.range_range_gte== "" and self.range_range_lte == "":
                                range_time ={"range": {
                                            "~modificationtime": {
                                            "gte":time.mktime(datetime.datetime.strptime(str((datetime.datetime.now()-datetime.timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')),
                                             '%Y-%m-%d %H:%M:%S').timetuple())*1000,
                                            "lte":time.mktime(datetime.datetime.strptime(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                                             '%Y-%m-%d %H:%M:%S').timetuple())*1000

                                                }
                                            }
                                        }
                            else:
                                range_time = {
                                    "range": {
                                        "~modificationtime": {
                                            "gte": time.mktime(datetime.datetime.strptime(self.range_range_gte,
                                            '%Y-%m-%d %H:%M:%S').timetuple()) * 1000,
                                            "lte": time.mktime(datetime.datetime.strptime(self.range_range_lte,
                                          '%Y-%m-%d %H:%M:%S').timetuple()) * 1000
                                        }
                                    }
                                }

                            if self.numberofresults == "":
                                numberofresults = str(10)
                            else:
                                numberofresults = self.numberofresults



                            if self.label == "":
                                label_name = {"match_all": {}}
                            else:
                                label_name = {"match":{ "~label":self.label}}




                            match_all = {
                                "sort": {"timestamp": "desc"},
                                "query": {"bool":
                                {"must": [

                                    #### Add % minutes Aggregation ####
                                    label_name,
                                    application_names,
                                    exporter_address,
                                    range_time,
                                                        ],


                                               "must_not": [],


                                                    "should": []}}, "from": 0,
                                "size": numberofresults,
                                "sort": [],
                                "aggs": {}

                            }

                            # make a search() request to get all docs in the index
                            resp = client.search(
                                index=index,
                                body=match_all,
                                scroll='2s'  # length of time to keep search context
                            )


                            # print the response results
                            print("\nresponse for index:", index)
                            print("_scroll_id:", resp['_scroll_id'])
                            print('response["hits"]["total"]["value"]:', resp["hits"]["total"]["value"])


                            date = datetime.datetime.now()
                            filename = "Elastic_Search_STEP1-{}.txt".format(date.strftime("%d-%B-%Y-%H-%M-%S"))


                            with open(filename, 'a') as the_file:
                                # iterate over the document hits for each 'scroll'
                                for doc in resp['hits']['hits']:
                                    print("\n", doc['_id'], doc['_source'], )
                                    an = ("\n", doc['_id'], doc['_source'],)
                                    print( "applicationName:",Fore.RED +  an[2]['applicationName'])
                                    doc_count += 1
                                    print(Fore.WHITE,"DOC COUNT:", doc_count)
                                    # print the total time and document count at the end
                                    print("\nTOTAL DOC COUNT:", doc_count)
                                    line1 = str(doc['_id']) + " " + str(doc['_source'])
                                    line2 = "TOTAL DOC COUNT: " + str(doc_count)
                                    the_file.write(line1)
                                    the_file.write('\n')
                                    the_file.write(line2)
                                    the_file.write('\n')






                    except exceptions.NotFoundError as err:
                        print("exceptions.NotFoundError error for", ind, "--", err)



### Step 2 Troubleshoting to confirm that FNF Is Recived onthe DNA server port 6007 ###


    def capture_fnf_traffic_confirm_that_received_traffic_port6007(self):
        # ascii_banner = pyfiglet.figlet_format("Step 2 - FNF Traffic Server ")
        print("Step 2 - FNF Traffic Server ")
        self.ipdna =input("Enter Your DNA Cluster IP Address:")
        self.username = input("Enter Your Username:")
        self.password = getpass.getpass(prompt="Please Enter Your Password:")
        input_exporter_device = input("Please Enter The Exporter IP Address Device:")
        self.port = 2222
        # Step1: SSH To the DNA Server #
        ssh_client = paramiko.SSHClient()
        # ssh_client
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(self.ipdna, self.port, self.username,
                           self.password)  # This is used to establish a connection

        ### Present Connectivity ####
        remote_connection = ssh_client.invoke_shell()
        output = remote_connection.recv(1000).decode("utf-8")
        print(output)

        command_ip_address = "ip a | grep" +  ' ' + (self.ipdna)
        print("=" * 50, command_ip_address, "=" * 50)
        stdin, stdout, stderr = ssh_client.exec_command(command_ip_address)
        output_ip_address = stdout.read().decode("utf-8").strip()
        print(output_ip_address)
        find_interface = re.search(r"(?<= global )(.*)",output_ip_address)
        interface_name =  find_interface.group(1)
        command_tcpdump_fnf = "sudo timeout 30 tcpdump -i {} ".format(interface_name)  + "host" + " " + input_exporter_device  + " " +  "and -n udp port 6007 -T cnfp"
        command_sudo = "echo {} | sudo -S ".format(self.password) + command_tcpdump_fnf
        stdin, stdout, stderr = ssh_client.exec_command(command_sudo)
        print("=" * 50, command_sudo , "=" * 50)

        date = datetime.datetime.now()
        filename = "DNAC_FNF_STEP2-{}.txt".format(date.strftime("%d-%B-%Y-%H-%M-%S"))

        output = stdout.read().decode("utf-8").strip()

        with open(filename, 'a') as the_file:
            the_file.write(output)

        print(output)

        ### Step 3 Troubleshooting to confirm that FNF Is Implemented on device as expected ###

    def fnf_confirm_on_device(self):
        # ascii_banner = pyfiglet.figlet_format("Step 3 - FNF Traffic Router and Switch")
        print("Step 3 - FNF Traffic Router and Switch")

        try:
            ipaddress_input = input("Enter your IP Device:")
            username_input = input("Enter your Username Device:")
            password_input = input("Enter your Password Device:")
            # enable_password_input = input("Enter your Enable Password Device , If No Enable Please just Press Enter:")
            date_time = datetime.datetime.now().strftime("%d-%B-%Y-%H-%M-%S")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ipaddress_input, port=22, username=username_input, password=password_input, look_for_keys=False,
                        timeout=None)
            connection = ssh.invoke_shell()
            connection.send("terminal length 0\n")
            time.sleep(1)
            connection.send("\n")
            connection.send("show flow monitor\n")
            time.sleep(3)
            connection.send("show performance monitor context \n")
            time.sleep(3)
            connection.send("show performance monitor cache detail format table\n")
            time.sleep(3)
            file_output = connection.recv(300000).decode(encoding='utf-8')
            hostname = (re.search('(.+)#', file_output)).group().strip('#')
            print(file_output)
            outFile = open(hostname + "-" + "STEP3" + "-" + str(date_time) + ".txt", "w")
            outFile.writelines(file_output)
            outFile.close()
            ssh.close()
            print("%s is done" % hostname)

        except paramiko.AuthenticationException:
            print("User or password incorrect, Please try again!!!")

    ### Step 4 Collect ElasticSerach Records for 1 Hour ####
    def collect_flowmetrics_from_elastic_1_hour(self):

        # ascii_banner = pyfiglet.figlet_format("Step 4 - ElasticSearch For 1 Hour Records ")
        print("Step 4 - ElasticSearch For 1 Hour Records ")

        self.ipdna =input("Enter Your DNA Cluster IP Address:")
        self.username = input("Enter Your Username:")
        self.password = getpass.getpass(prompt="Please Enter Your Password:")
        self.port = 2222
        self.application_names = input("Please Insert Specific ApplicationName or Just Press Enter For All Applications:")
        self.numberofresults = input("Insert the Number of Results you are looking for(Example: 5,10 ,20 ,50) or Just Press Enter For Getting 10 Results:")

        # create a timestamp using the time() method
        start_time = time.time()
        DOMAIN = self.ipdna
        PORT = self.ssh_expose_port_elastic()
        # concatenate a string for the client's host paramater
        host = str(DOMAIN) + ":" + str(PORT)
        # declare an instance of the Elasticsearch library
        client = Elasticsearch(host)

        try:
            # use the JSON library's dump() method for indentation
            info = json.dumps(client.info(), indent=4)

            # pass client object to info() method
            print("Elasticsearch client info():", info)

        except exceptions.ConnectionError as err:

            # print ConnectionError for Elasticsearch
            print("\nElasticsearch info() ERROR:", err)
            print("\nThe client host:", host, "is invalid or cluster is not running")

            # change the client's value to 'None' if ConnectionError
            client = None

        # valid client instance for Elasticsearch
        if client != None:

            # get all of the indices on the Elasticsearch cluster
            all_indices = client.indices.get_alias("*")
            # keep track of the number of the documents returned
            all_docs = {}
            # iterate over the index names
            for ind in all_indices:
                match_vertex = re.search(r"tsg_ngf_([0-9a-fA-F])*_vertex", ind)
                # Check if the FlowMetric Index Existing
                if match_vertex:
                    try:
                        all_docs = {ind}
                        print("\nindex name:", ind)
                        doc_count = 0

                        for num, index in enumerate(all_docs):
                            # declare a filter query dict object

                            if self.application_names == "":
                                application_names = {"match_all": {}}
                            else:
                                application_names = {"match": {"applicationName": self.application_names}},

                            if self.numberofresults == "":
                                numberofresults = str(10)
                            else:
                                numberofresults = self.numberofresults

                            label_name = {"wildcard": {"~label": "nfAp*"}}

                            match_all = {
                                "sort": {"timestamp": "desc"},
                                "query": {"bool":
                                    {"must": [

                                        #### Add % minutes Aggregation ####
                                        label_name,
                                        application_names,
                                    ],

                                        "must_not": [],

                                        "should": []}}, "from": 0,
                                "size": numberofresults,
                                "sort": [],
                                "aggs": {}

                            }

                            # make a search() request to get all docs in the index
                            resp = client.search(
                                index=index,
                                body=match_all,
                                scroll='2s'  # length of time to keep search context
                            )

                            # print the response results
                            print("\nresponse for index:", index)
                            print("_scroll_id:", resp['_scroll_id'])
                            print('response["hits"]["total"]["value"]:', resp["hits"]["total"]["value"])

                            date = datetime.datetime.now()
                            filename = "Elastic_Search_STEP4-{}.txt".format(date.strftime("%d-%B-%Y-%H-%M-%S"))

                            with open(filename, 'a') as the_file:
                                # iterate over the document hits for each 'scroll'
                                for doc in resp['hits']['hits']:
                                    print("\n", doc['_id'], doc['_source'], )
                                    doc_count += 1
                                    print("DOC COUNT:", doc_count)
                                    # print the total time and document count at the end
                                    print("\nTOTAL DOC COUNT:", doc_count)
                                    line1 = str(doc['_id']) + " " + str(doc['_source'])
                                    line2 = "TOTAL DOC COUNT: " + str(doc_count)
                                    the_file.write(line1)
                                    the_file.write('\n')
                                    the_file.write(line2)
                                    the_file.write('\n')


                    except exceptions.NotFoundError as err:
                        print("exceptions.NotFoundError error for", ind, "--", err)


    def ntp_confirm_on_devices(self):
        # ascii_banner = pyfiglet.figlet_format("Step 5 - Validate that Clock is Sync on both Device/DNA Cluster")
        print("Step 5 - Validate that Clock is Sync on both Device/DNA Cluster")

        try:
            cisco_3x = {
                'device_type': 'cisco_ios_telnet',
                'ip': input("Enter your IP Device ( SSH Protocol): "),
                'username': input("Enter your Username: "),
                'password': input("Enter your Password: "),
                'secret': input("Enter you Enable Password: "),
            }
            mansingh = ConnectHandler(**cisco_3x)
            mansingh.enable()
            output = mansingh.send_command("show clock")
            print (output)

        except paramiko.AuthenticationException:
            print("User or password incorrect, Please try again!!!")
            self.ntp_confirm_on_devices()


        try:
            self.ipdna = input("Enter Your DNA Cluster IP Address:")
            self.username = input("Enter Your Username:")
            self.password = getpass.getpass(prompt="Please Enter Your Password:")
            self.port = 2222
            # Step1: SSH To the DNA Server #
            ssh_client = paramiko.SSHClient()
            # ssh_client
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(self.ipdna, self.port, self.username,
                               self.password)  # This is used to establish a connection

            command_ip_address = "date"
            stdin,stdout, stderr = ssh_client.exec_command(command_ip_address)
            output_ip_address = stdout.read().decode("utf-8").strip()
            print(output_ip_address)


        except paramiko.AuthenticationException:
            print("User or password incorrect, Please try again!!!")
            self.ntp_confirm_on_devices()

        ### Step 6 Capture traffic with TCPDUMP command to confirm that FNF Is Recived on the DNA server port 6007 ###
    def capture_fnf_traffic_confirm_that_capture_traffic_port6007(self):
            print("Step 6 - CAPTURE Traffic with TCPDUMP command on the DNAC Server ")
            self.ipdna = input("Enter Your DNA Cluster IP Address:")
            self.username = input("Enter Your Username:")
            self.password = getpass.getpass(prompt="Please Enter Your Password:")
            self.timeout_capture = input("Enter your timeout for the command , Timeout: 0-3600:")
            input_exporter_device = input("Please Enter The Exporter IP Address Device:")
            self.port = 2222
            # Step1: SSH To the DNA Server #
            ssh_client = paramiko.SSHClient()
            # ssh_client
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(self.ipdna, self.port, self.username,
                               self.password)  # This is used to establish a connection

            ### Present Connectivity ####
            remote_connection = ssh_client.invoke_shell()
            output = remote_connection.recv(1000).decode("utf-8")
            print(output)

            command_ip_address = "ip a | grep" + ' ' + (self.ipdna)
            print("=" * 50, command_ip_address, "=" * 50)
            stdin, stdout, stderr = ssh_client.exec_command(command_ip_address)
            output_ip_address = stdout.read().decode("utf-8").strip()
            print(output_ip_address)
            find_interface = re.search(r"(?<= global )(.*)", output_ip_address)
            interface_name = find_interface.group(1)
            print("The Following command will capture the FNF Traffic sending by device to the DNA Cluster , "
                  "This capture command will execute for 360 seconds, "
                  "Once it's completed you will find the capture file on your cluster in the following path:/home/maglev/FNF_Capture.pcap ")
            command_tcpdump_fnf = "sudo timeout" " " + self.timeout_capture + " " + " tcpdump -i {} ".format(
                interface_name) + "host" + " " + input_exporter_device + " " + "and -n udp port 6007 -T cnfp  -w /home/maglev/FNF_Capture.pcap"

            command_sudo = "echo {} | sudo -S ".format(self.password) + command_tcpdump_fnf
            stdin, stdout, stderr = ssh_client.exec_command(command_sudo)
            print("=" * 50, command_sudo, "=" * 50)

            date = datetime.datetime.now()
            filename = "DNAC_FNF_STEP6-{}.txt".format(date.strftime("%d-%B-%Y-%H-%M-%S"))

            output = stdout.read().decode("utf-8").strip()

            with open(filename, 'a') as the_file:
                the_file.write(output)
            print(output)


if __name__ == "__main__":
    Assurance_Troubleshoting()















