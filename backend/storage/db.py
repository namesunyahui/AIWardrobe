"""
数据库连接和 CRUD 操作 - MySQL (SQLAlchemy 异步)
"""
import os
import json
import asyncio
import aiosqlite
from pathlib import Path
from typing import Any, List, Optional
from datetime import datetime

from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.clothes import ClothesItem, ClothesCreate
from storage.database import get_session_maker, init_db, check_db_connection, is_mysql_configured
from storage.models_mysql import (
    User, UserSettings, RefreshToken, Admin, AdminLog,
    Clothes, RecommendationRecord, FavoriteRecommendation, HoroscopeRecord
)
from services.minio import get_minio_service

# SQLite 旧数据路径（用于迁移）
_default_sqlite_path = Path(__file__).parent.parent / "wardrobe.db"
SQLITE_DB_PATH = Path(os.getenv("DB_FILE_PATH", _default_sqlite_path))

# 为了兼容性，导出 DB_PATH
DB_PATH = SQLITE_DB_PATH


async def init_db_with_migration():
    """初始化数据库并迁移旧数据（如果需要）"""
    # 初始化 MySQL 表结构
    from storage.database import init_db as db_init
    await db_init()

    # 检查是否需要从 SQLite 迁移数据
    if SQLITE_DB_PATH.exists() and SQLITE_DB_PATH.stat().st_size > 0:
        await migrate_from_sqlite()


async def migrate_from_sqlite():
    """从 SQLite 迁移数据到 MySQL"""
    try:
        import aiosqlite

        # 检查 MySQL 是否已有数据
        async_session_maker = get_session_maker()
        async with async_session_maker() as session:
            result = await session.execute(select(User).limit(1))
            if result.scalar_one_or_none():
                return  # MySQL 已有数据，跳过迁移

        # 检查 SQLite 是否有数据
        async with aiosqlite.connect(SQLITE_DB_PATH) as sqlite_db:
            cursor = await sqlite_db.execute("SELECT COUNT(*) FROM clothes")
            count = (await cursor.fetchone())[0]
            if count == 0:
                return  # SQLite 没有数据

            print(f"检测到 SQLite 旧数据，开始迁移...")

            # 迁移用户
            await _migrate_users_sqlite(sqlite_db)

            # 迁移用户设置
            await _migrate_user_settings_sqlite(sqlite_db)

            # 迁移衣物
            await _migrate_clothes_sqlite(sqlite_db)

            # 迁移星座运势
            await _migrate_horoscope_sqlite(sqlite_db)

            print("数据迁移完成！")

    except Exception as e:
        print(f"迁移过程中出错: {e}")


async def _migrate_users_sqlite(sqlite_db):
    """迁移用户数据"""
    sqlite_db.row_factory = aiosqlite.Row
    cursor = await sqlite_db.execute(
        "SELECT * FROM users WHERE is_deleted = 0"
    )
    users = await cursor.fetchall()

    if not users:
        return

    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        for user in users:
            session.add(User(
                username=user["username"],
                email=user["email"],
                password_hash=user["password_hash"],
                nickname=user["nickname"],
                avatar_key=user["avatar_key"],
                role=user["role"] or "user",
                is_active=bool(user["is_active"]) if user["is_active"] is not None else True,
                is_deleted=bool(user["is_deleted"]) if user["is_deleted"] is not None else False,
                created_at=datetime.fromisoformat(user["created_at"]) if user["created_at"] else datetime.now(),
                updated_at=datetime.fromisoformat(user["updated_at"]) if user["updated_at"] else datetime.now()
            ))
        await session.commit()

    print(f"迁移了 {len(users)} 个用户")


async def _migrate_user_settings_sqlite(sqlite_db):
    """迁移用户设置"""
    sqlite_db.row_factory = aiosqlite.Row
    cursor = await sqlite_db.execute("SELECT * FROM user_settings")
    settings = await cursor.fetchall()

    if not settings:
        return

    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        for s in settings:
            session.add(UserSettings(
                user_id=s["user_id"],
                theme=s["theme"] or "light",
                language=s["language"] or "zh-CN",
                default_location=s["default_location"],
                zodiac_sign=s["zodiac_sign"],
                temperature_unit=s["temperature_unit"] or "celsius",
                notification_enabled=bool(s["notification_enabled"]) if s["notification_enabled"] is not None else True,
                created_at=datetime.fromisoformat(s["created_at"]) if s["created_at"] else datetime.now(),
                updated_at=datetime.fromisoformat(s["updated_at"]) if s["updated_at"] else datetime.now()
            ))
        await session.commit()

    print(f"迁移了 {len(settings)} 条用户设置")


