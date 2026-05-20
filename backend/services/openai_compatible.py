"""
OpenAI 兼容 API 服务
支持任何 OpenAI 风格的 API 接口
"""
import httpx
import base64
import json
import re
import asyncio
from typing import List, Optional
from storage.config_store import load_config
from domain.prompts import CLOTHES_SEMANTIC_PROMPT
from domain.clothes import ClothesSemantics
from domain.constants import normalize_api_base, MAX_RETRIES, INITIAL_DELAY


async def fetch_available_models() -> List[dict]:
    """
    获取可用模型列表
    """
    config = load_config()
    
    if not config.api_key:
        return []
    
    # 确保 api_base 格式正确
    api_base = normalize_api_base(config.api_base)
    
    url = f"{api_base}/models"
    
    try:
        async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
            response = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Claude/4.0 (Claude Code)",
                    "anthropic-client": "aiwardrobe",
                    "xanthropic-client": "ClaudeCode/4.0"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                # 过滤出支持视觉的模型（通常包含 vision, gpt-4o, claude 等关键词）
                return [
                    {"id": m["id"], "name": m.get("name", m["id"])}
                    for m in models
                ]
            else:
                error_msg = f"API请求失败 ({response.status_code}): {response.text[:200]}"
                print(error_msg)
                raise Exception(error_msg)
    except Exception as e:
        print(f"获取模型列表异常: {e}")
        raise Exception(f"连接异常: {str(e)}")


def extract_json_from_response(text: str) -> dict:
    """
    从响应中提取 JSON
    处理可能的 markdown 代码块包装、长文本、中文引号等问题
    """
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试提取 markdown 代码块中的 JSON
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试找到第一个完整的 JSON 对象（使用括号计数）
    first_brace = text.find('{')
    if first_brace == -1:
        raise ValueError(f"响应中没有找到 JSON: {text[:100]}...")

    # 从第一个 { 开始，逐字符追踪，提取完整的 JSON 对象
    json_str = ""
    brace_count = 0
    in_string = False
    escape_next = False

    for i in range(first_brace, len(text)):
        char = text[i]

        # 处理转义字符
        if escape_next:
            json_str += char
            escape_next = False
            continue

        if char == '\\' and in_string:
            json_str += char
            escape_next = True
            continue

        # 处理字符串
        if char == '"' and not escape_next:
            in_string = not in_string

        # 统计大括号
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:  # 找到了完整的 JSON
                    json_str = text[first_brace:i + 1]
                    break

        json_str += char

    if not json_str:
        raise ValueError(f"无法提取完整 JSON: {text[:200]}...")

    # 修复常见问题：中文引号、单引号等
    json_str = fix_common_json_errors(json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}, 内容: {json_str[:100]}...")


def fix_common_json_errors(text: str) -> str:
    """
    修复常见的 JSON 格式错误
    """
    import re

    # 1. 将中文引号替换为英文引号
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    # 2. 确保键使用双引号
    # 匹配 key: value 模式，key 不带引号的情况
    text = re.sub(r'([{,]\s*)(\w+):', r'\1"\2":', text)

    # 3. 处理值中的单引号（如果是字符串值）
    # 匹配 "key": 'value' -> "key": "value"
    text = re.sub(r'("[\w_]+":\s*)' + "'" + r'([^"\'\},\[\n]+)' + "'" + r'', r'\1"\2"', text)

    # 4. 移除可能存在的多余逗号（如 {a:,} 或 [a:,]）
    text = re.sub(r',(\s*[}\]])', r'\1', text)

    return text


async def analyze_clothes_openai(image_bytes: bytes) -> ClothesSemantics:
    """
    使用 OpenAI 兼容 API 分析衣物图片（带重试机制）

    Args:
        image_bytes: 图片的字节数据

    Returns:
        ClothesSemantics: 衣物语义信息
    """
    config = load_config()

    if not config.api_key:
        raise ValueError("请先配置 API Key")

    # 确保 api_base 格式正确
    api_base = normalize_api_base(config.api_base)

    url = f"{api_base}/chat/completions"

    # 将图片转换为 base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # 构建请求体
    payload = {
        "model": config.model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": CLOTHES_SEMANTIC_PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 3000
    }

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {config.api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "Claude/4.0 (Claude Code)",
                        "anthropic-client": "aiwardrobe",
                        "xanthropic-client": "ClaudeCode/4.0"
                    },
                    json=payload
                )

                if response.status_code == 429:
                    # 并发限制，等待后重试
                    delay = INITIAL_DELAY * (2 ** attempt)
                    print(f"API 并发限制，等待 {delay}s 后重试 (尝试 {attempt + 1}/{MAX_RETRIES})")
                    await asyncio.sleep(delay)
                    continue

                if response.status_code != 200:
                    raise ValueError(f"API 请求失败: {response.status_code} - {response.text}")

                data = response.json()

                # 提取响应内容
                raw_content = data["choices"][0]["message"].get("content")
                reasoning = data["choices"][0]["message"].get("reasoning", "")

                # 处理 content 为 None 的情况（某些模型如 kimi-k2.5 会把内容放在 reasoning 中）
                if raw_content is None:
                    content = reasoning
                else:
                    content = raw_content

                if not content:
                    raise ValueError("API 返回内容为空")

                # 解析 JSON
                try:
                    result = extract_json_from_response(content)
                except ValueError as e:
                    # JSON 解析失败，发送修正请求
                    print(f"JSON 解析失败，尝试修正: {e}")

                    # 构建修正请求
                    correction_payload = {
                        "model": config.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "你之前返回的不是有效的 JSON 格式。请严格按照以下格式返回 JSON，不要有任何解释或额外文字��\n\n{\"category\":\"top|bottom|shoes|accessory\",\"item\":\"具体衣物名称\",\"style_semantics\":[\"风格1\"],\"season_semantics\":[\"季节1\"],\"usage_semantics\":[\"场景1\"],\"color_semantics\":\"颜色\",\"description\":\"描述\"}"
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 2000
                    }

                    # 发送修正请求
                    async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
                        response = await client.post(
                            url,
                            headers={
                                "Authorization": f"Bearer {config.api_key}",
                                "Content-Type": "application/json",
                                "User-Agent": "Claude/4.0 (Claude Code)",
                                "anthropic-client": "aiwardrobe",
                                "xanthropic-client": "ClaudeCode/4.0"
                            },
                            json=correction_payload
                        )

                        if response.status_code == 200:
                            correction_data = response.json()
                            correction_content = correction_data["choices"][0]["message"].get("content", "")
                            if correction_content:
                                try:
                                    result = extract_json_from_response(correction_content)
                                except ValueError:
                                    raise ValueError(f"修正后仍无法解析 JSON: {correction_content[:100]}...")

                                return ClothesSemantics(**result)

                    # 修正也失败
                    raise ValueError(f"JSON 解析失败且无法修正: {e}")

                return ClothesSemantics(**result)

        except httpx.TimeoutException as e:
            last_error = e
            delay = INITIAL_DELAY * (2 ** attempt)
            print(f"API 超时，等待 {delay}s 后重试 (尝试 {attempt + 1}/{MAX_RETRIES})")
            await asyncio.sleep(delay)
        except httpx.ConnectError as e:
            last_error = e
            delay = INITIAL_DELAY * (2 ** attempt)
            print(f"API 连接错误，等待 {delay}s 后重试 (尝试 {attempt + 1}/{MAX_RETRIES})")
            await asyncio.sleep(delay)

    # 所有重试都失败
    raise ValueError(f"API 请求失败，已重试 {MAX_RETRIES} 次: {last_error}")
