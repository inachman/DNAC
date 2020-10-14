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
        self.ipdna ='10.56.197.243'
        self.username = 'maglev'
        # self.password = getpass.getpass(prompt="Please Enter Your Password:")
        self.password =  'Maglev123'
        self.port = 2222
        self.application_names = input("Please Insert Specific ApplicationName or Just Press Enter For All Applications:")
        self.exporterIpAddress = input("Insert the Exporter IP Address Device or Just Press Enter For All Exporters:")
        self.range_range_gte = int(input("Insert a Minutes:"))
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

                            if self.range_range_gte== "" :
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
                                            "gte":time.mktime(datetime.datetime.strptime(str((datetime.datetime.now()-datetime.timedelta(minutes=self.range_range_gte)).strftime('%Y-%m-%d %H:%M:%S')),
                                             '%Y-%m-%d %H:%M:%S').timetuple())*1000,
                                            "lte":time.mktime(datetime.datetime.strptime(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                                             '%Y-%m-%d %H:%M:%S').timetuple())*1000
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


if __name__ == "__main__":
    Assurance_Troubleshoting()