async def _migrate_clothes_sqlite(sqlite_db):
    """迁移衣物数据"""
    sqlite_db.row_factory = aiosqlite.Row
    cursor = await sqlite_db.execute("SELECT * FROM clothes")
    clothes = await cursor.fetchall()

    if not clothes:
        return

    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        for c in clothes:
            session.add(Clothes(
                user_id=c["user_id"] if c["user_id"] else 1,
                category=c["category"],
                item=c["item"],
                style_semantics=c["style_semantics"],
                season_semantics=c["season_semantics"],
                usage_semantics=c["usage_semantics"],
                color_semantics=c["color_semantics"],
                description=c["description"],
                image_key=c["image_key"] or c["image_filename"],
                image_filename=c["image_filename"],
                created_at=datetime.fromisoformat(c["created_at"]) if c["created_at"] else datetime.now(),
                updated_at=datetime.fromisoformat(c["updated_at"]) if c["updated_at"] else datetime.now()
            ))
        await session.commit()

    print(f"迁移了 {len(clothes)} 件衣物")


async def _migrate_horoscope_sqlite(sqlite_db):
    """迁移星座运势数据"""
    sqlite_db.row_factory = aiosqlite.Row
    cursor = await sqlite_db.execute("SELECT * FROM horoscope_records")
    records = await cursor.fetchall()

    if not records:
        return

    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        for r in records:
            session.add(HoroscopeRecord(
                user_id=r["user_id"] if r["user_id"] else 1,
                record_date=r["record_date"],
                zodiac_sign=r["zodiac_sign"],
                zodiac_name=r["zodiac_name"],
                source_provider=r["source_provider"],
                source_payload=r["source_payload"],
                llm_status=r["llm_status"] or "pending",
                llm_reasoning=r["llm_reasoning"],
                llm_error=r["llm_error"],
                created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else datetime.now(),
                updated_at=datetime.fromisoformat(r["updated_at"]) if r["updated_at"] else datetime.now()
            ))
        await session.commit()

    print(f"迁移了 {len(records)} 条星座运势记录")


# ========== 衣物 CRUD ==========

async def add_clothes(clothes: ClothesCreate, user_id: int = 1) -> int:
    """添加衣物到数据库"""
    image_key = clothes.image_filename

    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        db_clothes = Clothes(
            user_id=user_id,
            category=clothes.category,
            item=clothes.item,
            style_semantics=json.dumps(clothes.style_semantics),
            season_semantics=json.dumps(clothes.season_semantics),
            usage_semantics=json.dumps(clothes.usage_semantics),
            color_semantics=clothes.color_semantics,
            description=clothes.description,
            image_filename=clothes.image_filename,
            image_key=image_key
        )
        session.add(db_clothes)
        await session.commit()
        return db_clothes.id


async def get_all_clothes(user_id: int = None) -> List[ClothesItem]:
    """获取所有衣物（可按用户过滤）"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        if user_id:
            stmt = select(Clothes).where(Clothes.user_id == user_id).order_by(Clothes.created_at.desc())
        else:
            stmt = select(Clothes).order_by(Clothes.created_at.desc())

        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [_db_clothes_to_item(row) for row in rows]


async def get_clothes_by_user(user_id: int) -> List[ClothesItem]:
    """获取指定用户的所有衣物"""
    return await get_all_clothes(user_id)


async def get_clothes_by_category(category: str, user_id: int = None) -> List[ClothesItem]:
    """按类别获取衣物（可按用户过滤）"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        if user_id:
            stmt = select(Clothes).where(
                Clothes.category == category,
                Clothes.user_id == user_id
            ).order_by(Clothes.created_at.desc())
        else:
            stmt = select(Clothes).where(
                Clothes.category == category
            ).order_by(Clothes.created_at.desc())

        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [_db_clothes_to_item(row) for row in rows]


