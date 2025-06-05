#!/usr/bin/env python3
"""
Mac Agent - 자연어 캘린더 관리 시스템
메인 실행 파일 (리팩토링됨)
"""

import asyncio
import sys

from cli import create_parser, CLICommands


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


def main():
    """메인 함수"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 인수 검증
    if not args.command and not args.session and not args.interactive:
        parser.error("--command, --session, 또는 --interactive 중 하나는 필수입니다.")
    
    if args.session in ['info', 'delete', 'history'] and not args.session_id:
        parser.error(f"--session {args.session}는 --session-id가 필요합니다.")
    
    # verbose 모드가 아니면 간단한 출력만
    if args.verbose:
        print("🚀 Mac Agent 시작 중...")
        
        # 의존성 확인
        if not check_dependencies():
            sys.exit(1)
        
        if args.command:
            print(f"📝 명령어 실행: {args.command}")
    else:
        # 조용한 의존성 확인
        if not check_dependencies_quiet():
            print("❌ 필요한 패키지가 설치되지 않았습니다. --verbose 옵션으로 자세한 정보를 확인하세요.")
            sys.exit(1)
    
    # 비동기 실행
    try:
        if args.interactive:
            # 대화형 모드
            asyncio.run(CLICommands.interactive_mode(args.calendar))
        elif args.session:
            # 세션 관리
            asyncio.run(CLICommands.manage_sessions(args.session, args.session_id))
        else:
            # 단일 명령어 실행
            result = asyncio.run(CLICommands.run_single_command(
                args.command, args.calendar, args.session_id, 
                args.session_strategy, args.user_id
            ))
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