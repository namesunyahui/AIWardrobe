"""
推荐历史和收藏 API - MySQL版本
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import select, func
import json
from services.auth import CurrentUser, get_current_user
from storage.db import (
    get_recommendation_records,
    get_recommendation_record_by_id,
    get_user_favorites,
    add_favorite,
    remove_favorite,
    is_favorited,
    get_user_by_id,
    add_recommendation_record,
)
from storage.database import get_session_maker
from storage.models_mysql import FavoriteRecommendation, RecommendationRecord

router = APIRouter()


# ========== 保存推荐记录函数 ==========

async def save_recommendation_record(
    user_id: int,
    weather_data: dict,
    horoscope_data: dict,
    recommendation_text: str,
    outfit_summary: str,
    selection_reasons: dict,
    suggested_top_id: int = None,
    suggested_bottom_id: int = None,
    suggested_shoes_id: int = None,
    suggested_accessory_ids: list = None,
    purchase_suggestions: list = None,
    goal_raw: str = "",
    goal_normalized: str = "",
    weather_location: str = "",
) -> int:
    """保存推荐记录到数据库"""
    from datetime import date
    record_date = date.today().isoformat()

    return await add_recommendation_record(
        user_id=user_id,
        record_date=record_date,
        weather_location=weather_location,
        weather_data=json.dumps(weather_data, ensure_ascii=False) if weather_data else None,
        horoscope_data=json.dumps(horoscope_data, ensure_ascii=False) if horoscope_data else None,
        recommendation_text=recommendation_text,
        outfit_summary=outfit_summary,
        selection_reasons=json.dumps(selection_reasons, ensure_ascii=False) if selection_reasons else None,
        suggested_top_id=suggested_top_id,
        suggested_bottom_id=suggested_bottom_id,
        suggested_shoes_id=suggested_shoes_id,
        suggested_accessory_ids=json.dumps(suggested_accessory_ids, ensure_ascii=False) if suggested_accessory_ids else None,
        purchase_suggestions=json.dumps(purchase_suggestions, ensure_ascii=False) if purchase_suggestions else None,
        goal_raw=goal_raw,
        goal_normalized=goal_normalized,
    )


class FavoriteResponse(BaseModel):
    """收藏响应"""
    message: str


class FavoriteCheckResponse(BaseModel):
    """检查收藏状态响应"""
    is_favorited: bool


# ===== 收藏相关路由 =====

@router.get("/recommendations/favorites")
async def get_favorites(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取收藏列表"""
    try:
        async_session_maker = get_session_maker()
        async with async_session_maker() as session:
            # 使用 JOIN 一次性获取收藏和推荐记录，避免 N+1 查询
            stmt = (
                select(FavoriteRecommendation, RecommendationRecord)
                .join(
                    RecommendationRecord,
                    FavoriteRecommendation.recommendation_id == RecommendationRecord.id
                )
                .where(FavoriteRecommendation.user_id == current_user.user_id)
                .order_by(FavoriteRecommendation.created_at.desc())
            )
            result = await session.execute(stmt)
            rows = result.all()

            total = len(rows)
            offset = (page - 1) * limit
            paginated = rows[offset:offset + limit]

            items = []
            for fav, rec in paginated:
                items.append({
                    "id": rec.id,
                    "record_date": rec.record_date,
                    "weather_location": rec.weather_location,
                    "recommendation_text": rec.recommendation_text,
                    "outfit_summary": rec.outfit_summary,
                    "goal_raw": rec.goal_raw,
                    "created_at": rec.created_at.isoformat() if hasattr(rec.created_at, 'isoformat') else rec.created_at,
                    "favorited_at": fav.created_at.isoformat() if hasattr(fav.created_at, 'isoformat') else fav.created_at,
                })

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": limit,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏列表失败: {str(e)}")


@router.post("/recommendations/{record_id}/favorite")
async def add_to_favorites(
    record_id: int = Path(..., description="推荐记录ID"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """添加收藏"""
    try:
        # 检查记录是否存在
        record = await get_recommendation_record_by_id(record_id, current_user.user_id)
        if not record:
            raise HTTPException(status_code=404, detail="推荐记录不存在")

        # 检查是否已收藏
        if await is_favorited(current_user.user_id, record_id):
            return FavoriteResponse(message="已经收藏过了")

        # 添加收藏
        await add_favorite(current_user.user_id, record_id)
        return FavoriteResponse(message="收藏成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"收藏失败: {str(e)}")


@router.delete("/recommendations/{record_id}/favorite")
async def remove_from_favorites(
    record_id: int = Path(..., description="推荐记录ID"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """取消收藏"""
    try:
        await remove_favorite(current_user.user_id, record_id)
        return FavoriteResponse(message="取消收藏成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消收藏失败: {str(e)}")


@router.get("/recommendations/{record_id}/favorite/status")
async def check_favorite_status(
    record_id: int = Path(..., description="推荐记录ID"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """检查收藏状态"""
    try:
        is_fav = await is_favorited(current_user.user_id, record_id)
        return FavoriteCheckResponse(is_favorited=is_fav)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查收藏状态失败: {str(e)}")


# ===== 推荐历史路由 =====

@router.get("/recommendations/history")
async def get_recommendation_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取推荐历史"""
    try:
        records = await get_recommendation_records(current_user.user_id, limit=100)

        # 批量获取收藏状态，避免 N+1 查询
        async_session_maker = get_session_maker()
        async with async_session_maker() as session:
            rec_ids = [r.get("id") for r in records if r.get("id")]
            favorited_ids = set()
            if rec_ids:
                stmt = select(FavoriteRecommendation.recommendation_id).where(
                    FavoriteRecommendation.user_id == current_user.user_id,
                    FavoriteRecommendation.recommendation_id.in_(rec_ids)
                )
                result = await session.execute(stmt)
                favorited_ids = {row[0] for row in result.all()}

        total = len(records)
        offset = (page - 1) * limit
        paginated = records[offset:offset + limit]

        items = []
        for rec in paginated:
            rec_id = rec.get("id")
            items.append({
                "id": rec_id,
                "record_date": rec.get("record_date"),
                "weather_location": rec.get("weather_location"),
                "recommendation_text": rec.get("recommendation_text"),
                "outfit_summary": rec.get("outfit_summary"),
                "goal_raw": rec.get("goal_raw"),
                "created_at": rec.get("created_at"),
                "is_favorited": rec_id in favorited_ids,
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": limit,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐历史失败: {str(e)}")


@router.get("/recommendations/{record_id}")
async def get_recommendation_detail(
    record_id: int = Path(..., description="推荐记录ID"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """获取推荐详情"""
    try:
        record = await get_recommendation_record_by_id(record_id, current_user.user_id)
        if not record:
            raise HTTPException(status_code=404, detail="推荐记录不存在")

        # 添加收藏状态
        record["is_favorited"] = await is_favorited(current_user.user_id, record_id)
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐详情失败: {str(e)}")


@router.delete("/recommendations/{record_id}")
async def delete_recommendation_record(
    record_id: int = Path(..., description="推荐记录ID"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """删除推荐记录"""
    try:
        from storage.db import delete_recommendation_record as db_delete_rec
        await db_delete_rec(record_id, current_user.user_id)
        return {"message": "删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")