async def get_clothes_by_id(clothes_id: int, user_id: int = None) -> Optional[ClothesItem]:
    """按 ID 获取衣物（可按用户过滤）"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        if user_id:
            stmt = select(Clothes).where(
                Clothes.id == clothes_id,
                Clothes.user_id == user_id
            )
        else:
            stmt = select(Clothes).where(Clothes.id == clothes_id)

        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row:
            return _db_clothes_to_item(row)
        return None


async def get_clothes_image_filename(clothes_id: int, user_id: int = None) -> Optional[str]:
    """获取衣物的完整图片路径（包含用户ID前缀）"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        if user_id:
            stmt = select(Clothes).where(
                Clothes.id == clothes_id,
                Clothes.user_id == user_id
            )
        else:
            stmt = select(Clothes).where(Clothes.id == clothes_id)

        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row:
            # 使用 image_key 或 image_filename，并添加用户ID前缀
            filename = row.image_key or row.image_filename or ""
            if filename and "/" not in filename:
                filename = f"{row.user_id}/clothes/{filename}"
            return filename
        return None


async def delete_clothes(clothes_id: int, user_id: int = None) -> bool:
    """删除衣物（可按用户过滤），同时删除 MinIO 中的图片"""
    # 先获取图片的 image_key，以便删除 MinIO 中的文件
    image_key = await get_clothes_image_filename(clothes_id, user_id)

    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        if user_id:
            stmt = delete(Clothes).where(
                Clothes.id == clothes_id,
                Clothes.user_id == user_id
            )
        else:
            stmt = delete(Clothes).where(Clothes.id == clothes_id)

        result = await session.execute(stmt)
        await session.commit()
        deleted = result.rowcount > 0

    # 如果删除成功，删除 MinIO 中的图片
    if deleted and image_key:
        try:
            from services.minio import delete_from_minio
            await delete_from_minio(image_key)
        except Exception as e:
            print(f"删除 MinIO 图片失败: {e}")

    return deleted


async def update_clothes(clothes_id: int, clothes: ClothesCreate, user_id: int = None) -> bool:
    """更新衣物信息（可按用户过滤）"""
    image_key = clothes.image_filename

    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        if user_id:
            stmt = (
                update(Clothes)
                .where(Clothes.id == clothes_id, Clothes.user_id == user_id)
                .values(
                    category=clothes.category,
                    item=clothes.item,
                    style_semantics=json.dumps(clothes.style_semantics),
                    season_semantics=json.dumps(clothes.season_semantics),
                    usage_semantics=json.dumps(clothes.usage_semantics),
                    color_semantics=clothes.color_semantics,
                    description=clothes.description,
                    image_filename=clothes.image_filename,
                    image_key=image_key,
                    updated_at=datetime.now()
                )
            )
        else:
            stmt = (
                update(Clothes)
                .where(Clothes.id == clothes_id)
                .values(
                    category=clothes.category,
                    item=clothes.item,
                    style_semantics=json.dumps(clothes.style_semantics),
                    season_semantics=json.dumps(clothes.season_semantics),
                    usage_semantics=json.dumps(clothes.usage_semantics),
                    color_semantics=clothes.color_semantics,
                    description=clothes.description,
                    image_filename=clothes.image_filename,
                    image_key=image_key,
                    updated_at=datetime.now()
                )
            )

        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


def _db_clothes_to_item(row: Clothes) -> ClothesItem:
    """将数据库行转换为 ClothesItem"""
    # 获取文件名
    filename = row.image_key or row.image_filename or ""
    # 如果文件名不包含用户ID前缀，则添加
    if filename and "/" not in filename:
        filename = f"{row.user_id}/clothes/{filename}"
    # 使用 MinIO 服务获取图片 URL
    minio_service = get_minio_service()
    image_url = minio_service.get_image_url(filename)
    return ClothesItem(
        id=row.id,
        category=row.category,
        item=row.item,
        style_semantics=json.loads(row.style_semantics or "[]"),
        season_semantics=json.loads(row.season_semantics or "[]"),
        usage_semantics=json.loads(row.usage_semantics or "[]"),
        color_semantics=row.color_semantics or "",
        description=row.description or "",
        image_url=image_url,
        created_at=row.created_at if row.created_at else datetime.now()
    )


# ========== 星座运势 CRUD ==========

