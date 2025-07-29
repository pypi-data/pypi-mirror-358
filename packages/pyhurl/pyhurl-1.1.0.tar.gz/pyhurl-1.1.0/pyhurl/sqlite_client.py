import os
import sqlite3
from typing import Optional, List, Any


class SqliteClient:
    """
    一个用于操作 SQLite 数据库的、支持上下文管理的客户端。
    它通过复用连接和管理事务边界来提供高性能和数据一致性。
    """

    def __init__(self, db_file: str):
        if not db_file or not isinstance(db_file, str):
            raise ValueError("必须提供一个有效的数据库文件路径字符串。")
        self.db_file = db_file
        self.connection: Optional[sqlite3.Connection] = None
        self._ensure_db_directory_exists()

    def _ensure_db_directory_exists(self):
        parent_folder = os.path.dirname(self.db_file)
        if parent_folder and not os.path.exists(parent_folder):
            os.makedirs(parent_folder, exist_ok=True)

    def __enter__(self):
        """上下文管理器入口：建立连接并开始事务。"""
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.connection.row_factory = sqlite3.Row
            # 返回自身，以便在 with 块中使用
            return self
        except sqlite3.Error as e:
            raise ConnectionError(f"无法连接到数据库 {self.db_file}: {e}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口：根据异常情况提交或回滚，并关闭连接。"""
        if self.connection:
            try:
                if exc_type is None:
                    # 没有异常，提交事务
                    self.connection.commit()
                else:
                    # 发生异常，回滚事务
                    self.connection.rollback()
            finally:
                # 无论如何都关闭连接
                self.connection.close()
                self.connection = None

    def _get_cursor(self) -> sqlite3.Cursor:
        """获取一个游标。确保在连接上下文中调用。"""
        if self.connection is None:
            raise RuntimeError("数据库连接未打开。请在 'with' 语句中使用该客户端。")
        return self.connection.cursor()

    # --- 数据操作方法（现在依赖于共享的 self.connection） ---

    def execute(self, sql: str, params: Optional[Any] = None) -> int:
        """
        执行一个非查询语句（如 UPDATE, INSERT, DELETE），返回受影响的行数。
        注意：在 with 块结束前，更改不会被提交。
        """
        cursor = self._get_cursor()
        cursor.execute(sql, params or ())
        return cursor.rowcount

    def fetchall(self, sql: str, params: Optional[Any] = None) -> List[sqlite3.Row]:
        """执行 SELECT 查询并返回所有匹配的记录。"""
        cursor = self._get_cursor()
        cursor.execute(sql, params or ())
        return cursor.fetchall()

    def fetchone(self, sql: str, params: Optional[Any] = None) -> Optional[sqlite3.Row]:
        """执行 SELECT 查询并返回第一条匹配的记录。"""
        cursor = self._get_cursor()
        cursor.execute(sql, params or ())
        return cursor.fetchone()

    def fetch_scalar(self, sql: str, params: Optional[Any] = None) -> Optional[Any]:
        """执行查询并返回第一条记录的第一个列的值。"""
        cursor = self._get_cursor()
        cursor.execute(sql, params or ())
        row = cursor.fetchone()
        return row[0] if row else None

    def last_row_id(self) -> Optional[int]:
        """获取最后插入的行的ID。应在 INSERT 操作后立即调用。"""
        cursor = self._get_cursor()
        return cursor.lastrowid
