"""
CLI 파서 설정
"""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """CLI 파서를 생성합니다."""
    parser = argparse.ArgumentParser(
        description="Mac Agent - 자연어 캘린더 관리 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  기본 명령어 실행 (터미널 PID 기반):
    python main.py -c "5월 17일 일정등록해줘 저녁식사"
    python main.py -c "내일 일정 보여줘"
    
  세션 관리 전략:
    python main.py -c "안녕하세요" --session-strategy terminal_pid  # 터미널별 독립 세션 (기본값)
    python main.py -c "안녕하세요" --session-strategy system_user  # 시스템 사용자명
    python main.py -c "안녕하세요" --session-strategy custom --user-id "김덕배"  # 사용자 지정
    python main.py -c "안녕하세요" --session-strategy directory  # 디렉토리 기반
    python main.py -c "안녕하세요" --session-strategy recent  # 최근 세션
    
  특정 세션 사용:
    python main.py -c "안녕하세요" --session-id abc123
    
  세션 관리:
    python main.py --session list
    python main.py --session info --session-id abc123
    python main.py --session delete --session-id abc123
    
  대화형 모드:
    python main.py --interactive
        """
    )
    
    parser.add_argument(
        '-c', '--command',
        help='실행할 명령어 (자연어)'
    )
    
    parser.add_argument(
        '--calendar',
        default="캘린더",
        help='사용할 캘린더 이름 (기본값: 캘린더)'
    )
    
    parser.add_argument(
        '--session-id',
        help='사용할 세션 ID'
    )
    
    parser.add_argument(
        '--session-strategy',
        choices=['terminal_pid', 'system_user', 'custom', 'directory', 'recent', 'default'],
        default='terminal_pid',
        help='세션 관리 전략 (기본값: terminal_pid)'
    )
    
    parser.add_argument(
        '--user-id',
        help='사용자 지정 ID (--session-strategy custom과 함께 사용)'
    )
    
    parser.add_argument(
        '--session',
        choices=['list', 'info', 'delete', 'history'],
        help='세션 관리 명령어'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='대화형 모드 실행'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='상세한 로그 출력'
    )
    
    return parser 