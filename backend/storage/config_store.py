"""
配置存储 - 使用 JSON 文件持久化配置
"""
import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from domain.config import LLMConfig
from services.weather import validate_location_input, DEFAULT_LOCATION_QUERY

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

CONFIG_FILE = Path(__file__).parent / "llm_config.json"
_CONFIG_CACHE: Optional[LLMConfig] = None
_CONFIG_MTIME: Optional[float] = None


def load_config() -> LLMConfig:
    """加载 LLM 配置，优先从环境变量读取 API 配置，从 JSON 读取其他配置"""
    global _CONFIG_CACHE, _CONFIG_MTIME

    # 从环境变量读取 API 配置
    api_base = os.getenv("LLM_API_BASE")
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    removebg_api_key = os.getenv("REMOVE_BG_API_KEY")
    bg_removal_method = os.getenv("BG_REMOVAL_METHOD", "removebg")
    weather_location = os.getenv("WEATHER_LOCATION", "上海, 上海市, 中国")
    zodiac_sign = os.getenv("ZODIAC_SIGN")

    # 始终从 JSON 文件读取其他配置（如 zodiac_sign）
    json_config = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                json_config = json.load(f)
        except Exception:
            pass

    # 环境变量优先用于 API 配置，但使用 JSON 中的其他值作为默认值
    if api_base and api_key:
        _CONFIG_CACHE = LLMConfig(
            api_base=api_base,
            api_key=api_key,
            model=model or json_config.get("model", "gemini-flash-latest"),
            removebg_api_key=removebg_api_key or json_config.get("removebg_api_key", ""),
            bg_removal_method=bg_removal_method or json_config.get("bg_removal_method", "removebg"),
            weather_location=weather_location if weather_location != "上海, 上海市, 中国" else json_config.get("weather_location", "上海, 上海市, 中国"),
            zodiac_sign=zodiac_sign if zodiac_sign else json_config.get("zodiac_sign", "")
        )
        _CONFIG_MTIME = None
        return _CONFIG_CACHE

    # 回退到 JSON 文件
    if not CONFIG_FILE.exists():
        _CONFIG_CACHE = LLMConfig()
        _CONFIG_MTIME = None
        return _CONFIG_CACHE

    try:
        mtime = CONFIG_FILE.stat().st_mtime
    except Exception:
        mtime = None

    if _CONFIG_CACHE is not None and _CONFIG_MTIME == mtime:
        return _CONFIG_CACHE

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        _CONFIG_CACHE = LLMConfig(**data)
        _CONFIG_MTIME = mtime
        return _CONFIG_CACHE
    except Exception:
        _CONFIG_CACHE = LLMConfig()
        _CONFIG_MTIME = mtime
        return _CONFIG_CACHE


def save_config(config: LLMConfig) -> None:
    """保存 LLM 配置"""
    global _CONFIG_CACHE, _CONFIG_MTIME

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)

    _CONFIG_CACHE = config
    try:
        _CONFIG_MTIME = CONFIG_FILE.stat().st_mtime
    except Exception:
        _CONFIG_MTIME = None


def update_config(
    api_base: Optional[str] = None,
    api_key: Optional[str] = None, 
    model: Optional[str] = None,
    removebg_api_key: Optional[str] = None,
    bg_removal_method: Optional[str] = None,
    weather_location: Optional[str] = None,
    zodiac_sign: Optional[str] = None
) -> LLMConfig:
    """更新配置"""
    config = load_config()
    
    if api_base is not None:
        config.api_base = api_base.strip()
    if api_key is not None:
        config.api_key = api_key.strip()
    if model is not None:
        config.model = model.strip()
    if removebg_api_key is not None:
        config.removebg_api_key = removebg_api_key.strip()
    if bg_removal_method is not None:
        config.bg_removal_method = bg_removal_method
    if weather_location is not None:
        normalized_location = weather_location.strip() or DEFAULT_LOCATION_QUERY
        validation_error = validate_location_input(normalized_location)
        if validation_error:
            raise ValueError(validation_error)
        config.weather_location = normalized_location
    if zodiac_sign is not None:
        config.zodiac_sign = zodiac_sign.strip().lower()
    
    save_config(config)
    return config


def _mask_key(key: str) -> str:
    """对 API Key 进行脱敏处理"""
    if not key:
        return ""
    if len(key) > 8:
        return key[:4] + "*" * (len(key) - 8) + key[-4:]
    return "*" * len(key)


def get_masked_config() -> dict:
    """获取脱敏后的配置（隐藏 API Key）"""
    config = load_config()
    weather_location = (config.weather_location or "").strip() or DEFAULT_LOCATION_QUERY
    if validate_location_input(weather_location):
        weather_location = DEFAULT_LOCATION_QUERY
    
    return {
        "api_base": config.api_base,
        "api_key_masked": _mask_key(config.api_key),
        "has_api_key": bool(config.api_key),
        "model": config.model,
        "removebg_api_key_masked": _mask_key(config.removebg_api_key),
        "has_removebg_key": bool(config.removebg_api_key),
        "bg_removal_method": config.bg_removal_method,
        "weather_location": weather_location,
        "zodiac_sign": config.zodiac_sign
    }
