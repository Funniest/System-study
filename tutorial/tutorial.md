# tutorial
### CSAW 2016
***tutorial은 CSAW 2016에 출제된 문제입니다.***

tutorial을 실행시 에러가 났었는데 저는 아래 방법으로 해결했습니다.
```
user add를 이용하여 tutorial 계정을 만들어 주어야합니다.

그 후 sudo ./tutorial [PORT]으로 실행해 주면 잘 되더라구요 :)
```

tutorial에 접속하면, 아래 그림과 같이 3가지 선택지가 나옵니다.

![Alt text]()

여기서 1번 메뉴는 아래와 같이 puts의 주소를 뿌려줍니다. ㄱㅇㄷ

![Alt text]()

2번 메뉴는 오버플로우가 일어나는 선택지 입니다.

![Alt text]()

sub rsp, 150 -> 0x150만큼 버퍼 생성

[rpb+s] -> 0x140부터 입력을 받기 시작합니다.

[rbp+var_8] -> Canary

정리해 보면 0x138(buf) + canary(8) + SFP(8) = 0x148(328)만큼 받고, 입력은 0x1CC만큼 받습니다.

└ read(fd, buf, 0x1CC)

필요한 가젯들과 시나리오를 정리하기 전 제가 몰랐던 것을 잠깐 적고 넘어가겠습니다.

### Calling Convention
```
32bit는 함수를 콜할때 스택을 써서 pop ret가젯을 사용합니다.
하지만 64bit는 32bit와 다르게 레지스터를 이용하여 함수를 콜합니다.
순서는 다음과 같습니다.
1. RDI
2. RSI
3. RDX
4. RCX
5. R8
6. R9
와 같은 순으로 넣어준 뒤 콜을 해야합니다.

반면 64bit윈도우 에서의 순서를 보겠습니다.
1. RCX
2. RDX
3. R8
4. R9
와 같은 순으로 받고 그 이상은 스택을 사용합니다.
```

### Stack frame
```
32bit의 stack frame은 함수가 실행될 때 그 함수가 사용하는 만큼 스택을 생성했었습니다.
이 부분은 아직 잘 이해가 안가는 부분인데, 64bit의 Stack frame은
함수에서 필요한 스택 크기보다 크게 스택을 확보한다고 합니다.
다른 서브 함수를 호출할 때에는 push명령을 상요했던 것과 다르게
생성된 스택에 mov명령을 이용하여 전달한다고 합니다.
또한 Stack frame을 구성할 때에도 RBP레지스터를 이용하지않고, RSP 레지스터를 이용하여 구현합니다.

[참고] 
```

### Gadget 잘라쓰기
![Alt text]()

만약 위 처럼 pop x 7 ret이 있다고 해서 필요한 가젯이 ppr이면 아래 그냥 ppr만 때어 썻는데,

저 가젯에서 만약 나는 pop rdi가젯이 필요해! 라고 한다면, 0x21102주소를 넣어주면 됩니다.

이렇게 되면 옵코드가 5f, c3이 되고 결국에는 pop rdi ret이 되는 것 입니다.

### libc파일에서 가젯 offset가져와 libc base주소에 더해버리기!
libc파일의 가젯들을 사용할 수 있다는 사실을 오늘 처음 알았습니다...

그냥 단순히 함수 offset가져와 더해버리면 없는 함수도 실행할수 있구나.. 라고 생각했는데,

이번 문제를 풀면서 libc안에 있는 pop ret가젯들도 전부 사용할 수 있다는 것을 알게되었습니다. (놀람!!)

***신기 방기XD***

이것 저것 많이 알게되서 정말 좋았던것 같습니다 :) !!

이제 익스플로잇 가젯들을 정리해 보면,
```
1. Canary
2. libc base address
3. read plt
4. write plt
5. puts got
6. libc puts offset
7. libc system offset
8. pop rdi
9. pop rsi
10. pop rdx
```
이 필요합니다.

익스플로잇 순서는
```
1. canary를 leak합니다.
2. 익스플로잇에 필요한 가젯들을 구합니다.
3. 구한 가젯들을 조합해서 페이로드를 작성합니다.
      └ menu 1번에서 주는 puts got를 받아 libc system offset과 빼어 libc base를 구합니다.
      └ 구한 libc base에 pop rdi, rsi, rdx과 system의 offset에 더해 실제 주소를 구합니다.
      └ read plt를이용하여 bss영역에 명령어를 씁니다.
      └ 그후 system에 bss를 인자로 주어 호출합니다.
```

***※하루 동안 고생한 부분이 있었는데, puts got를 뿌릴때 -1280을 해서 뿌려서 +1280을 해줘야합니다.***
***※문제에서 libc 2.19를 주는데 풀이 환경에 따라 다릅니다. (아래 명령어를 이용해서 확인)***
```
cat /proc/process nubmer/maps를 하면 로컬에서 어떤 libc쓰는지 보이더라구요!
주현이 땡큐~~
```

### 소스코드
Ubuntu 16 LTS 64 bit환경에서 테스팅 하였습니다.
```
```