async def get_horoscope_record(record_date: str, zodiac_sign: str) -> Optional[dict[str, Any]]:
    """按日期和星座获取缓存的运势记录"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = select(HoroscopeRecord).where(
            HoroscopeRecord.record_date == record_date,
            HoroscopeRecord.zodiac_sign == zodiac_sign
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if not row:
            return None
        return _db_horoscope_to_dict(row)


async def upsert_horoscope_source(
    record_date: str,
    zodiac_sign: str,
    zodiac_name: str,
    source_provider: str,
    source_payload: dict[str, Any],
) -> int:
    """写入或更新星座原始数据"""
    payload_json = json.dumps(source_payload, ensure_ascii=False)

    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = select(HoroscopeRecord).where(
            HoroscopeRecord.record_date == record_date,
            HoroscopeRecord.zodiac_sign == zodiac_sign
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.zodiac_name = zodiac_name
            existing.source_provider = source_provider
            existing.source_payload = payload_json
            existing.updated_at = datetime.now()
            await session.commit()
            return existing.id

        new_record = HoroscopeRecord(
            record_date=record_date,
            zodiac_sign=zodiac_sign,
            zodiac_name=zodiac_name,
            source_provider=source_provider,
            source_payload=payload_json,
            llm_status="pending"
        )
        session.add(new_record)
        await session.commit()
        return new_record.id


async def update_horoscope_inference(
    record_id: int,
    llm_status: str,
    llm_reasoning: Optional[str] = None,
    llm_error: Optional[str] = None,
) -> None:
    """更新运势推理状态与结果"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = (
            update(HoroscopeRecord)
            .where(HoroscopeRecord.id == record_id)
            .values(
                llm_status=llm_status,
                llm_reasoning=llm_reasoning,
                llm_error=llm_error,
                updated_at=datetime.now()
            )
        )
        await session.execute(stmt)
        await session.commit()


def _db_horoscope_to_dict(row: HoroscopeRecord) -> dict[str, Any]:
    """将数据库行转换为字典"""
    return {
        "id": row.id,
        "record_date": row.record_date,
        "zodiac_sign": row.zodiac_sign,
        "zodiac_name": row.zodiac_name,
        "source_provider": row.source_provider or "unknown",
        "source_payload": json.loads(row.source_payload or "{}"),
        "llm_status": row.llm_status or "pending",
        "llm_reasoning": row.llm_reasoning or "",
        "llm_error": row.llm_error or "",
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


# ========== 用户相关 CRUD ==========

async def create_user(username: str, email: str, password_hash: str, nickname: str = None) -> int:
    """创建用户"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            nickname=nickname or username
        )
        session.add(user)
        await session.flush()

        # 创建默认用户设置
        settings = UserSettings(user_id=user.id)
        session.add(settings)
        await session.commit()
        return user.id


async def get_user_by_username(username: str) -> Optional[dict]:
    """按用户名获取用户"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = select(User).where(User.username == username, User.is_deleted == False)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return _db_user_to_dict(row) if row else None


async def get_user_by_email(email: str) -> Optional[dict]:
    """按邮箱获取用户"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = select(User).where(User.email == email, User.is_deleted == False)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return _db_user_to_dict(row) if row else None


async def get_user_by_id(user_id: int) -> Optional[dict]:
    """按 ID 获取用户"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = select(User).where(User.id == user_id, User.is_deleted == False)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return _db_user_to_dict(row) if row else None


async def update_user_password(user_id: int, password_hash: str) -> bool:
    """更新用户密码"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(password_hash=password_hash, updated_at=datetime.now())
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


async def update_user_profile(user_id: int, nickname: str = None, avatar_key: str = None) -> bool:
    """更新用户资料"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        updates = {}
        if nickname is not None:
            updates["nickname"] = nickname
        if avatar_key is not None:
            updates["avatar_key"] = avatar_key

        if not updates:
            return False

        updates["updated_at"] = datetime.now()
        stmt = update(User).where(User.id == user_id).values(**updates)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


async def deactivate_user(user_id: int) -> bool:
    """禁用用户（软删除）"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=False, updated_at=datetime.now())
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


async def activate_user(user_id: int) -> bool:
    """启用用户"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=True, updated_at=datetime.now())
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


async def delete_user(user_id: int) -> bool:
    """删除用户（软删除）"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_deleted=True, updated_at=datetime.now())
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


def _db_user_to_dict(row: User) -> dict:
    """将数据库行转换为用户字典"""
    return {
        "id": row.id,
        "username": row.username,
        "email": row.email,
        "password_hash": row.password_hash,
        "nickname": row.nickname,
        "avatar_key": row.avatar_key,
        "role": row.role,
        "is_active": row.is_active,
        "is_deleted": row.is_deleted,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


# ========== Token 黑名单 ==========

async def add_refresh_token(user_id: int, token_hash: str, expires_at: str) -> int:
    """添加 refresh token 到黑名单"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.fromisoformat(expires_at)
        )
        session.add(token)
        await session.commit()
        return token.id


