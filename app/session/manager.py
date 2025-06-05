"""
세션 관리자
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from .models import SessionInfo
from .storage import SessionStorage
from utils.strategies import SessionStrategy


class SessionManager:
    """세션 관리자"""
    
    def __init__(self, storage: Optional[SessionStorage] = None):
        self.storage = storage or SessionStorage()
        self.sessions: Dict[str, SessionInfo] = {}
        self._load_all_sessions()
    
    def _load_all_sessions(self):
        """저장된 모든 세션을 로드합니다."""
        session_data = self.storage.load_all_sessions()
        for session_id, (session_info, _) in session_data.items():
            self.sessions[session_id] = session_info
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """새로운 세션을 생성합니다."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session_info = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_active=now
        )
        
        self.sessions[session_id] = session_info
        self.storage.save_session(session_info)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """세션 정보를 조회합니다."""
        return self.sessions.get(session_id)
    
    def get_or_create_session_by_strategy(self, strategy: str = "terminal_pid", 
                                        custom_user_id: Optional[str] = None) -> str:
        """전략에 따라 세션을 가져오거나 생성합니다."""
        user_id = SessionStrategy.get_user_id(strategy, custom_user_id)
        
        # 기존 세션 찾기
        for session_id, session_info in self.sessions.items():
            if session_info.user_id == user_id:
                self.update_session_activity(session_id)
                return session_id
        
        # 최근 세션 전략인 경우
        if strategy == "recent" and self.sessions:
            most_recent = max(self.sessions.items(), 
                            key=lambda x: x[1].last_active)
            self.update_session_activity(most_recent[0])
            return most_recent[0]
        
        # 새 세션 생성
        return self.create_session(user_id=user_id)
    
    def update_session_activity(self, session_id: str):
        """세션 활동 시간을 업데이트합니다."""
        if session_id in self.sessions:
            self.sessions[session_id].update_activity()
            # 메모리 내용 없이는 저장하지 않음 - 메인 프로세스에서 메모리와 함께 저장
    
    def delete_session(self, session_id: str) -> bool:
        """세션을 삭제합니다."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return self.storage.delete_session(session_id)
        return False
    
    def list_sessions(self) -> List[dict]:
        """모든 세션 목록을 반환합니다."""
        return [
            {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "created_at": session.created_at.isoformat(),
                "last_active": session.last_active.isoformat(),
                "message_count": session.message_count
            }
            for session in self.sessions.values()
        ]
    
    def get_session_info(self, session_id: str) -> Optional[dict]:
        """세션 정보를 딕셔너리로 반환합니다."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "last_active": session.last_active.isoformat(),
            "message_count": session.message_count
        } 