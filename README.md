# Mac Agent 🤖

**터미널에서 자연어로 캘린더를 관리하는 AI 어시스턴트**
`version 0.0.2`
Mac Agent는 AutoGen AgentChat을 기반으로 한 지능형 캘린더 관리 시스템입니다. 터미널에서 자연어 명령으로 캘린더 일정을 생성, 조회, 수정, 삭제할 수 있으며, 대화 컨텍스트를 유지하여 연속적인 상호작용이 가능합니다.

## ✨ 주요 기능

### 🗓️ 캘린더 관리
- **일정 생성**: "내일 오후 3시에 회의 일정 추가해줘"
- **일정 조회**: "이번 주 일정 알려줘", "회의 관련 일정 찾아줘"
- **일정 수정**: "회의 시간을 4시로 변경해줘"
- **일정 삭제**: "내일 회의 일정 취소해줘"

### 💬 지능형 대화
- **의도 분류**: 캘린더 관련 요청과 일반 대화 자동 구분
- **컨텍스트 유지**: 터미널별 독립적인 대화 세션 관리
- **자연어 처리**: 복잡한 명령어 없이 자연스러운 대화로 조작

### 🔄 세션 관리
- **터미널별 세션**: 각 터미널 창마다 독립적인 대화 컨텍스트
- **영속성**: 프로세스 종료 후에도 대화 내역 보존
- **다양한 세션 전략**: terminal_pid, system_user, custom, directory, recent

### 🌐 전역 CLI 도구
- **어디서든 사용**: `mac_agent` 명령어로 전역 접근
- **간편한 설치**: 자동 설치 스크립트 제공
- **패키지 관리**: pip를 통한 의존성 자동 관리

## 🏗️ 아키텍처

```
app/
├── main.py                 # 진입점
├── cli/                    # CLI 처리
│   ├── parser.py          # 명령행 파싱
│   └── commands.py        # 명령어 처리
├── agent/                  # 에이전트 관련
│   ├── agent.py           # 메인 에이전트
│   ├── factory.py         # 에이전트 팩토리
│   └── prompt.py          # 프롬프트 관리
├── session/                # 세션 관리
│   ├── manager.py         # 세션 관리자
│   ├── models.py          # 세션 모델
│   └── storage.py         # 세션 저장소
├── memory/                 # 메모리 관리
│   └── manager.py         # 메모리 관리자
├── utils/                  # 유틸리티
│   └── strategies.py      # 세션 전략
├── calendar_tools.py       # 캘린더 도구
├── config.py              # 설정
├── mac_agent              # 전역 CLI 스크립트
├── setup.py               # 패키지 설정
└── install.sh             # 자동 설치 스크립트
```

### 핵심 컴포넌트

- **CalendarManagerAgent**: 메인 에이전트, 의도 분류 및 요청 라우팅
- **SessionManager**: 세션 생성, 조회, 삭제, 전략별 관리
- **MemoryManager**: 메모리 저장, 복원, 대화 내역 관리
- **AgentFactory**: 의도별 전문 에이전트 생성 (캘린더/일반대화/의도분류)
- **SessionStorage**: 파일 기반 세션 영속성

## 🚀 설치 및 설정

### 방법 1: 자동 설치 (권장) ⭐
```bash
# 저장소 클론
git clone <repository-url>
cd mac_agent

# 자동 설치 스크립트 실행
./install.sh
```

자동 설치 스크립트는 두 가지 옵션을 제공합니다:
1. **pip install (권장)**: 전역 설치 및 의존성 자동 관리
2. **심볼릭 링크**: 빠른 설치

### 방법 2: pip install (수동)
```bash
# 저장소 클론
git clone <repository-url>
cd mac_agent

# 의존성 설치
pip install -r requirements.txt

# 전역 설치 (editable mode)
pip install -e .
```

### 방법 3: 심볼릭 링크 (개발자용)
```bash
# 저장소 클론
git clone <repository-url>
cd mac_agent

# 의존성 설치
pip install -r requirements.txt

# ~/.local/bin에 심볼릭 링크 생성
mkdir -p ~/.local/bin
ln -sf "$(pwd)/mac_agent" ~/.local/bin/mac_agent

# PATH에 ~/.local/bin 추가 (필요한 경우)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc  # zsh 사용자
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc # bash 사용자
```

### 환경 설정
```bash
# .env 파일 생성
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 캘린더 권한 설정
macOS에서 캘린더 접근 권한을 허용해야 합니다:
1. 시스템 환경설정 > 보안 및 개인 정보 보호 > 개인 정보 보호
2. 캘린더 선택
3. 터미널 또는 Python 앱에 권한 부여

## 💻 사용법

### 기본 사용법 (전역 설치 후)
```bash
# 직접 명령 실행
mac_agent -c "내일 오후 2시에 팀 미팅 일정 추가해줘"

# 대화형 모드
mac_agent -i

# 도움말
mac_agent --help
```

### 로컬 실행 (개발용)
```bash
# 직접 명령 실행
python app/main.py -c "내일 오후 2시에 팀 미팅 일정 추가해줘"

# 대화형 모드
python app/main.py -i
```

### 세션 관리
```bash
# 세션 목록 조회
mac_agent --session list

# 특정 세션 정보
mac_agent --session info --session-id <session_id>

# 대화 내역 조회
mac_agent --session history --session-id <session_id>

