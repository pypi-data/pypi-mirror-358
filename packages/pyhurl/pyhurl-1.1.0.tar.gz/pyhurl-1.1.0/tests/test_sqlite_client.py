import os
import tempfile
import unittest
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock

from pyhurl.sqlite_client import SqliteClient


class TestSqliteClient(unittest.TestCase):
    def setUp(self):
        # 创建一个临时数据库文件
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        
        # 初始化测试数据
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                )
            ''')
            conn.commit()

    def tearDown(self):
        # 清理临时文件
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_context_manager_success(self):
        """测试上下文管理器正常使用"""
        with SqliteClient(self.db_path) as client:
            self.assertIsNotNone(client.connection)
            self.assertIsInstance(client.connection, sqlite3.Connection)
        # 连接应该已关闭
        self.assertIsNone(client.connection)

    def test_context_manager_with_exception(self):
        """测试在发生异常时事务回滚"""
        try:
            with SqliteClient(self.db_path) as client:
                client.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Test", "test@example.com"))
                # 模拟一个异常
                raise ValueError("Test exception")
        except ValueError:
            pass
            
        # 检查数据是否回滚
        with SqliteClient(self.db_path) as client:
            result = client.fetchone("SELECT COUNT(*) as count FROM users")
            self.assertEqual(result[0], 0)

    def test_execute_and_fetch(self):
        """测试执行SQL和查询数据"""
        with SqliteClient(self.db_path) as client:
            # 测试插入
            affected = client.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)", 
                ("Alice", "alice@example.com")
            )
            self.assertEqual(affected, 1)
            
            # 测试查询所有记录
            users = client.fetchall("SELECT * FROM users")
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0]['name'], "Alice")
            
            # 获取最后插入的ID
            last_id = users[0]['id']
            self.assertIsNotNone(last_id)
            
            # 测试查询单条
            user = client.fetchone("SELECT * FROM users WHERE id = ?", (last_id,))
            self.assertEqual(user['name'], "Alice")
            
            # 测试标量查询
            count = client.fetch_scalar("SELECT COUNT(*) FROM users")
            self.assertEqual(count, 1)
            
            # 测试 last_row_id 方法
            # 注意：lastrowid 只在某些情况下有效，这里我们只检查它不抛出异常
            try:
                client.last_row_id()
            except Exception as e:
                self.fail(f"last_row_id() raised {e} unexpectedly")

    def test_nonexistent_directory_creation(self):
        """测试自动创建不存在的目录"""
        temp_dir = os.path.join(self.temp_dir, 'nonexistent_dir')
        db_path = os.path.join(temp_dir, 'test.db')
        
        with SqliteClient(db_path) as client:
            self.assertTrue(os.path.exists(temp_dir))
            self.assertTrue(os.path.exists(db_path))
        
        # 清理
        os.unlink(db_path)
        os.rmdir(temp_dir)

    def test_invalid_db_file(self):
        """测试无效的数据库文件路径"""
        with self.assertRaises(ValueError):
            SqliteClient("")
        
        with self.assertRaises(ValueError):
            SqliteClient(None)

    def test_connection_error(self):
        """测试连接错误处理"""
        # 创建一个临时目录用于测试
        test_dir = os.path.join(self.temp_dir, 'test_connection')
        os.makedirs(test_dir, exist_ok=True)
        
        # 创建一个只读文件而不是目录，这会触发连接错误
        db_path = os.path.join(test_dir, 'test.db')
        with open(db_path, 'w') as f:
            f.write('not a database')
        os.chmod(test_dir, 0o400)  # 只读权限
        
        # 测试连接错误
        with self.assertRaises((ConnectionError, sqlite3.OperationalError)):
            with SqliteClient(db_path) as client:
                pass
        
        # 清理
        os.chmod(test_dir, 0o700)  # 恢复权限以便删除
        os.unlink(db_path)
        os.rmdir(test_dir)


if __name__ == '__main__':
    unittest.main()
