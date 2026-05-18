"""
SQLAlchemy 异步模型定义 - MySQL
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, ForeignKey,
    UniqueConstraint, Index, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ========== 用户模块 ==========

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_key: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    clothes: Mapped[List["Clothes"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    user_settings: Mapped[Optional["UserSettings"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    recommendation_records: Mapped[List["RecommendationRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    horoscope_records: Mapped[List["HoroscopeRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    theme: Mapped[str] = mapped_column(String(20), default="light")
    language: Mapped[str] = mapped_column(String(10), default="zh-CN")
    default_location: Mapped[Optional[str]] = mapped_column(String(100))
    zodiac_sign: Mapped[Optional[str]] = mapped_column(String(20))
    temperature_unit: Mapped[str] = mapped_column(String(10), default="celsius")
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    user: Mapped["User"] = relationship(back_populates="user_settings")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    token_type: Mapped[str] = mapped_column(String(20), default="refresh")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

    __table_args__ = (
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_expires", "expires_at"),
    )


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    permissions: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )


class AdminLog(Base):
    __tablename__ = "admin_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[Optional[int]] = mapped_column(Integer)
    details: Mapped[Optional[str]] = mapped_column(Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("idx_admin_logs_admin", "admin_id"),
        Index("idx_admin_logs_created", "created_at"),
    )


# ========== 衣物模块 ==========

class Clothes(Base):
    __tablename__ = "clothes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), default=1
    )
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    item: Mapped[str] = mapped_column(String(100), nullable=False)
    style_semantics: Mapped[Optional[str]] = mapped_column(Text)
    season_semantics: Mapped[Optional[str]] = mapped_column(Text)
    usage_semantics: Mapped[Optional[str]] = mapped_column(Text)
    color_semantics: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_key: Mapped[str] = mapped_column(String(255), nullable=False)
    image_filename: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    user: Mapped["User"] = relationship("User", back_populates="clothes")

    __table_args__ = (
        Index("idx_clothes_user_id", "user_id"),
        Index("idx_clothes_category", "category"),
        Index("idx_clothes_category_user", "category", "user_id"),
        Index("idx_clothes_created_at", "created_at"),
    )


# ========== 推荐模块 ==========

class RecommendationRecord(Base):
    __tablename__ = "recommendation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    record_date: Mapped[str] = mapped_column(String(10), nullable=False)
    weather_location: Mapped[Optional[str]] = mapped_column(String(100))
    weather_data: Mapped[Optional[str]] = mapped_column(Text)
    horoscope_data: Mapped[Optional[str]] = mapped_column(Text)
    recommendation_text: Mapped[Optional[str]] = mapped_column(Text)
    outfit_summary: Mapped[Optional[str]] = mapped_column(Text)
    selection_reasons: Mapped[Optional[str]] = mapped_column(Text)
    suggested_top_id: Mapped[Optional[int]] = mapped_column(Integer)
    suggested_bottom_id: Mapped[Optional[int]] = mapped_column(Integer)
    suggested_shoes_id: Mapped[Optional[int]] = mapped_column(Integer)
    suggested_accessory_ids: Mapped[Optional[str]] = mapped_column(Text)
    purchase_suggestions: Mapped[Optional[str]] = mapped_column(Text)
    goal_raw: Mapped[Optional[str]] = mapped_column(Text)
    goal_normalized: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    user: Mapped["User"] = relationship("User", back_populates="recommendation_records")
    favorites: Mapped[List["FavoriteRecommendation"]] = relationship(
        back_populates="recommendation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_recommendation_user_id", "user_id"),
        Index("idx_recommendation_date", "user_id", "record_date"),
    )


class FavoriteRecommendation(Base):
    __tablename__ = "favorite_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    recommendation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recommendation_records.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    user: Mapped["User"] = relationship("User")
    recommendation: Mapped["RecommendationRecord"] = relationship(
        "RecommendationRecord", back_populates="favorites"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "recommendation_id", name="uq_favorite_user_rec"),
        Index("idx_favorite_user_id", "user_id"),
        Index("idx_favorite_recommendation_id", "recommendation_id"),
    )


# ========== 星座运势模块 ==========

class HoroscopeRecord(Base):
    __tablename__ = "horoscope_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), default=1
    )
    record_date: Mapped[str] = mapped_column(String(10), nullable=False)
    zodiac_sign: Mapped[str] = mapped_column(String(20), nullable=False)
    zodiac_name: Mapped[str] = mapped_column(String(50), nullable=False)
    source_provider: Mapped[str] = mapped_column(String(20), nullable=False)
    source_payload: Mapped[str] = mapped_column(Text, nullable=False)
    llm_status: Mapped[str] = mapped_column(String(20), default="pending")
    llm_reasoning: Mapped[Optional[str]] = mapped_column(Text)
    llm_error: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    user: Mapped["User"] = relationship("User", back_populates="horoscope_records")

    __table_args__ = (
        UniqueConstraint(
            "user_id", "record_date", "zodiac_sign", name="uq_horoscope_user_date_sign"
        ),
        Index("idx_horoscope_user_date", "user_id", "record_date", "zodiac_sign"),
    )