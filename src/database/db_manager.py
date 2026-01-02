"""
数据库管理模块
使用 SQLite 存储日记片段、总结和待办事项
"""
import sqlite3
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from contextlib import contextmanager

from src.config import Config
from src.models import FragMind, DiarySummary, TodoItem


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初始化数据库连接"""
        self.db_path = db_path or str(Config.DATABASE_FULL_PATH)
        self._init_database()
    
    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    @contextmanager
    def _get_cursor(self, commit=False):
        """获取数据库游标的上下文管理器"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with self._get_cursor(commit=True) as cursor:
            # 日记片段表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diary_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date TEXT NOT NULL
                )
            """)
            
            # 日记总结表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diary_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    summary TEXT NOT NULL,
                    entry_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 待办事项表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS todo_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    due_date TIMESTAMP,
                    completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
    
    # ==================== 日记片段操作 ====================
    
    def add_frag_mind(self, entry: FragMind) -> int:
        """添加日记片段"""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO diary_entries (content, created_at, date)
                VALUES (?, ?, ?)
            """, (entry.content, entry.created_at, entry.date))
            return cursor.lastrowid

    def update_frag_mind_content(self, entry_id: int, new_content: str):
        """更新日记片段内容"""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE diary_entries 
                SET content = ? 
                WHERE id = ?
            """, (new_content, entry_id))
    
    def get_frag_minds_by_date(self, date: str) -> List[FragMind]:
        """获取指定日期的所有片段"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, content, created_at, date
                FROM diary_entries
                WHERE date = ?
                ORDER BY created_at DESC
            """, (date,))
            
            entries = []
            for row in cursor.fetchall():
                entries.append(FragMind(
                    id=row[0],
                    content=row[1],
                    created_at=row[2],
                    date=row[3]
                ))
            return entries
    
    def get_recent_frag_minds(self, limit: int = 10) -> List[FragMind]:
        """获取最近的日记片段"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, content, created_at, date
                FROM diary_entries
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            entries = []
            for row in cursor.fetchall():
                entries.append(FragMind(
                    id=row[0],
                    content=row[1],
                    created_at=row[2],
                    date=row[3]
                ))
            return entries
    
    def delete_frag_mind(self, entry_id: int):
        """删除日记片段"""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM diary_entries WHERE id = ?", (entry_id,))
    
    # ==================== 日记总结操作 ====================
    
    def save_diary_summary(self, summary: DiarySummary) -> int:
        """保存或更新日记总结"""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT OR REPLACE INTO diary_summaries (date, summary, entry_count, updated_at)
                VALUES (?, ?, ?, ?)
            """, (summary.date, summary.summary, summary.entry_count, datetime.now()))
            return cursor.lastrowid
    
    def get_diary_summary(self, date: str) -> Optional[DiarySummary]:
        """获取指定日期的日记总结"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, date, summary, entry_count, created_at, updated_at
                FROM diary_summaries
                WHERE date = ?
            """, (date,))
            
            row = cursor.fetchone()
            
            if row:
                return DiarySummary(
                    id=row[0],
                    date=row[1],
                    summary=row[2],
                    entry_count=row[3],
                    created_at=row[4],
                    updated_at=row[5]
                )
            return None
    
    def get_recent_summaries(self, limit: int = 7) -> List[DiarySummary]:
        """获取最近的日记总结"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, date, summary, entry_count, created_at, updated_at
                FROM diary_summaries
                ORDER BY date DESC
                LIMIT ?
            """, (limit,))
            
            summaries = []
            for row in cursor.fetchall():
                summaries.append(DiarySummary(
                    id=row[0],
                    date=row[1],
                    summary=row[2],
                    entry_count=row[3],
                    created_at=row[4],
                    updated_at=row[5]
                ))
            return summaries
    
    # ==================== 待办事项操作 ====================
    
    def add_todo_item(self, todo: TodoItem) -> int:
        """添加待办事项"""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO todo_items (title, due_date, completed, created_at)
                VALUES (?, ?, ?, ?)
            """, (todo.title, todo.due_date, todo.completed, todo.created_at))
            return cursor.lastrowid
    
    def get_active_todos(self) -> List[TodoItem]:
        """获取未完成的待办事项"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, title, due_date, completed, created_at, completed_at
                FROM todo_items
                WHERE completed = 0
                ORDER BY due_date ASC
            """)
            
            todos = []
            for row in cursor.fetchall():
                todos.append(TodoItem(
                    id=row[0],
                    title=row[1],
                    due_date=row[2],
                    completed=bool(row[3]),
                    created_at=row[4],
                    completed_at=row[5]
                ))
            return todos
    
    def get_all_todos(self) -> List[TodoItem]:
        """获取所有待办事项"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT id, title, due_date, completed, created_at, completed_at
                FROM todo_items
                ORDER BY completed ASC, created_at DESC
            """)
            
            todos = []
            for row in cursor.fetchall():
                todos.append(TodoItem(
                    id=row[0],
                    title=row[1],
                    due_date=row[2],
                    completed=bool(row[3]),
                    created_at=row[4],
                    completed_at=row[5]
                ))
            return todos
    
    def update_todo_status(self, todo_id: int, completed: bool):
        """更新待办事项状态"""
        completed_at = datetime.now() if completed else None
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE todo_items
                SET completed = ?, completed_at = ?
                WHERE id = ?
            """, (completed, completed_at, todo_id))
    
    def update_todo_info(self, todo_id: int, title: str = None, due_date: datetime = None):
        """更新待办事项信息"""
        with self._get_cursor(commit=True) as cursor:
            if title is not None:
                cursor.execute("UPDATE todo_items SET title = ? WHERE id = ?", (title, todo_id))
            
            if due_date is not None:
                cursor.execute("UPDATE todo_items SET due_date = ? WHERE id = ?", (due_date, todo_id))

    def delete_todo_item(self, todo_id: int):
        """删除待办事项"""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM todo_items WHERE id = ?", (todo_id,))
