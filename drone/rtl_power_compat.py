#!/usr/bin/python3
# -*- coding: utf-8 -*

import socket
import sys

IP_ADDRESS = "192.168.1.5"
PORT_NO = 7576

serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind((IP_ADDRESS, PORT_NO))

encoding = 'utf-8'

while True:
    data, addr = serverSock.recvfrom(655650)
    sys.stdout.write(data.decode(encoding))

