# Ropasaurusrex
### Plaid CTF 2013
***Ropasaurusrex는 p CTF 2013의 문제입니다.***

ropasaurusrex를 처음 실행해 보면, 입력을 받은뒤  WIN이라는 글자와 함께 종료되는 모습을 볼 수 있습니다.

### Main
![Alt text](https://github.com/Funniest/System-study/blob/master/ropasaurusrex/img/Main.PNG)

### Vuln Funtion
![Alt text](https://github.com/Funniest/System-study/blob/master/ropasaurusrex/img/Funciotn.PNG)

sub esp, 98 -> 0x98 만큼 버퍼 생성

lea eax, [ebp-buf] -> 0x88 부터 입력 버퍼

취약한 함수 = call sub_80483F4

buf의 크기는 총 0x88(136) + SFP = (140)인데, 입력은 0x100(256)만큼 받습니다.

└ read(fd, buf, 0x100)

즉 버퍼오버플로우가 일어나게 됩니다.

이제 익스플로잇에 필요한 가젯들을 정리해 보면,
1. read_plt, read_got
2. write_plt, write_got
3. pppr
4. dynamic_addr -> bss영역을 사용하지 않는 이유는 영역이 작아서 입니다.
5. read - system libc offset
  └ Offset을 구하는 이유는 주소가 가변적으로 바뀌어도 offset은 고정이기 때문에 이 offset에 base주소를 더해 주면, 원래 system주소가 나오기 때문입니다.

read - system을 하여 system의 offset을 구한다음 read_got의 addr를 얻어 구한 system offset을 빼면 원래의 system 주소가 나오게 됩니다.

가젯들을 구할 때에는 objdump -d, -h와 gdb를 이용하여 구하였습니다.

read - system을 하여 offset을 구할 때에는 gdb로 아무데나 b를 걸고 달린후 p system, p read를 이용하여 구해주시면 됩니다.

익스플로잇 순서는
1. 익스플로잇에 필요한 가젯들을 구합니다.
2. 구한 가젯들을 조합하여 페이로드를 작성합니다.
  
  └ write_plt에 read_got를 인자로 주어 로드된 read 주소를 얻어옵니다.

  └ 그 후 read_plt를 이용하여 dynamic섹션에 명령어를 받습니다.

  └ got overwrite를 이용하여 read_got를 구한 system주소를 씁니다.

  └ read_plt(system)에 dynamic섹션 영역을 인자로 주어 실행합니다.

###Got Overwrite?
Got Overwrite란 read, write함수 등 함수들은 plt주소와 got주소를 가지고 있는데,

plt란 외부 프로시저를 연결해주는 테이블 이라고 나와있습니다.

plt를 이용하여 다른 라이브러리에 있는 프로시저를 호출하여 사용하는 것이 가능합니다.

got는 plt가 참조하는 테이블이고, 프로시저들의 주소가 들어있습니다.

이런 plt와 got를 사용하는 이유는 프로그램을 조금 더 가볍게 하기 위해서 입니다.

원래 옛날에 코드를 컴파일 하면, 라이브러리가 프로그램 안에 들어가서 무거워 졌었는데, 지금은 이렇게 링크를 하여 외부 파일에서 함수를 불러와 프로그램이 가벼워 집니다.

이렇게 프로그램안에 모든 함수 주소를 넣는것을 Static link, 외부 파일에서 필요한 함수만 불러오도록 하는 것을 dynamic link라고 합니다.

간단하게 dynamic link 링크 방식은 plt -> got -> 실제 함수주소를 호출하게 됩니다.

[참고] https://bpsecblog.wordpress.com/2016/03/07/about_got_plt_1/

그럼 plt overwrite는 왜 없냐면 plt는 read only속성이기 때문에 overwrite하는게 불가능하기 때문입니다.

###소스코드
Ubuntu 16 LTS 32bit 환경에서 테스팅 해보았습니다.

```
```
