#!/usr/bin/env python3
"""
Mac Agent - 자연어 캘린더 관리 시스템
메인 실행 파일 (리팩토링됨)
"""

import asyncio
import sys
import os
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가 (로컬 실행용)
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    # 전역 설치된 경우 (패키지 import)
    from app.cli import create_parser, CLICommands
    from app.agent import CalendarManagerAgent
except ImportError:
    # 로컬 실행인 경우 (상대 import)
    from cli import create_parser, CLICommands
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


async def main():
    """메인 함수"""
    parser = create_parser()
    args = parser.parse_args()
    
    # CLI 명령어 처리기 생성
    cli_commands = CLICommands()
    
    # 세션 관련 명령어 처리
    if hasattr(args, 'session_command') and args.session_command:
        await cli_commands.handle_session_command(args)
        return
    
    # 에이전트 생성
    agent = CalendarManagerAgent()
    
    try:
        if args.interactive:
            # 대화형 모드
            await cli_commands.interactive_mode(agent, args)
        elif args.command:
            # 단일 명령 모드
            response = await cli_commands.single_command_mode(agent, args)
            print(f"🤖 {response}")
        else:
            # 도움말 출력
            parser.print_help()
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main()) 