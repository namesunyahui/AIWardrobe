"""
衣柜 API - 获取和管理衣物
"""
from fastapi import APIRouter, HTTPException, Depends

from domain.clothes import ClothesItem, WardrobeResponse, ClothesCreate
from domain.clothes import normalize_category_value
from storage.db import (
    get_all_clothes,
    get_clothes_by_category,
    get_clothes_by_id,
    delete_clothes,
    update_clothes
)
from services.auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/wardrobe", response_model=WardrobeResponse)
async def get_wardrobe(current_user: CurrentUser = Depends(get_current_user)):
    """
    获取当前用户的整个衣柜

    按 top/bottom/shoes/accessory/uncategorized 五类返回所有衣物
    """
    all_clothes = await get_all_clothes(user_id=current_user.user_id)

    tops: list[ClothesItem] = []
    bottoms: list[ClothesItem] = []
    shoes: list[ClothesItem] = []
    accessories: list[ClothesItem] = []
    uncategorized: list[ClothesItem] = []

    for clothes in all_clothes:
        category = normalize_category_value(clothes.category)
        if category == "top":
            tops.append(clothes)
        elif category == "bottom":
            bottoms.append(clothes)
        elif category == "shoes":
            shoes.append(clothes)
        elif category == "accessory":
            accessories.append(clothes)
        elif category == "uncategorized":
            uncategorized.append(clothes)

    return WardrobeResponse(
        tops=tops,
        bottoms=bottoms,
        shoes=shoes,
        accessories=accessories,
        uncategorized=uncategorized
    )


@router.get("/wardrobe/{category}", response_model=list[ClothesItem])
async def get_wardrobe_category(category: str, current_user: CurrentUser = Depends(get_current_user)):
    """
    按类别获取衣物

    Args:
        category: top, bottom, shoes, accessory
    """
    category = normalize_category_value(category)
    if category not in ["top", "bottom", "shoes", "accessory"]:
        raise HTTPException(
            status_code=400,
            detail="类别必须是 top, bottom, shoes 或 accessory"
        )

    return await get_clothes_by_category(category, user_id=current_user.user_id)


@router.get("/clothes/{clothes_id}", response_model=ClothesItem)
async def get_clothes(clothes_id: int, current_user: CurrentUser = Depends(get_current_user)):
    """获取单个衣物详情"""
    clothes = await get_clothes_by_id(clothes_id, user_id=current_user.user_id)
    if not clothes:
        raise HTTPException(status_code=404, detail="衣物不存在")
    return clothes


@router.put("/clothes/{clothes_id}")
async def update_clothes_item(
    clothes_id: int,
    clothes: ClothesCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    """更新衣物信息"""
    success = await update_clothes(clothes_id, clothes, user_id=current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="衣物不存在")
    return {"message": "更新成功", "id": clothes_id}


@router.delete("/clothes/{clothes_id}")
async def remove_clothes(clothes_id: int, current_user: CurrentUser = Depends(get_current_user)):
    """删除衣物"""
    success = await delete_clothes(clothes_id, user_id=current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="衣物不存在")
    return {"message": "删除成功", "id": clothes_id}
