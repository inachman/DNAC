import paramiko
import time
import socket
__author__= "Idan Nachmani - idan.nachmani@gmail.com"

print("Configurator Tool Made By Idan Nachmani - email: idan.nachmani@gmail.com")
print("Please Read the Configurator Tool Document Instructions")
remote_conn_pre = paramiko.SSHClient()
remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ips = [i.strip() for i in open("ip_address_pool.txt")]
commands = [c.strip() for c in open("config_template.txt")]

user_local = input("Please Enter Your Username:")
pass_local = input("Please Enter Your Password:")


g = open('config.txt', 'r+')
str = g.read()
g.close

success = open('success.txt', 'a')
fail = open('failed.txt', 'a')

paramiko.util.log_to_file("paramiko.log")

for ip in ips:
    try:
        remote_conn_pre.connect(ip, username=user_local, password=pass_local, timeout=4, look_for_keys=False, allow_agent=False)
        remote_conn = remote_conn_pre.invoke_shell()
        print ("SSH connection established to %s" + ip)
        print (ip + ' === local credential')
        for com in commands:
            remote_conn.send(com+"\n")
            time.sleep(1)
            output = remote_conn.recv(10000)
            print (output)
    except paramiko.AuthenticationException:
        print (ip + ' === Bad credentials')
        remote_conn3 = remote_conn_pre.invoke_shell()
        output3 = remote_conn3.recv(5000)
        print (output3)
    except paramiko.SSHException:
        print (ip + ' === Issues with ssh service')
    except socket.error:
        print (ip + ' === Device unreachable')