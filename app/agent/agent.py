"""
캘린더 관리 에이전트 모듈
"""

import asyncio
import json
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import StructuredMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from calendar_tools import CalendarTools
from config import OPENAI_API_KEY
from .prompt import PromptManager


class UserIntent(BaseModel):
    """사용자 의도 분류 모델"""
    intent_type: Literal["calendar", "general"] = Field(
        description="의도 유형: calendar(캘린더 관련) 또는 general(일반 대화)"
    )
    reasoning: str = Field(
        description="분류 이유"
    )


class CalendarManagerAgent:
    """AutoGen AgentChat 기반 캘린더 관리 에이전트"""
    #캘린더 이름은 캘린더, home, work 중 다양하게 선택 가능
    def __init__(self, calendar_name: str = "캘린더"):
        self.calendar_tools = CalendarTools(calendar_name)
        self.model_client = OpenAIChatCompletionClient(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
            temperature=0.1
        )
        self.prompt_manager = PromptManager()
        self.setup_agents()
    
    def setup_agents(self):
        """AutoGen AgentChat 에이전트들을 설정합니다."""
        
        # 의도 분류 에이전트 (Structured Output 사용)
        self.intent_classifier = AssistantAgent(
            name="intent_classifier",
            model_client=self.model_client,
            output_content_type=UserIntent,
            system_message=self.prompt_manager.get_intent_classifier_prompt()
        )
        
        # 캘린더 전문 에이전트
        self.calendar_agent = AssistantAgent(
            name="calendar_agent",
            model_client=self.model_client,
            tools=self._get_calendar_tools(),
            system_message=self.prompt_manager.get_calendar_agent_prompt()
        )
        
        # 일반 대화 에이전트
        self.general_agent = AssistantAgent(
            name="general_agent",
            model_client=self.model_client,
            system_message=self.prompt_manager.get_general_agent_prompt()
        )
    
    def _get_calendar_tools(self) -> List:
        """캘린더 관련 도구 함수들을 반환합니다."""
        
        def create_event(date_str: str, title: str, time_str: str = None, duration_minutes: int = 60) -> str:
            """캘린더에 새 일정을 생성합니다."""
            result = self.calendar_tools.create_event(date_str, title, time_str, duration_minutes)
            return json.dumps(result, ensure_ascii=False)
        
        def get_events(date_str: str = None, keywords: str = None, months_range: int = 1) -> str:
            """캘린더에서 일정을 조회합니다."""
            result = self.calendar_tools.get_events(date_str, keywords, months_range)
            return json.dumps(result, ensure_ascii=False)
        
        def update_event(original_title: str, new_date_str: str = None, 
                        new_time_str: str = None, new_title: str = None) -> str:
            """기존 일정을 수정합니다."""
            result = self.calendar_tools.update_event(original_title, new_date_str, new_time_str, new_title)
            return json.dumps(result, ensure_ascii=False)
        
        def delete_event(title: str, date_str: str = None) -> str:
            """일정을 삭제합니다."""
            result = self.calendar_tools.delete_event(title, date_str)
            return json.dumps(result, ensure_ascii=False)
        
        return [create_event, get_events, update_event, delete_event]
    
    async def classify_intent(self, user_input: str) -> UserIntent:
        """사용자 의도를 분류합니다."""
        try:
            # 종료 조건 설정
            termination = MaxMessageTermination(max_messages=2)
            
            # 팀 생성
            team = RoundRobinGroupChat([self.intent_classifier], termination_condition=termination)
            
            # 의도 분류 실행
            result = await team.run(task=user_input)
            
            # Structured Output 결과 처리
            if result and result.messages:
                for message in reversed(result.messages):
                    if isinstance(message, StructuredMessage) and isinstance(message.content, UserIntent):
                        return message.content
            
            # 분류 실패 시 기본값 (일반 대화로 분류)
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
    
    async def process_user_input(self, user_input: str) -> str:
        """사용자 입력을 처리하고 결과를 반환합니다."""
        try:
            # 1. 의도 분류
            intent = await self.classify_intent(user_input)
            
            # 2. 의도에 따른 처리
            if intent.intent_type == "calendar":
                return await self._handle_calendar_request(user_input)
            else:
                return await self._handle_general_conversation(user_input)
            
        except Exception as e:
            return f"오류가 발생했습니다: {str(e)}"
    
    async def _handle_calendar_request(self, user_input: str) -> str:
        """캘린더 관련 요청을 처리합니다."""
        try:
            termination = MaxMessageTermination(max_messages=5)
            team = RoundRobinGroupChat([self.calendar_agent], termination_condition=termination)
            
            result = await team.run(task=user_input)
            
            if result and result.messages:
                for message in reversed(result.messages):
                    if hasattr(message, 'content') and message.content and message.source == 'calendar_agent':
                        return message.content.strip()
            
            return "캘린더 작업을 완료했지만 결과를 가져올 수 없습니다."
            
        except Exception as e:
            return f"캘린더 작업 중 오류가 발생했습니다: {str(e)}"
    
    async def _handle_general_conversation(self, user_input: str) -> str:
        """일반 대화를 처리합니다."""
        try:
            termination = MaxMessageTermination(max_messages=2)
            team = RoundRobinGroupChat([self.general_agent], termination_condition=termination)
            
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