# 세션 삭제
mac_agent --session delete --session-id <session_id>
```

### 세션 전략 설정
```bash
# 터미널별 세션 (기본값)
mac_agent -c "안녕하세요" --session-strategy terminal_pid

# 사용자별 세션
mac_agent -c "안녕하세요" --session-strategy system_user

# 커스텀 세션
mac_agent -c "안녕하세요" --session-strategy custom --user-id "my_session"

# 디렉토리별 세션
mac_agent -c "안녕하세요" --session-strategy directory

# 최근 세션 사용
mac_agent -c "안녕하세요" --session-strategy recent
```

## 📝 사용 예시

### 캘린더 관리
```bash
# 일정 생성
$ mac_agent -c "내일 오후 3시에 회의 일정 추가해줘"
🤖 내일 오후 3시에 '회의' 일정을 추가했습니다.

# 일정 조회
$ mac_agent -c "이번 주 일정 알려줘"
🤖 이번 주 일정을 확인해드리겠습니다...

# 일정 수정
$ mac_agent -c "회의 시간을 4시로 변경해줘"
🤖 회의 일정을 오후 4시로 변경했습니다.
```

### 대화 컨텍스트 유지 ⭐
```bash
# 첫 번째 대화
$ mac_agent -c "안녕하세요! 저는 김덕배입니다."
🤖 안녕하세요, 김덕배님! 만나서 반갑습니다.

# 두 번째 대화 (이름 기억)
$ mac_agent -c "내가 누구라고?"
🤖 김덕배님이시죠! 다시 뵙게 되어 반갑습니다.
```

### 대화형 모드
```bash
$ mac_agent -i
🤖 Mac Agent 대화형 모드 시작
💡 도움말:
  - 'quit' 또는 'exit': 종료
  - 'history': 대화 내역 보기
  - 'session': 세션 정보 보기
  - 'clear': 새 세션 시작
  - 'help': 도움말 보기
--------------------------------------------------

사용자: 내일 오후 2시에 팀 미팅 추가해줘
🤖 내일 오후 2시에 '팀 미팅' 일정을 추가했습니다.

사용자: 이번 주 일정 알려줘
🤖 이번 주 일정을 확인해드리겠습니다...

사용자: exit
👋 Mac Agent를 종료합니다.
```

### 터미널별 독립 세션
```bash
# 터미널 A에서
$ mac_agent -c "저는 김덕배입니다."
🤖 안녕하세요, 김덕배님!

# 터미널 B에서 (다른 세션)
$ mac_agent -c "저는 이영희입니다."
🤖 안녕하세요, 이영희님!

# 터미널 A로 돌아가서
$ mac_agent -c "내가 누구라고?"
🤖 김덕배님이시죠!  # 터미널별로 독립적인 메모리 유지
```

## 🔧 설정

### 환경 변수
- `OPENAI_API_KEY`: OpenAI API 키 (필수)
- `MAC_AGENT_SESSION_DIR`: 세션 저장 디렉토리 (선택, 기본값: `~/.mac_agent/sessions`)

### 캘린더 설정
기본적으로 시스템의 기본 캘린더를 사용하며, `calendar_tools.py`에서 다른 캘린더를 지정할 수 있습니다.

## 🛠️ 개발

### 프로젝트 구조
- **모듈화된 아키텍처**: 각 컴포넌트가 단일 책임 원칙을 따름
- **팩토리 패턴**: 에이전트 생성을 위한 팩토리 패턴 적용
- **전략 패턴**: 다양한 세션 식별 전략 지원
- **의존성 주입**: 컴포넌트 간 느슨한 결합

### 확장 가능성
- 새로운 세션 전략 추가
- 다른 캘린더 서비스 연동
- 추가 AI 모델 지원
- 웹 인터페이스 추가

### 개발 모드 실행
```bash
# 로컬에서 개발 및 테스트
python app/main.py -c "테스트 명령어"

# 대화형 모드로 디버깅
python app/main.py -i --verbose
```

## 📋 요구사항

- Python 3.8+
- macOS (캘린더 접근을 위해)
- OpenAI API 키
- 터미널 환경

## 🎯 주요 특징

### ✅ 완전한 메모리 기능
- 터미널별 독립 세션으로 자연스러운 워크플로우
- 프로세스 간 대화 컨텍스트 완벽 유지
- 파일 기반 영속성으로 안정성 보장

### ✅ 전역 CLI 도구
- `mac_agent` 명령어로 어디서든 접근 가능
- 자동 설치 스크립트로 간편한 설정
- pip를 통한 패키지 관리

### ✅ 지능형 의도 분류
- 캘린더 관련 요청과 일반 대화 자동 구분
- 컨텍스트에 맞는 적절한 응답 생성

### ✅ 확장 가능한 아키텍처
- 모듈화된 설계로 유지보수 용이
- 새로운 기능 추가 간편
- 테스트 친화적 구조

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 라이선스

MIT License

## 🙋‍♂️ 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.

---

**Mac Agent로 더 스마트한 캘린더 관리를 경험해보세요!** 🚀

### 🎉 빠른 시작

```bash
# 1. 설치
git clone <repository-url> && cd mac_agent && ./install.sh

# 2. 환경 설정
echo "OPENAI_API_KEY=your_api_key" > .env

# 3. 사용 시작
mac_agent -c "안녕하세요! Mac Agent입니다."
``` 
