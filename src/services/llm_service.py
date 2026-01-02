"""
LLM 服务层
封装与 LLM API 的交互，提供日记总结、Todo 解析等 Agent 功能
使用 PydanticAI 框架重构
"""
from typing import List, Optional
from datetime import datetime
import os
import httpx

from PyQt6.QtCore import QSettings
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.deepseek import DeepSeekProvider

from src.config import Config
from src.models import FragMind, TodoItem


class TodoResult(BaseModel):
    """Todo 解析结果模型"""
    title: str = Field(description="待办事项标题（简洁明了）")
    due_date: Optional[datetime] = Field(default=None, description="截止时间（ISO 8601 格式，如果没有明确时间则为 null）")


class TodoList(BaseModel):
    """Todo 列表容器"""
    items: List[TodoResult] = Field(description="提取出的待办事项列表")


class LLMService:
    """LLM 服务类 - 提供 AI Agent 功能"""
    
    def __init__(self):
        """初始化 LLM 服务"""
        self.model = None
        self.summary_agent = None
        self.todo_agent = None
        self._init_agents()
    
    def _init_agents(self):
        """初始化 PydanticAI Agents"""
        api_key = Config.get_api_key()
        
        if api_key:
            # 创建自定义 httpx client 以支持代理（如果环境变量设置了）
            # 并且设置较长的超时时间
            http_client = httpx.AsyncClient(
                timeout=30.0,
                proxy=os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
            )
            
            self.model = OpenAIChatModel(
                'deepseek-chat',
                provider=DeepSeekProvider(
                    api_key=api_key,
                    http_client=http_client
                )
            )

            
        if self.model:
            # 1. 日记总结 Agent
            self.summary_agent = Agent(
                self.model,
                system_prompt="你是 FragMind 系统中的 Reflection Agent，负责将用户在一天中记录的碎片化想法整理为一篇日记。",
                output_type=str
            )
            
            # 2. Todo 解析 Agent
            self.todo_agent = Agent(
                self.model,
                system_prompt="""你是 FragMind 系统中的 Todo Agent，负责从用户的日记片段中提取**所有**待办事项、计划、约会、活动安排和日程。

请严格遵循以下规则：
1. 捕捉休闲计划：即使是口语化的计划（如"去吃炸串"、"看电影"、"和朋友见面"）也必须提取为待办事项。
2. 提取时间：如果文中提到了时间（如"今晚八点"、"明天下午"），必须将其转换为具体的 `due_date`。
""",
                output_type=TodoList
            )
    
    def is_available(self) -> bool:
        """检查 LLM 服务是否可用"""
        return self.model is not None
    
    def summarize_diary_entries(self, entries: List[FragMind], date: str, current_summary: str = "") -> str:
        """
        总结多个日记片段为一篇完整日记
        """
        if not self.is_available():
            return "LLM 服务未配置，无法生成总结。\n\n" + "\n\n".join([e.content for e in entries])
        
        if not entries and not current_summary:
            return "今天还没有任何记录。"
        
        # 构建 prompt
        entries_text = "\n\n".join([
            f"[{e.created_at.strftime('%H:%M')}] {e.content}"
            for e in sorted(entries, key=lambda x: x.created_at)
        ])
        
        # 获取用户自定义 Prompt
        settings = QSettings("FragMind", "AppConfig")
        user_custom_prompt = settings.value("summary_prompt", "")
        
        prompt = f"""请将用户今天（{date}）零散记录的多条碎片化想法，整理成一篇流畅、连贯的日记。

请遵循以下原则：
1. 保留用户原有的情绪与观点，不夸大、不编造
2. 用第一人称书写，风格克制、连贯、自然、有一定的文学性、可按时间或逻辑组织
3. 不进行心理诊断或说教式分析，保持温和的自我反思视角。
4. 如果有重复或相似的内容，进行适当合并，避免冗余。
"""

        if user_custom_prompt:
            prompt += f"""
【用户额外指令】：
{user_custom_prompt}
请务必在遵循上述基本原则的同时，优先满足用户的这条额外指令。
"""

        if current_summary:
            prompt += f"""
5. **重要：重写模式**。
用户可能修改或删除了部分原始片段。
请以**下方的【今日所有有效片段】为唯一事实依据**重新生成日记。
【参考日记】仅用于参考文风和语调，**绝对不要**保留【参考日记】中存在但【今日所有有效片段】中不存在的信息。

【参考日记】（仅供文风参考）：
{current_summary}

【今日所有有效片段】（唯一事实来源）：
{entries_text}
"""
        else:
            prompt += f"""
【今日所有有效片段】：
{entries_text}
"""
        
        try:
            result = self.summary_agent.run_sync(prompt)
            return result.output
        
        except Exception as e:
            return f"生成总结时出错：{str(e)}\n\n原始内容：\n{entries_text}"
    
    def parse_todo_from_text(self, text: str, existing_titles: List[str] = None) -> List[TodoItem]:
        """
        从自然语言中解析待办事项
        """
        if not self.is_available():
            return []
        
        try:
            now = datetime.now()
            current_context = f"今天是 {now.strftime('%Y年%m月%d日')} {now.strftime('%A')}。"
            
            prompt = f"{current_context}\n请从以下文本中提取待办事项：\n{text}"
            
            
            result = self.todo_agent.run_sync(prompt)
            data_list = result.output.items
            
            todos = []
            for data in data_list:
                todos.append(TodoItem(
                    title=data.title,
                    due_date=data.due_date
                ))
            return todos
            
        except Exception as e:
            print(f"解析 Todo 时出错：{e}")
            return []

