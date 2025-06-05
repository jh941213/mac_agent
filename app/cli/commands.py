"""
CLI 명령어 처리 모듈
"""

import asyncio
import sys

try:
    # 전역 설치된 경우
    from app.agent import CalendarManagerAgent
    from app.session import SessionManager
except ImportError:
    # 로컬 실행인 경우
    from agent import CalendarManagerAgent
    from session import SessionManager


class CLICommands:
    """CLI 명령어 처리기"""
    
    async def single_command_mode(self, agent, args):
        """단일 명령 모드를 처리합니다."""
        # 세션 ID가 없으면 전략에 따라 세션 선택
        session_id = args.session_id
        if not session_id:
            session_id = agent.session_manager.get_or_create_session_by_strategy(
                args.session_strategy, args.user_id
            )
        
        return await agent.process_user_input(args.command, session_id)
    
    async def interactive_mode(self, agent, args):
        """대화형 모드를 실행합니다."""
        session_id = agent.session_manager.get_or_create_session_by_strategy(
            args.session_strategy, args.user_id
        )
        
        print("🤖 Mac Agent 대화형 모드 시작")
        print("💡 도움말:")
        print("  - 'quit' 또는 'exit': 종료")
        print("  - 'history': 대화 내역 보기")
        print("  - 'session': 세션 정보 보기")
        print("  - 'clear': 새 세션 시작")
        print("  - 'help': 도움말 보기")
        print("-" * 50)
        
        try:
            while True:
                try:
                    user_input = input("\n사용자: ").strip()
                except KeyboardInterrupt:
                    print("\n👋 Ctrl+C로 Mac Agent를 종료합니다.")
                    break
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit']:
                    print("👋 Mac Agent를 종료합니다.")
                    break
                elif user_input.lower() == 'help':
                    print("\n💡 사용 가능한 명령어:")
                    print("  - 캘린더 관련: '내일 회의 일정 추가해줘', '오늘 일정 보여줘'")
                    print("  - 일반 대화: '안녕하세요', '날씨 어때?'")
                    print("  - 시스템 명령어: quit, history, session, clear, help")
                    continue
                elif user_input.lower() == 'history':
                    history = await agent.memory_manager.get_conversation_history(session_id)
                    if history:
                        print("\n📜 대화 내역:")
                        for msg in history[-10:]:  # 최근 10개만 표시
                            print(f"  {msg}")
                    else:
                        print("📜 대화 내역이 없습니다.")
                    continue
                elif user_input.lower() == 'session':
                    session_info = agent.session_manager.get_session_info(session_id)
                    if session_info:
                        print(f"\n🔍 세션 정보:")
                        print(f"  세션 ID: {session_info['session_id'][:8]}...")
                        print(f"  메시지 수: {session_info['message_count']}")
                        print(f"  생성 시간: {session_info['created_at']}")
                        print(f"  마지막 활동: {session_info['last_active']}")
                    else:
                        print("🔍 세션 정보를 찾을 수 없습니다.")
                    continue
                elif user_input.lower() == 'clear':
                    # 새 세션 시작
                    session_id = agent.session_manager.create_session()
                    print("🆕 새 세션을 시작했습니다.")
                    continue
                
                try:
                    response = await agent.process_user_input(user_input, session_id)
                    print(f"🤖 {response}")
                except KeyboardInterrupt:
                    print("\n👋 처리 중 종료 요청을 받았습니다.")
                    break
                except Exception as e:
                    print(f"❌ 오류: {str(e)}")
                    
        except KeyboardInterrupt:
            print("\n👋 Mac Agent를 종료합니다.")
    
    async def handle_session_command(self, args):
        """세션 관리 명령을 처리합니다."""
        session_manager = SessionManager()
        
        if args.session_command == "list":
            sessions = session_manager.list_sessions()
            if sessions:
                print("📋 활성 세션 목록:")
                for session in sessions:
                    print(f"  - 세션 ID: {session['session_id'][:8]}...")
                    print(f"    사용자 ID: {session['user_id'] or 'N/A'}")
                    print(f"    메시지 수: {session['message_count']}")
                    print(f"    마지막 활동: {session['last_active']}")
                    print()
            else:
                print("📋 활성 세션이 없습니다.")
                
        elif args.session_command == "delete" and args.session_id:
            success = session_manager.delete_session(args.session_id)
            if success:
                print(f"✅ 세션 {args.session_id[:8]}...이 삭제되었습니다.")
            else:
                print(f"❌ 세션 {args.session_id[:8]}...을 찾을 수 없습니다.")
                
        elif args.session_command == "info" and args.session_id:
            session_info = session_manager.get_session_info(args.session_id)
            if session_info:
                print(f"🔍 세션 정보:")
                print(f"  세션 ID: {session_info['session_id']}")
                print(f"  사용자 ID: {session_info['user_id'] or 'N/A'}")
                print(f"  생성 시간: {session_info['created_at']}")
                print(f"  마지막 활동: {session_info['last_active']}")
                print(f"  메시지 수: {session_info['message_count']}")
            else:
                print(f"❌ 세션 {args.session_id[:8]}...을 찾을 수 없습니다.")
        else:
            print("❌ 잘못된 세션 관리 명령입니다.") 