"""
세션 관리 전략들
"""

import os
import getpass
from typing import Optional


class SessionStrategy:
    """세션 ID 생성 전략"""
    
    @staticmethod
    def terminal_pid() -> str:
        """터미널 PID 기반 사용자 ID 생성"""
        try:
            terminal_pid = os.getppid()
            return f"terminal_{terminal_pid}"
        except Exception:
            return "unknown_terminal"
    
    @staticmethod
    def system_user() -> str:
        """시스템 사용자명 기반 사용자 ID 생성"""
        try:
            return getpass.getuser()
        except Exception:
            return "unknown_user"
    
    @staticmethod
    def custom(user_id: str) -> str:
        """사용자 지정 ID"""
        return user_id or "custom_user"
    
    @staticmethod
    def directory() -> str:
        """현재 작업 디렉토리 기반 사용자 ID 생성"""
        try:
            current_dir = os.getcwd()
            return f"dir_{os.path.basename(current_dir)}"
        except Exception:
            return "dir_unknown"
    
    @staticmethod
    def get_user_id(strategy: str, custom_user_id: Optional[str] = None) -> str:
        """전략에 따라 사용자 ID를 생성합니다."""
        if strategy == "terminal_pid":
            return SessionStrategy.terminal_pid()
        elif strategy == "system_user":
            return SessionStrategy.system_user()
        elif strategy == "custom":
            return SessionStrategy.custom(custom_user_id)
        elif strategy == "directory":
            return SessionStrategy.directory()
        else:
            # 기본값은 터미널 PID
            return SessionStrategy.terminal_pid() 