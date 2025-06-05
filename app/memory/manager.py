"""
메모리 관리자
"""

from datetime import datetime
from typing import Dict, List

from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType

try:
    # 전역 설치된 경우
    from app.session.storage import SessionStorage
except ImportError:
    # 로컬 실행인 경우
    from session.storage import SessionStorage


class MemoryManager:
    """메모리 관리자"""
    
    def __init__(self, storage: SessionStorage):
        self.storage = storage
        self.session_memories: Dict[str, ListMemory] = {}
        self._pending_memory_restore: Dict[str, List[str]] = {}
    
    def get_or_create_memory(self, session_id: str) -> ListMemory:
        """세션의 메모리를 가져오거나 생성합니다."""
        if session_id not in self.session_memories:
            memory = ListMemory()
            self.session_memories[session_id] = memory
            
            # 저장된 메모리 내용 복원 준비
            session_data = self.storage.load_session(session_id)
            if session_data:
                _, memory_contents = session_data
                if memory_contents:
                    self._pending_memory_restore[session_id] = memory_contents
        
        return self.session_memories[session_id]
    
    async def add_to_memory(self, session_id: str, content: str, role: str = "user"):
        """세션 메모리에 대화 내용을 추가합니다."""
        memory = self.get_or_create_memory(session_id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memory_content = f"[{timestamp}] {role}: {content}"
        
        await memory.add(MemoryContent(
            content=memory_content,
            mime_type=MemoryMimeType.TEXT
        ))
    
    async def restore_pending_memories(self, session_id: str):
        """대기 중인 메모리 내용을 복원합니다."""
        if session_id in self._pending_memory_restore:
            memory = self.session_memories.get(session_id)
            if memory:
                for content_str in self._pending_memory_restore[session_id]:
                    await memory.add(MemoryContent(
                        content=content_str,
                        mime_type=MemoryMimeType.TEXT
                    ))
                # 복원 완료 후 대기 목록에서 제거
                del self._pending_memory_restore[session_id]
    
    async def get_conversation_history(self, session_id: str, limit: int = 50) -> List[str]:
        """세션의 대화 내역을 반환합니다."""
        if session_id not in self.session_memories:
            return []
        
        memory = self.session_memories[session_id]
        try:
            memory_contents = memory.content
            recent_memories = memory_contents[-limit:] if len(memory_contents) > limit else memory_contents
            return [mem.content for mem in recent_memories]
        except Exception as e:
            print(f"대화 내역 조회 중 오류: {str(e)}")
            return []
    
    def get_memory_contents(self, session_id: str) -> List[str]:
        """메모리 내용을 문자열 리스트로 반환합니다."""
        if session_id not in self.session_memories:
            return []
        
        memory = self.session_memories[session_id]
        try:
            return [content.content for content in memory.content]
        except Exception:
            return []
    
    def delete_memory(self, session_id: str):
        """세션의 메모리를 삭제합니다."""
        if session_id in self.session_memories:
            del self.session_memories[session_id]
        if session_id in self._pending_memory_restore:
            del self._pending_memory_restore[session_id] 