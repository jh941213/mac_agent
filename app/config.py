"""
설정 파일
"""

import os
from pathlib import Path
from dotenv import load_dotenv

current_dir = Path(__file__).parent  
project_root = current_dir.parent   

env_path = project_root / '.env'


if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    print(f"⚠️ .env 파일을 찾을 수 없습니다: {env_path}")


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_openai_api_key_here':
    raise ValueError(
        "❌ OPENAI_API_KEY가 설정되지 않았습니다.\n"
        f"프로젝트 루트({project_root})에 .env 파일을 생성하고 다음과 같이 설정하세요:\n"
        "OPENAI_API_KEY=your_actual_api_key_here"
    )


DEFAULT_CALENDAR_NAME = "캘린더"  
DEFAULT_EVENT_DURATION = 60  
DEFAULT_EVENT_START_TIME = "09:00"  


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
APPLESCRIPT_DATE_FORMAT = "%A %Y년 %m월 %d일 %H:%M:%S" 