async def is_token_revoked(token_hash: str) -> bool:
    """检查 token 是否已在黑名单中"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None


async def cleanup_expired_tokens() -> int:
    """清理过期的 token 记录"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = delete(RefreshToken).where(RefreshToken.expires_at < datetime.now())
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount


# ========== 用户设置 ==========

async def get_user_settings(user_id: int) -> Optional[dict]:
    """获取用户设置"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return _db_settings_to_dict(row) if row else None


async def update_user_settings(user_id: int, **kwargs) -> bool:
    """更新用户设置"""
    if not kwargs:
        return False

    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        kwargs["updated_at"] = datetime.now()
        stmt = update(UserSettings).where(UserSettings.user_id == user_id).values(**kwargs)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


def _db_settings_to_dict(row: UserSettings) -> dict:
    """将数据库行转换为设置字典"""
    return {
        "id": row.id,
        "user_id": row.user_id,
        "theme": row.theme,
        "language": row.language,
        "default_location": row.default_location,
        "zodiac_sign": row.zodiac_sign,
        "temperature_unit": row.temperature_unit,
        "notification_enabled": row.notification_enabled,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


# ========== 管理员 ==========

async def get_admin_by_user_id(user_id: int) -> Optional[dict]:
    """获取用户的管理员信息"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = select(Admin).where(Admin.user_id == user_id)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return _db_admin_to_dict(row) if row else None


async def add_admin(user_id: int, permissions: str, created_by: int = None) -> int:
    """添加管理员"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        admin = Admin(
            user_id=user_id,
            permissions=permissions,
            created_by=created_by
        )
        session.add(admin)
        await session.commit()
        return admin.id


def _db_admin_to_dict(row: Admin) -> dict:
    """将数据库行转换为管理员字典"""
    return {
        "id": row.id,
        "user_id": row.user_id,
        "permissions": row.permissions,
        "created_by": row.created_by,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


# ========== 推荐记录 CRUD ==========

async def add_recommendation_record(
    user_id: int,
    record_date: str,
    weather_location: str = None,
    weather_data: str = None,
    horoscope_data: str = None,
    recommendation_text: str = None,
    outfit_summary: str = None,
    selection_reasons: str = None,
    suggested_top_id: int = None,
    suggested_bottom_id: int = None,
    suggested_shoes_id: int = None,
    suggested_accessory_ids: str = None,
    purchase_suggestions: str = None,
    goal_raw: str = None,
    goal_normalized: str = None,
) -> int:
    """添加推荐记录"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        record = RecommendationRecord(
            user_id=user_id,
            record_date=record_date,
            weather_location=weather_location,
            weather_data=weather_data,
            horoscope_data=horoscope_data,
            recommendation_text=recommendation_text,
            outfit_summary=outfit_summary,
            selection_reasons=selection_reasons,
            suggested_top_id=suggested_top_id,
            suggested_bottom_id=suggested_bottom_id,
            suggested_shoes_id=suggested_shoes_id,
            suggested_accessory_ids=suggested_accessory_ids,
            purchase_suggestions=purchase_suggestions,
            goal_raw=goal_raw,
            goal_normalized=goal_normalized,
        )
        session.add(record)
        await session.commit()
        return record.id


