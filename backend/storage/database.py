"""
数据库连接管理 - MySQL (SQLAlchemy 异步)
"""
import os
from pathlib import Path
from urllib.parse import quote_plus
from typing import AsyncGenerator

# 加载环境变量
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

# MySQL 连接配置
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "aiwardrobe")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "aiwardrobe")

# 构建 DSN (Data Source Name)
password = quote_plus(MYSQL_PASSWORD) if MYSQL_PASSWORD else ""
DSN = f"mysql+aiomysql://{MYSQL_USER}:{password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# 创建异步引擎
_engine = None
_async_session_maker = None


def get_engine():
    """获取或创建异步引擎"""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            DSN,
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            pool_pre_ping=True,
            poolclass=NullPool,
        )
    return _engine


def get_session_maker():
    """获取或创建会话工厂"""
    global _async_session_maker
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖函数"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库 - 创建所有表"""
    from storage.models_mysql import Base

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def check_db_connection() -> bool:
    """检查数据库连接是否正常"""
    from sqlalchemy import text
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return False


def is_mysql_configured() -> bool:
    """检查是否配置了 MySQL"""
    return bool(MYSQL_HOST and MYSQL_USER and MYSQL_PASSWORD and MYSQL_DATABASE)