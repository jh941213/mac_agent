# Mac Agent - 자연어 캘린더 관리 시스템

AutoGen AgentChat과 Structured Output을 활용한 macOS 캘린더 자동화 에이전트입니다.

**history 는 구현 안함 아직** 

`version : 0.0.1`

## 🌟 주요 기능

- **자연어 일정 관리**: "5월 17일 일정등록해줘 저녁식사" 형태의 자연어로 캘린더 관리
- **Structured Output**: Pydantic 모델 기반 안전한 의도 분석
- **모듈화된 구조**: 프롬프트와 에이전트 로직 분리로 유지보수성 향상
- **다중 캘린더 지원**: 여러 캘린더에서 일정 검색 및 관리
- **일반 대화 지원**: 캘린더 외 일반적인 질문과 인사 처리
- **전역 명령어**: 터미널 어디서든 `mac_agent "명령어"` 사용 가능

## 🚀 빠른 시작

### 전역 명령어 사용 (권장)
```bash
# 일정 생성
mac_agent "5월 17일 일정등록해줘 저녁식사"
mac_agent "7월 15일 오후 3시 - 팀 회의"

# 일정 조회
mac_agent "팀 회의 일정 찾아줘"
mac_agent "내일 일정 보여줘"

# 일정 삭제
mac_agent "팀 회의 삭제해줘"

# 일반 대화
mac_agent "안녕하세요"
mac_agent "테스트"
```

### 직접 실행
```bash
cd app
python main.py -c "5월 17일 일정등록해줘 저녁식사"
```

## 📋 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정
프로젝트 루트에 `.env` 파일 생성:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 전역 명령어 설정 (권장)
```bash
# 실행 권한 부여
chmod +x mac_agent

# 전역 경로에 심볼릭 링크 생성
sudo ln -sf "$(pwd)/mac_agent" /usr/local/bin/mac_agent
```

## 🏗 프로젝트 구조

```
mac_agent/
├── mac_agent                    # 전역 명령어 스크립트
└── app/
    ├── main.py                  # 메인 실행 파일
    ├── agent/                   # 에이전트 모듈
    │   ├── __init__.py         # 모듈 초기화
    │   ├── agent.py            # 캘린더 관리 에이전트
    │   └── prompt.py           # 프롬프트 관리
    ├── calendar_tools.py        # macOS 캘린더 연동 도구
    ├── config.py               # 설정 파일
    ├── requirements.txt        # Python 의존성
    └── README.md              # 프로젝트 문서
```

## 🛠 기술 스택

- **AutoGen AgentChat**: ms 오픈소스 ai Agent
- **Structured Output**: Pydantic 기반 안전한 데이터 처리
- **OpenAI GPT-4o-mini**: 자연어 이해 및 의도 분석
- **AppleScript**: macOS 캘린더 연동


## 📖 사용 예시

### 일정 생성
```bash
mac_agent "5월 17일 일정등록해줘 저녁식사"
mac_agent "6월 30일 오후 4시 - 프로젝트 회의"
mac_agent "내일 오전 10시 치과 예약"
mac_agent "다음주 금요일 오후 2시 - 팀 빌딩"
```

### 일정 조회
```bash
mac_agent "저녁식사 일정 찾아줘"
mac_agent "프로젝트 회의 찾아줘"
mac_agent "내일 일정 보여줘"
mac_agent "이번주 일정 확인"
```

### 일정 수정
```bash
mac_agent "프로젝트 회의 시간을 오후 5시로 변경해줘"
mac_agent "치과 예약을 내일 오후 3시로 옮겨줘"
```

### 일정 삭제
```bash
mac_agent "저녁식사 일정 삭제해줘"
mac_agent "프로젝트 회의 삭제해줘"
mac_agent "치과 예약 취소"
```

### 일반 대화
```bash
mac_agent "안녕하세요"
mac_agent "테스트"
mac_agent "고마워"
```

## 🏗 시스템 아키텍처

### 모듈화된 구조
- **agent/prompt.py**: 시스템 프롬프트 중앙 관리
- **agent/agent.py**: 에이전트 로직과 비즈니스 로직 분리
- **main.py**: 실행 진입점과 CLI 인터페이스

### 의도 분류 시스템
- **Structured Output**: Pydantic 모델로 안전한 의도 분석
- **이진 분류**: `calendar` vs `general` 단순 분류
- **Chain of Thought**: 분류 이유 추론 포함

### 전문화된 에이전트
- **의도 분류 에이전트**: 사용자 요청 타입 분류
- **캘린더 전문 에이전트**: 캘린더 작업 처리
- **일반 대화 에이전트**: 일반적인 대화 처리

### 자연스러운 종료
- **MaxMessageTermination**: 최대 메시지 수 기반 종료
- **정규표현식 제거**: Structured Output으로 안전한 파싱

## 🔧 설정 옵션

### 검색 범위 조정
기본적으로 1개월 범위로 일정을 검색합니다. `calendar_tools.py`에서 수정 가능:
```python
def get_events(self, date_str=None, keywords=None, months_range=1):
    # months_range 값 조정
```

### 캘린더 이름 변경
다른 캘린더를 사용하려면 `main.py`에서 수정:
```python
agent = CalendarManagerAgent(calendar_name="Work")  # 기본값: "캘린더"
```

### 프롬프트 커스터마이징
`agent/prompt.py`에서 시스템 프롬프트 수정 가능:
```python
class PromptManager:
    @staticmethod
    def get_intent_classifier_prompt() -> str:
        # 의도 분류 프롬프트 수정
    
    @staticmethod
    def get_calendar_agent_prompt() -> str:
        # 캘린더 에이전트 프롬프트 수정
```

## 🐛 문제 해결

### 캘린더 권한 오류
macOS에서 캘린더 접근 권한을 허용해야 합니다:
1. 시스템 환경설정 > 보안 및 개인정보보호
2. 개인정보보호 > 캘린더
3. Python/터미널 앱에 권한 부여

### API 키 오류
`.env` 파일이 올바른 위치에 있고 유효한 OpenAI API 키가 설정되어 있는지 확인하세요.

### 전역 명령어 오류
```bash
# 심볼릭 링크 확인
ls -la /usr/local/bin/mac_agent

# 권한 확인
chmod +x mac_agent

# 재설정
sudo ln -sf "$(pwd)/mac_agent" /usr/local/bin/mac_agent
```

### 모듈 import 오류
```bash
# app 디렉토리에서 실행 확인
cd app && python main.py -c "테스트"
```

## 📝 라이선스

MIT License

## 🤝 기여

이슈 리포트와 풀 리퀘스트를 환영합니다! 