async def get_recommendation_records(user_id: int, limit: int = 10) -> List[dict]:
    """获取用户的推荐记录"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = (
            select(RecommendationRecord)
            .where(RecommendationRecord.user_id == user_id)
            .order_by(RecommendationRecord.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [_db_recommendation_to_dict(row) for row in rows]


async def get_recommendation_record_by_id(record_id: int, user_id: int = None) -> Optional[dict]:
    """获取单条推荐记录"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        if user_id:
            stmt = select(RecommendationRecord).where(
                RecommendationRecord.id == record_id,
                RecommendationRecord.user_id == user_id
            )
        else:
            stmt = select(RecommendationRecord).where(RecommendationRecord.id == record_id)

        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        return _db_recommendation_to_dict(row) if row else None


def _db_recommendation_to_dict(row: RecommendationRecord) -> dict:
    """将数据库行转换为推荐记录字典"""
    return {
        "id": row.id,
        "user_id": row.user_id,
        "record_date": row.record_date,
        "weather_location": row.weather_location,
        "weather_data": json.loads(row.weather_data) if row.weather_data else None,
        "horoscope_data": json.loads(row.horoscope_data) if row.horoscope_data else None,
        "recommendation_text": row.recommendation_text,
        "outfit_summary": row.outfit_summary,
        "selection_reasons": row.selection_reasons,
        "suggested_top_id": row.suggested_top_id,
        "suggested_bottom_id": row.suggested_bottom_id,
        "suggested_shoes_id": row.suggested_shoes_id,
        "suggested_accessory_ids": json.loads(row.suggested_accessory_ids) if row.suggested_accessory_ids else None,
        "purchase_suggestions": row.purchase_suggestions,
        "goal_raw": row.goal_raw,
        "goal_normalized": row.goal_normalized,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


# ========== 收藏 CRUD ==========

async def add_favorite_recommendation(user_id: int, recommendation_id: int) -> bool:
    """添加收藏"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        # 检查是否已收藏
        stmt = select(FavoriteRecommendation).where(
            FavoriteRecommendation.user_id == user_id,
            FavoriteRecommendation.recommendation_id == recommendation_id
        )
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            return False

        favorite = FavoriteRecommendation(
            user_id=user_id,
            recommendation_id=recommendation_id
        )
        session.add(favorite)
        await session.commit()
        return True


async def remove_favorite_recommendation(user_id: int, recommendation_id: int) -> bool:
    """移除收藏"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = delete(FavoriteRecommendation).where(
            FavoriteRecommendation.user_id == user_id,
            FavoriteRecommendation.recommendation_id == recommendation_id
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


async def get_user_favorites(user_id: int) -> List[dict]:
    """获取用户的所有收藏"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = (
            select(FavoriteRecommendation)
            .where(FavoriteRecommendation.user_id == user_id)
            .order_by(FavoriteRecommendation.created_at.desc())
        )
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [_db_favorite_to_dict(row) for row in rows]


async def is_favorite(user_id: int, recommendation_id: int) -> bool:
    """检查是否已收藏"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = select(FavoriteRecommendation).where(
            FavoriteRecommendation.user_id == user_id,
            FavoriteRecommendation.recommendation_id == recommendation_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None


def _db_favorite_to_dict(row: FavoriteRecommendation) -> dict:
    """将数据库行转换为收藏字典"""
    return {
        "id": row.id,
        "user_id": row.user_id,
        "recommendation_id": row.recommendation_id,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


# ========== 兼容性别名函数 ==========

async def add_favorite(user_id: int, recommendation_id: int) -> bool:
    """添加收藏（兼容别名）"""
    return await add_favorite_recommendation(user_id, recommendation_id)


async def remove_favorite(user_id: int, recommendation_id: int) -> bool:
    """移除收藏（兼容别名）"""
    return await remove_favorite_recommendation(user_id, recommendation_id)


async def is_favorited(user_id: int, recommendation_id: int) -> bool:
    """检查是否已收藏（兼容别名）"""
    return await is_favorite(user_id, recommendation_id)


async def delete_recommendation_record(record_id: int, user_id: int) -> bool:
    """删除推荐记录"""
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        stmt = delete(RecommendationRecord).where(
            RecommendationRecord.id == record_id,
            RecommendationRecord.user_id == user_id
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0


# ========== 兼容性函数（供旧代码调用）==========

# 为了兼容性，保留这些函数但指向新实现
async def init_db():
    """初始化数据库（兼容旧代码）"""
    await init_db_with_migration()


async def migrate_to_multiuser():
    """迁移到多用户版本（兼容旧代码）"""
    pass