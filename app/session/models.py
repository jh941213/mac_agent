"""
세션 관련 데이터 모델
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SessionInfo(BaseModel):
    """세션 정보 모델"""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime
    last_active: datetime
    message_count: int = 0
    
    def update_activity(self):
        """활동 시간을 현재 시간으로 업데이트"""
        self.last_active = datetime.now()
        self.message_count += 1 