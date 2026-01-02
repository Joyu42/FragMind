"""
数据模型定义
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FragMind(BaseModel):
    """片段思绪数据模型"""
    id: Optional[int] = None
    content: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))


class DiarySummary(BaseModel):
    """完整日记总结数据模型"""
    id: Optional[int] = None
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    summary: str = ""
    entry_count: int = 0  # 关联的片段数量
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class TodoItem(BaseModel):
    """待办事项数据模型"""
    id: Optional[int] = None
    title: str = ""
    due_date: Optional[datetime] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def mark_completed(self):
        """标记为已完成"""
        self.completed = True
        self.completed_at = datetime.now()
    
    def mark_uncompleted(self):
        """取消完成标记"""
        self.completed = False
        self.completed_at = None
