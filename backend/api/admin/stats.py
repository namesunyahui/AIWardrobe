"""
管理员 - 统计 API
"""
from fastapi import APIRouter, Depends
from api.admin.deps import require_admin, require_permission
from services.auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/stats")
async def get_stats(
    current_user: CurrentUser = Depends(require_permission("stats:read"))
):
    """获取系统统计数据"""
    from storage.db import DB_PATH
    import aiosqlite
    from datetime import datetime, timedelta

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # 用户统计
        cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE is_deleted = 0")
        total_users = (await cursor.fetchone())["count"]

        cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE is_deleted = 0 AND is_active = 1")
        active_users = (await cursor.fetchone())["count"]

        cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE is_deleted = 0 AND is_active = 0")
        inactive_users = (await cursor.fetchone())["count"]

        # 今日新用户
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM users WHERE is_deleted = 0 AND date(created_at) = ?",
            (today,)
        )
        new_today = (await cursor.fetchone())["count"]

        # 衣物统计
        cursor = await db.execute("SELECT COUNT(*) as count FROM clothes")
        total_clothes = (await cursor.fetchone())["count"]

        # 按分类统计
        cursor = await db.execute(
            "SELECT category, COUNT(*) as count FROM clothes GROUP BY category"
        )
        category_rows = await cursor.fetchall()
        by_category = {row["category"]: row["count"] for row in category_rows}

        # 推荐统计
        cursor = await db.execute("SELECT COUNT(*) as count FROM recommendation_records WHERE date(created_at) = ?", (today,))
        recommendations_today = (await cursor.fetchone())["count"]

        cursor = await db.execute("SELECT COUNT(*) as count FROM recommendation_records")
        recommendations_total = (await cursor.fetchone())["count"]

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": inactive_users,
            "new_today": new_today
        },
        "clothes": {
            "total": total_clothes,
            "by_category": by_category
        },
        "recommendations": {
            "total_today": recommendations_today,
            "total": recommendations_total
        }
    }


@router.get("/stats/users")
async def get_user_stats(
    current_user: CurrentUser = Depends(require_permission("stats:read"))
):
    """获取用户统计数据"""
    from storage.db import DB_PATH
    import aiosqlite

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT
                date(created_at) as date,
                COUNT(*) as count
            FROM users
            WHERE is_deleted = 0
                AND created_at >= date('now', '-30 days')
            GROUP BY date(created_at)
            ORDER BY date
        """)
        rows = await cursor.fetchall()

    return {
        "items": [{"date": row["date"], "count": row["count"]} for row in rows]
    }


@router.get("/stats/usage")
async def get_usage_stats(
    current_user: CurrentUser = Depends(require_permission("stats:read"))
):
    """获取使用统计数据"""
    from storage.db import DB_PATH
    import aiosqlite

    async with aiosqlite.connect(DB_PATH) as db:
        # 衣物上传趋势（最近30天）
        cursor = await db.execute("""
            SELECT
                date(created_at) as date,
                COUNT(*) as count
            FROM clothes
            WHERE created_at >= date('now', '-30 days')
            GROUP BY date(created_at)
            ORDER BY date
        """)
        clothes_rows = await cursor.fetchall()

        # 推荐使用趋势
        cursor = await db.execute("""
            SELECT
                date(created_at) as date,
                COUNT(*) as count
            FROM recommendation_records
            WHERE created_at >= date('now', '-30 days')
            GROUP BY date(created_at)
            ORDER BY date
        """)
        recommendation_rows = await cursor.fetchall()

    return {
        "clothes_trend": [{"date": row["date"], "count": row["count"]} for row in clothes_rows],
        "recommendations_trend": [{"date": row["date"], "count": row["count"]} for row in recommendation_rows]
    }