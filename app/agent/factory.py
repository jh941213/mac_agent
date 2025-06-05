"""
에이전트 팩토리
"""

import json
from typing import List

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.memory import ListMemory

from calendar_tools import CalendarTools
from .prompt import PromptManager


class AgentFactory:
    """에이전트 생성 팩토리"""
    
    def __init__(self, model_client: OpenAIChatCompletionClient, 
                 calendar_tools: CalendarTools, prompt_manager: PromptManager):
        self.model_client = model_client
        self.calendar_tools = calendar_tools
        self.prompt_manager = prompt_manager
    
    def create_intent_classifier(self, memory: ListMemory = None) -> AssistantAgent:
        """의도 분류 에이전트를 생성합니다."""
        from .agent import UserIntent  # 순환 import 방지
        
        config = {
            "name": "intent_classifier",
            "model_client": self.model_client,
            "output_content_type": UserIntent,
            "system_message": self.prompt_manager.get_intent_classifier_prompt()
        }
        
        if memory:
            config["memory"] = [memory]
        
        return AssistantAgent(**config)
    
    def create_calendar_agent(self, memory: ListMemory = None) -> AssistantAgent:
        """캘린더 전문 에이전트를 생성합니다."""
        config = {
            "name": "calendar_agent",
            "model_client": self.model_client,
            "tools": self._get_calendar_tools(),
            "system_message": self.prompt_manager.get_calendar_agent_prompt()
        }
        
        if memory:
            config["memory"] = [memory]
        
        return AssistantAgent(**config)
    
    def create_general_agent(self, memory: ListMemory = None) -> AssistantAgent:
        """일반 대화 에이전트를 생성합니다."""
        config = {
            "name": "general_agent",
            "model_client": self.model_client,
            "system_message": self.prompt_manager.get_general_agent_prompt()
        }
        
        if memory:
            config["memory"] = [memory]
        
        return AssistantAgent(**config)
    
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