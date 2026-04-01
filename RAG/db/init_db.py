"""
数据库初始化脚本

用于创建 RAG 服务所需的额外表结构
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = Path(__file__).parent.parent / "data" / "rag_sqlite.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_knowledge_documents_table():
    """初始化 knowledge_documents 表（添加扩展字段）"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='knowledge_documents'
        """)
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            # 创建完整表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    doc_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    doc_type TEXT,
                    category TEXT DEFAULT 'shared',
                    vector_ids TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            logger.info("创建 knowledge_documents 表成功")
        else:
            # 检查并添加缺失的字段
            cursor.execute("PRAGMA table_info(knowledge_documents)")
            columns = [row[1] for row in cursor.fetchall()]

            if "category" not in columns:
                cursor.execute("""
                    ALTER TABLE knowledge_documents
                    ADD COLUMN category TEXT DEFAULT 'shared'
                """)
                logger.info("添加 category 字段成功")

            if "vector_ids" not in columns:
                cursor.execute("""
                    ALTER TABLE knowledge_documents
                    ADD COLUMN vector_ids TEXT
                """)
                logger.info("添加 vector_ids 字段成功")

        conn.commit()
        logger.info("knowledge_documents 表初始化完成")

    except sqlite3.Error as e:
        logger.error(f"初始化失败: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


def init_other_tables():
    """创建其他 RAG 所需的表"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 创建会话历史表（可选，用于替代文件存储）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                role_type TEXT DEFAULT 'student',
                title TEXT DEFAULT '新对话',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                message_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
            )
        """)

        conn.commit()
        logger.info("其他表初始化完成")

    except sqlite3.Error as e:
        logger.error(f"初始化失败: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


def main():
    """主函数"""
    logger.info(f"数据库路径: {DB_PATH}")

    init_knowledge_documents_table()
    init_other_tables()

    logger.info("数据库初始化完成！")


if __name__ == "__main__":
    main()
