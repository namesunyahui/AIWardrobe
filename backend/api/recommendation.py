"""
AI穿搭推荐 API 路由
基于天气的智能穿搭推荐
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from services.weather import get_weather, normalize_location_request, DEFAULT_LOCATION_QUERY
from services.recommendation import get_ai_recommendation
from services.auth import CurrentUser, get_current_user
from storage.db import get_user_settings
from api.recommendation_extra import save_recommendation_record
from pydantic import BaseModel, Field

router = APIRouter()


class RecommendationResponse(BaseModel):
    """推荐响应"""
    weather: dict
    horoscope: Optional[dict] = None
    temperature_rule: Optional[dict] = None
    recommendation_text: str
    outfit_summary: Optional[str] = None
    selection_reasons: Optional[dict] = None
    suggested_top: Optional[dict] = None
    suggested_bottom: Optional[dict] = None
    suggested_shoes: Optional[dict] = None
    suggested_accessories: list[dict] = Field(default_factory=list)
    purchase_suggestions: list[dict] = Field(default_factory=list)
    goal_raw: Optional[str] = None
    goal_normalized: Optional[str] = None
    record_id: Optional[int] = None


@router.get("/recommendation", response_model=RecommendationResponse)
async def get_outfit_recommendation(
    location: str = Query(
        default=DEFAULT_LOCATION_QUERY,
        description="城市名 或 经纬度坐标(如 '31.23,121.47' 或 '121.47,31.23')"
    ),
    city: Optional[str] = Query(default=None, description="城市（结构化查询参数）"),
    state: Optional[str] = Query(default=None, description="省/州（结构化查询参数）"),
    country: Optional[str] = Query(default=None, description="国家（结构化查询参数）"),
    zodiac_sign: Optional[str] = Query(
        default=None,
        description="可选，临时指定星座（会覆盖设置中的星座）"
    ),
    goal: Optional[str] = Query(default=None, description="可选，用户本次穿搭目标/场景"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取AI穿搭推荐

    参数:
        location: 城市名（如 上海、Tokyo）或 经纬度坐标（如 31.23,121.47）
    返回:
        天气信息 + AI推荐文本 + 推荐的衣服和裤子
    """
    normalized_location, validation_error = normalize_location_request(
        location=location,
        city=city,
        state=state,
        country=country,
    )
    if validation_error:
        raise HTTPException(status_code=422, detail=validation_error)

    # 获取天气信息
    weather = await get_weather(normalized_location)

    if not weather:
        raise HTTPException(status_code=500, detail="获取天气信息失败")

    # 如果没有临时指定星座，从用户设置中获取，再从全局配置获取
    if not zodiac_sign:
        user_settings = await get_user_settings(current_user.user_id)
        if user_settings:
            zodiac_sign = user_settings.get("zodiac_sign")
        if not zodiac_sign:
            from storage.config_store import load_config
            config = load_config()
            zodiac_sign = config.zodiac_sign if config.zodiac_sign and len(config.zodiac_sign) <= 10 else ""

    # 获取AI推荐
    recommendation = await get_ai_recommendation(weather, zodiac_sign=zodiac_sign, goal=goal, user_id=current_user.user_id)

    # 保存推荐历史记录
    record_id = None
    try:
        # normalized_location 是字符串（城市名）
        weather_location = normalized_location if isinstance(normalized_location, str) else location

        # 获取推荐结果中的数据
        rec_dict = recommendation.dict() if hasattr(recommendation, 'dict') else recommendation

        # 将 weather 转换为 dict
        weather_dict = weather.dict() if hasattr(weather, 'dict') else weather

        record_id = await save_recommendation_record(
            user_id=current_user.user_id,
            weather_data=weather_dict,
            horoscope_data=rec_dict.get("horoscope", {}),
            recommendation_text=rec_dict.get("recommendation_text", ""),
            outfit_summary=rec_dict.get("outfit_summary", ""),
            selection_reasons=rec_dict.get("selection_reasons", {}),
            suggested_top_id=rec_dict.get("suggested_top", {}).get("id") if rec_dict.get("suggested_top") else None,
            suggested_bottom_id=rec_dict.get("suggested_bottom", {}).get("id") if rec_dict.get("suggested_bottom") else None,
            suggested_shoes_id=rec_dict.get("suggested_shoes", {}).get("id") if rec_dict.get("suggested_shoes") else None,
            suggested_accessory_ids=[a.get("id") for a in rec_dict.get("suggested_accessories", []) if a.get("id")],
            purchase_suggestions=rec_dict.get("purchase_suggestions", []),
            goal_raw=goal or "",
            goal_normalized=rec_dict.get("goal_normalized", ""),
            weather_location=weather_location
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[Warning] Failed to save recommendation record: {e}")

    # 返回结果时添加 record_id
    result = recommendation.dict() if hasattr(recommendation, 'dict') else recommendation
    result['record_id'] = record_id

    return result
