# bookstore
### Codegate 2015
***bookstore은 Codegate 2015에 출제된 문제입니다.***

bookstore를 실행 할 때에는 User가 필요한대 아래 처럼 추가해주시면됩니다!
```
user add명령얼르 이용하여 bookstore계정을 추가해 주어야 됩니다 :)
```

booksotre에 접속하면 멘 처음 아이디와 비밀번호를 입력하라고 나오는데 아래 그림에 바로 나와있습니다 ㄷㄷ..

![Alt text]()

로그인을 하게 되면 아래 처럼 관리 메뉴가 여러가지 나오게 됩니다.

![Alt text]()

여기서 간략하게 매뉴 별로 설명을 하겠습니다.

```
1. Add new item (책을 추가하는 메뉴입니다)
2. Modify the itme(등록된 책 들을 수정하는 메뉴입니다)
    └ 1. Modify Bookname(책 이름 수정)
    └ 2. Modify description(책 설명 수정)
    └ 3. Modify information(책 정보를 모두 수정)
    └ 4. Modify Shipping option(책의 쇼핑 옵션 수정)
    └ 5. Modify Avaliable(판매 여부 수정?)
3. View information(선택한 책의 정보만 보여준다)
4. Show item list(등록된 책 전체의 리스트를 출력해 준다)
```

이제 취약한 메뉴를 알아보겠습니다. 

(이 부분에서 Overflow취약점인줄 알고 2일 삽질 끝에 하루종일 라업보고 겨우 이해했내요...)

![Alt text]()

### Stack Spray(?)

일단 [2. Modify the item]의 메뉴 중 2번 메뉴를 보면 사용하는 값은 300개인데 3000개나 입력받습니다.

여기서 취약점이 일어나게 되는데, 그 이유는 스택에 Description을 수정하기 위해 A를 3000개를 꽉 채운다고 가정하면,

Description에 A가 300개 만큼 사용된 다음 나머지 A들은 스택에 막 뿌려져있습니다.

이 상태로 스택을 사용하게 된다면 A들은 변수의 초기값에 영향을 미치게 되고, 여기있는 Book struct의 초기 값을 조작하여 원하는 함수를 실행시킬 수 있습니다.

자세한 설명은 출제자 님의 블로그에 자세히 나와있습니다.

[출제자님의 블로그] www.blog.sweetchip.kr/374

***이거 이해하는데 하루 꼬박 걸렸내요... ㅠ_ㅠ***

이제 다시 돌아와 위 취약점을 이용해서 조작할 함수는 어디있을지 찾아봅시다.

아래 그림을 보면 함수 포인터를 2개 생성하는데, 여기서 다른 한 함수포인터의 초기화가 진행되지 않는 모습을 볼수 있고 저 함수포인터를 조작하면 원하는 함수를 실행시킬 수 있습니다.

![Alt text]()

그럼 저 함수 포인터가 실행되는 조건은 어떻게 되는지 한번 살펴보겠습니다.

아래 그림과 같이 freeshipping변수가 1로 설정되어있어야 저희가 조작한 함수 포인터가 실행된다는 것을 알 수 있습니다.

![Alt text]()

이제 이것들을 이용해서 원하는 함수 값을 [2. Modify the item]을 이용하여 스택을 꽉꽉 채운 뒤 수정해서 실앻시키면 될 것 같지만 PIE라는 기법 때문에 불가능합니다.

### PIE

PIE란 리눅스 시스템의 보호 기법중 하나로 ALSR같은 경우에는 스택의 주소를 랜덤으로 바꾸지만, PIE는 코드 영역의 주소를 랜덤하게 바꿉니다.

그럼 PIE는 어떻게 우회할까요?

릭을 통해 주소를 가져오는 방법이있습니다.

아래 그림을 보면서 대강 구조체의 구조를 알 수 있었습니다. (View Information의 호출부와 내부를 비교하면서 찾았습니다!)

![Alt text]()

```
bookID(4) 
type(4)
name(20)
price(4)
stock(4)
descriptionFuncAddr(4)
shipping(4)
shippingFuncAddr(4)
maxDownload(4)
avliavle(4)
description(300)

```

***아직 구조체 보는게 익숙하지 않아서 라이트 없을 보지 않았더라면 시간이 조금 오래걸리는 작업이였을 것 같습니다ㄷㄷ;;***

Name을 20byte채우고, price와 stock을 모두 채우면 description Function Address가 leak이 되고 이것을 통해 base주소를 알 수 있습니다! ㄱㅇㄷ

자 마지막으로 flag파일을 읽을만한 함수가 필요한데, Login 함수에 가보면 file을 rade하는 함수가 있는데 사용하면 될것 같습니다.

![Alt text]()

이제 시나리오를 정리해 봅시다.

```
1. Add new item으로 item을 하나 만듭니다(이때 type는 0)
2. Modify the item의 [3. Modify information]을 통해 name 20byte, price, stock을 NULL Byte없이 꽉꽉 채워줍니다.
3. Show item list메뉴를 이용하여 description function address를 leak해 와서 ida에서 본 offset을 빼서 BASE주소를 구하고, file read의 주소를 구합니다.
4. Modify the time의 [2. Modify Description]을 통해 구한 주소를 3000게 꽉꽉채워 스택에 막 뿌려줍니다.
5. 이어서 [3. Modify Information]을 이용하여 구조체 전체를 수정합니다. (수정방식이 memcpy를 이용한 복사 붙여 넣기 방식이므로 초기값도 다시 설정됨)
6. 그 후 [4. Modify Shipping option]을 1로 설정해 줍니다. (1이여야지만 조작한 함수 포인터가 실행됩니다.)
7. 마지막으로 View information을 통해 조작한 아이템을 선택하면 됩니다.
```

익스플로잇에 필요한 가젯들을 정리해 보겠습니다.
```
1. file read 함수의 offset
2. print description function의 offset
```

***이 문제를 푸는데 4일이라는 시간이 걸렸는데, 잘 못알았던 것을 바로잡고, 새로운 것들을 알게되서 좋았던 것 같습니다 :)***

***아직 구조체나 조금 소스가 복잡해 지면 보기가 힘들어서 더 많이 경험해 봐야 할것 같습니다 ㅠ_ㅠ***

### 소스코드
Ubuntu 16 LTS 64bit 환경에서 테스팅 하였습니다.
```

```
