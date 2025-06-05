#!/usr/bin/env python3
"""
Mac Agent - 자연어 캘린더 관리 시스템
메인 실행 파일
"""

import asyncio
import argparse
import sys
import subprocess
from typing import Optional

from agent import CalendarManagerAgent


def check_dependencies():
    """필요한 패키지가 설치되어 있는지 확인합니다."""
    required_packages = [
        ('autogen-agentchat', 'autogen_agentchat'),
        ('autogen-ext', 'autogen_ext'),
        ('openai', 'openai'),
        ('pydantic', 'pydantic'),
        ('python-dotenv', 'dotenv')
    ]
    
    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ 다음 패키지들이 설치되지 않았습니다: {', '.join(missing_packages)}")
        print("📦 다음 명령어로 설치해주세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 필요한 패키지가 설치되어 있습니다.")
    return True


def check_dependencies_quiet():
    """필요한 패키지가 설치되어 있는지 조용히 확인합니다."""
    required_packages = [
        ('autogen-agentchat', 'autogen_agentchat'),
        ('autogen-ext', 'autogen_ext'),
        ('openai', 'openai'),
        ('pydantic', 'pydantic'),
        ('python-dotenv', 'dotenv')
    ]
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            return False
    
    return True


async def run_mac_agent(command: str, calendar_name: str = "캘린더") -> str:
    """Mac Agent를 실행하고 결과를 반환합니다."""
    agent = None
    try:
        agent = CalendarManagerAgent(calendar_name)
        result = await agent.process_user_input(command)
        return result
    except Exception as e:
        return f"❌ 오류가 발생했습니다: {str(e)}"
    finally:
        if agent:
            await agent.close()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="Mac Agent - 자연어 캘린더 관리 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    사용 예시:
    python main.py -c "5월 17일 일정등록해줘 저녁식사"
    python main.py -c "내일 일정 보여줘"
    python main.py -c "회의 일정 삭제해줘"
    python main.py -c "안녕하세요"
            """
    )
    
    parser.add_argument(
        '-c', '--command',
        required=True,
        help='실행할 명령어 (자연어)'
    )
    
    parser.add_argument(
        '--calendar',
        default="캘린더",
        help='사용할 캘린더 이름 (기본값: 캘린더)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='상세한 로그 출력'
    )
    
    args = parser.parse_args()
    
    # verbose 모드가 아니면 간단한 출력만
    if args.verbose:
        print("🚀 Mac Agent 시작 중...")
        
        # 의존성 확인
        if not check_dependencies():
            sys.exit(1)
        
        print(f"📝 명령어 실행: {args.command}")
    else:
        # 조용한 의존성 확인
        if not check_dependencies_quiet():
            print("❌ 필요한 패키지가 설치되지 않았습니다. --verbose 옵션으로 자세한 정보를 확인하세요.")
            sys.exit(1)
    
    # 비동기 실행
    try:
        result = asyncio.run(run_mac_agent(args.command, args.calendar))
        print(f"🤖 {result}")
    except KeyboardInterrupt:
        if args.verbose:
            print("\n⚠️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 