"""
세션 저장소 관리
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import SessionInfo


class SessionStorage:
    """세션 파일 저장소"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            storage_dir = Path.home() / ".mac_agent" / "sessions"
        
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_session_file_path(self, session_id: str) -> Path:
        """세션 파일 경로를 반환합니다."""
        return self.storage_dir / f"{session_id}.json"
    
    def save_session(self, session_info: SessionInfo, memory_contents: List[str] = None) -> bool:
        """세션을 파일에 저장합니다."""
        try:
            session_data = {
                'session_info': {
                    'session_id': session_info.session_id,
                    'user_id': session_info.user_id,
                    'created_at': session_info.created_at.isoformat(),
                    'last_active': session_info.last_active.isoformat(),
                    'message_count': session_info.message_count
                },
                'memory_contents': memory_contents or []
            }
            
            with open(self._get_session_file_path(session_info.session_id), 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"세션 저장 중 오류: {str(e)}")
            return False
    
    def load_session(self, session_id: str) -> Optional[tuple]:
        """세션을 파일에서 로드합니다."""
        try:
            session_file = self._get_session_file_path(session_id)
            if not session_file.exists():
                return None
                
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            session_info_data = session_data.get('session_info')
            memory_contents = session_data.get('memory_contents', [])
            
            if session_info_data:
                session_info = SessionInfo(
                    session_id=session_info_data['session_id'],
                    user_id=session_info_data.get('user_id'),
                    created_at=datetime.fromisoformat(session_info_data['created_at']),
                    last_active=datetime.fromisoformat(session_info_data['last_active']),
                    message_count=session_info_data.get('message_count', 0)
                )
                return session_info, memory_contents
            return None
        except Exception as e:
            print(f"세션 로드 중 오류: {str(e)}")
            return None
    
    def load_all_sessions(self) -> Dict[str, tuple]:
        """모든 세션을 로드합니다."""
        sessions = {}
        try:
            for session_file in self.storage_dir.glob("*.json"):
                session_id = session_file.stem
                session_data = self.load_session(session_id)
                if session_data:
                    sessions[session_id] = session_data
        except Exception as e:
            print(f"세션 로드 중 오류: {str(e)}")
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """세션 파일을 삭제합니다."""
        try:
            session_file = self._get_session_file_path(session_id)
            if session_file.exists():
                session_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"세션 파일 삭제 중 오류: {str(e)}")
            return False 