# nuclear
### Codegate2014
***nuclear는 Codegate2014에 출제된 문제입니다.***

nuclear를 실행하려면, THIS_IS_NOT_KEY_JUST_PASSCODE라는 파일이 필요합니다!
```
편집기 명령어를 이용하여, 위 파일을 만들어주신 뒤 안에 아무 값이나 입력하고, 진행하시면 됩니다!~
```

처음 nuclear에 들어가면, Welcome to the nuclear control system이라고 나입니다!

nuclear를 관리하는 시스템 이라는 것을 알 수 있습니다 ㅋㅋ

명령어는 아래 그림과 같이 target, quit, launch세가지 명령어를 지원하는 것을 볼 수 있습니다.

![Alt text]()

한 명령어씩 살펴보자면, quit는 프로그램을 종료하는 명령어입니다!

target명령어는 sscanf를 이용하여 %f/%f 형식으로 값을 입력받는 것을 볼 수 있습니다.

마지막으로 launch는 Passcode를 입력받으면 nuclear를 실행 시킵니다.

nuclear를launch명령어를 실행 시키면, 아래 그림과  같이 나오게 됩니다.

이 때 IF YOU WANT CANCEL THIS CODE OPERATION, ENTE...이라는 말과 함께 CANCEL 코드를 입력받습니다.

이 캔슬 코드를 입력 받는 곳에서 버퍼는 -20C인데, 0x512만큼 입력을 받아 오버플로우가 생기게 됩니다.

![Alt text]()

그럼 시나리오는 PASSCODE를 찾아서 launch에 진입한 뒤 CANCEL CODE를 오버플로우나게 입력하면 됩니다!

그럼 PASSCOEE는 어디에 있을까요?

아래 그림을 보면, THIS IS NOT KEY JUST PASSCOE를 읽어서, [ebp-s]에 저장하는 모습을 볼 수 있습니다.

s는 var_34/38아래 있는 모습을 볼 수 있구요!

직접적으로 PASSCODE를 보여주지 않으니 leak을 이용하여 값을 알아내야 합니다.

leak을 어떻게 해야할까요?

첫 번째로는 알수없는 커멘드를 입력하면 Unkonw command를 출력하며, 자기가 입력한 커멘드를 보여줍니다.

![Alt text]()

이 커맨드를 입력받는 곳은 s1이고 -283에 위치해 있습니다. 그 아래로 var_38, 34가 보입니다.

![Alt text]()

s1을 꽉 채운후 var_38,34가 꽉 차있다면 s가 Unkonw command메시지가 나올 때 깥이 나오겠져?

그럼 var_34, 38은 어떻게 채워야 할까요?

target명령어 안의 sscanf를 이용하여 var_38, 34를 채울 수 있습니다!

저는 처음 sscanf가 뭔지 몰라 릭하는데 조금 해멧었내요!

![Alt text]()

처음 입력받는 곳이 sscanf밖에 없어서 한번 검색을 해보았습니다.

msdn 링크

대충 sscanf동작을 보면, 주어진 buffer에서 정해준 형식대로 입력될 버퍼들에게 전달하는 역할을 하는 함수입니다.

scanf하고 거희 유사해요!

자 그럼 sscanf를 이용하여 34,38부분을 꽉 채우면 PASSCODE를 leak할 수 있습니다!

이제 대강 어떻게 오버플로우를 할 지 알아보았니 본격적으로 익스플로잇 코드를 작성해 보겠습니다.

필요한 준비물은 아래와 같습니다.

```
1. bss address
2. send plt/got
3. recv plt
4. send - system offset
5. ppppr
```

익스플로잇 순서는 다음과 같습니다.
```
1. target 메뉴를 이용하여 var_38, 34의 값을 null없이 채워줍니다.
2. 그 후 0x283만큼 A를 입력하여 s를 null바이트 없이 채워 PASSCODE를 릭합니다.
3. 얻은 passcode로 launch에 접속합니다.
4. CANCLE CODE를 입력받을 때 구한 가젯들을 이용하여 페이로드를 작성합니다.
	└ send_plt로 send_got의 주소를 보냅니다.
	└ 그 후 recv_plt를 이용하여 bss영역에 실행할 명령어를 씁니다.
	└ recv_plt를 이용하여 send_got에 system주소로 덮어씁니다.
	└ 오버라이팅 된 send_got에 bss영역을 주어 호출합니다.
```

### 소스코드
Ubuntu 16 LTS 64bit환경에서 테스팅 해보았습니다.

```

```
