"""
캘린더 관리 에이전트 모듈 (리팩토링됨)
"""

import asyncio
from typing import Literal
from pydantic import BaseModel, Field

from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import StructuredMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

try:
    # 전역 설치된 경우
    from app.calendar_tools import CalendarTools
    from app.config import OPENAI_API_KEY
    from app.session import SessionManager
    from app.memory import MemoryManager
    from app.agent.prompt import PromptManager
    from app.agent.factory import AgentFactory
except ImportError:
    # 로컬 실행인 경우
    from calendar_tools import CalendarTools
    from config import OPENAI_API_KEY
    from session import SessionManager
    from memory import MemoryManager
    from .prompt import PromptManager
    from .factory import AgentFactory


class UserIntent(BaseModel):
    """사용자 의도 분류 모델"""
    intent_type: Literal["calendar", "general"] = Field(
        description="의도 유형: calendar(캘린더 관련) 또는 general(일반 대화)"
    )
    reasoning: str = Field(
        description="분류 이유"
    )


class CalendarManagerAgent:
    """AutoGen AgentChat 기반 캘린더 관리 에이전트 (리팩토링됨)"""
    
    def __init__(self, calendar_name: str = "캘린더"):
        # 핵심 컴포넌트들
        self.calendar_tools = CalendarTools(calendar_name)
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
            temperature=0.1
        )
        self.prompt_manager = PromptManager()
        
        # 관리자들
        self.session_manager = SessionManager()
        self.memory_manager = MemoryManager(self.session_manager.storage)
        
        # 에이전트 팩토리
        self.agent_factory = AgentFactory(
            self.model_client, 
            self.calendar_tools, 
            self.prompt_manager
        )
    
    async def classify_intent(self, user_input: str, session_id: str = None) -> UserIntent:
        """사용자 의도를 분류합니다."""
        try:
            # 메모리 가져오기
            memory = None
            if session_id:
                memory = self.memory_manager.get_or_create_memory(session_id)
            
            # 의도 분류 에이전트 생성
            intent_classifier = self.agent_factory.create_intent_classifier(memory)
            
            # 종료 조건 설정
            termination = MaxMessageTermination(max_messages=2)
            
            # 팀 생성 및 실행
            team = RoundRobinGroupChat([intent_classifier], termination_condition=termination)
            result = await team.run(task=user_input)
            
            # 결과 처리
            if result and result.messages:
                for message in reversed(result.messages):
                    if isinstance(message, StructuredMessage) and isinstance(message.content, UserIntent):
                        return message.content
            
            # 분류 실패 시 기본값
            return UserIntent(
                intent_type="general",
                reasoning="분류 실패로 일반 대화로 처리"
            )
            
        except Exception as e:
            print(f"의도 분류 중 오류: {str(e)}")
            return UserIntent(
                intent_type="general",
                reasoning=f"오류 발생으로 일반 대화로 처리: {str(e)}"
            )
    
    async def process_user_input(self, user_input: str, session_id: str = None) -> str:
        """사용자 입력을 처리하고 결과를 반환합니다."""
        try:
            # 세션 ID가 없으면 새로 생성
            if not session_id:
                session_id = self.session_manager.create_session()
            
            # 세션이 존재하지 않으면 새로 생성
            if not self.session_manager.get_session(session_id):
                session_id = self.session_manager.create_session()
            
            # 메모리 생성 및 대기 중인 메모리 복원
            self.memory_manager.get_or_create_memory(session_id)
            await self.memory_manager.restore_pending_memories(session_id)
            
            # 사용자 입력을 메모리에 추가
            await self.memory_manager.add_to_memory(session_id, user_input, "user")
            
            # 1. 의도 분류
            intent = await self.classify_intent(user_input, session_id)
            
            # 2. 의도에 따른 처리
            if intent.intent_type == "calendar":
                response = await self._handle_calendar_request(user_input, session_id)
            else:
                response = await self._handle_general_conversation(user_input, session_id)
            
            # 에이전트 응답을 메모리에 추가
            await self.memory_manager.add_to_memory(session_id, response, "assistant")
            
            # 세션 활동 업데이트 및 저장 (메모리 내용 포함)
            self.session_manager.update_session_activity(session_id)
            session_info = self.session_manager.get_session(session_id)
            memory_contents = self.memory_manager.get_memory_contents(session_id)
            self.session_manager.storage.save_session(session_info, memory_contents)
            
            return response
            
        except Exception as e:
            error_msg = f"오류가 발생했습니다: {str(e)}"
            if session_id:
                await self.memory_manager.add_to_memory(session_id, error_msg, "system")
            return error_msg
    
    async def _handle_calendar_request(self, user_input: str, session_id: str) -> str:
        """캘린더 관련 요청을 처리합니다."""
        try:
            # 메모리가 있는 캘린더 에이전트 생성
            memory = self.memory_manager.get_or_create_memory(session_id)
            calendar_agent = self.agent_factory.create_calendar_agent(memory)
            
            termination = MaxMessageTermination(max_messages=5)
            team = RoundRobinGroupChat([calendar_agent], termination_condition=termination)
            
            result = await team.run(task=user_input)
            
            if result and result.messages:
                for message in reversed(result.messages):
                    if hasattr(message, 'content') and message.content and message.source == 'calendar_agent':
                        return message.content.strip()
            
            return "캘린더 작업을 완료했지만 결과를 가져올 수 없습니다."
            
        except Exception as e:
            return f"캘린더 작업 중 오류가 발생했습니다: {str(e)}"
    
    async def _handle_general_conversation(self, user_input: str, session_id: str) -> str:
        """일반 대화를 처리합니다."""
        try:
            # 메모리가 있는 일반 대화 에이전트 생성
            memory = self.memory_manager.get_or_create_memory(session_id)
            general_agent = self.agent_factory.create_general_agent(memory)
            
            termination = MaxMessageTermination(max_messages=2)
            team = RoundRobinGroupChat([general_agent], termination_condition=termination)
            
            result = await team.run(task=user_input)
            
            if result and result.messages:
                for message in reversed(result.messages):
                    if hasattr(message, 'content') and message.content and message.source == 'general_agent':
                        return message.content.strip()
            
            return "안녕하세요! Mac Agent입니다. 캘린더 관리를 도와드릴게요."
            
        except Exception as e:
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    async def close(self):
        """리소스를 정리합니다."""
        if hasattr(self.model_client, 'close'):
            await self.model_client.close() 