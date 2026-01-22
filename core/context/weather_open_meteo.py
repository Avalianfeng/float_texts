"""
Open-Meteo 天气上下文实现

提供城市→经纬度→当前天气的完整流程，带两级缓存：
- 地理编码缓存（30天）
- 天气缓存（15分钟）

输出格式：例如 "12℃，多云，风1.0m/s" 或 "12℃，多云，风1.0m/s(东北)"
"""

from __future__ import annotations

import json
import os
import time
from typing import Optional, Tuple, Dict, Any

import requests

import config as _config

DEBUG = bool(getattr(_config, "DEBUG", False))
WEATHER_TIMEOUT_SECONDS = int(getattr(_config, "WEATHER_TIMEOUT_SECONDS", 10))

# 缓存目录
CONTEXT_CACHE_DIR = "data/context_cache"
GEO_CACHE_FILE = os.path.join(CONTEXT_CACHE_DIR, "geo_city.json")
WEATHER_CACHE_FILE = os.path.join(CONTEXT_CACHE_DIR, "weather_city.json")

# TTL 设置
GEO_CACHE_TTL = 30 * 24 * 3600  # 30天
WEATHER_CACHE_TTL = 15 * 60  # 15分钟

# Open-Meteo API 端点
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_API = "https://api.open-meteo.com/v1/forecast"

# 备用地理编码 API (Nominatim)
NOMINATIM_API = "https://nominatim.openstreetmap.org/search"

# 天气码映射表（WMO Weather interpretation codes）
WEATHER_CODE_MAP = {
    0: "晴",
    1: "大致晴",
    2: "少云",
    3: "多云",
    45: "雾",
    48: "雾",
    51: "毛毛雨",
    53: "毛毛雨",
    55: "毛毛雨",
    56: "冻毛毛雨",
    57: "冻毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "冻雨",
    67: "冻雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "雪粒",
    80: "阵雨",
    81: "阵雨",
    82: "强阵雨",
    85: "阵雪",
    86: "强阵雪",
    95: "雷暴",
    96: "雷暴带冰雹",
    99: "强雷暴带冰雹",
}

# 风向映射（度数 → 中文）
WIND_DIRECTION_MAP = {
    (0, 22.5): "北",
    (22.5, 67.5): "东北",
    (67.5, 112.5): "东",
    (112.5, 157.5): "东南",
    (157.5, 202.5): "南",
    (202.5, 247.5): "西南",
    (247.5, 292.5): "西",
    (292.5, 337.5): "西北",
    (337.5, 360): "北",
}


def _ensure_cache_dir() -> None:
    """确保缓存目录存在"""
    os.makedirs(CONTEXT_CACHE_DIR, exist_ok=True)


def _read_json_cache(path: str) -> Dict[str, Any]:
    """读取 JSON 缓存文件"""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        if DEBUG:
            print(f"[Weather] 读取缓存失败 {path}: {e}")
        return {}


def _write_json_cache(path: str, data: Dict[str, Any]) -> None:
    """写入 JSON 缓存文件"""
    try:
        _ensure_cache_dir()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        if DEBUG:
            print(f"[Weather] 写入缓存失败 {path}: {e}")


def _is_cache_valid(ts: float, ttl: int) -> bool:
    """检查缓存是否有效"""
    return (time.time() - ts) < ttl


def _degrees_to_direction(deg: float) -> str:
    """将度数转换为中文风向"""
    if deg is None:
        return ""
    for (start, end), direction in WIND_DIRECTION_MAP.items():
        if start <= deg < end or (start == 0 and deg == 0):
            return direction
    return ""


def _gen_city_queries(city: str) -> list[str]:
    """
    生成城市名查询变体
    
    返回: 查询候选列表，按优先级排序
    """
    city = city.strip()
    if not city:
        return []
    
    queries = [city]  # 原样
    
    # 去掉省份/空格前缀：只取最后一段
    parts = city.split()
    if len(parts) > 1:
        queries.append(parts[-1])
    
    # 去撇号："Lu'an" -> "Luan"
    if "'" in city:
        queries.append(city.replace("'", ""))
    
    # 撇号换空格："Lu'an" -> "Lu an"
    if "'" in city:
        queries.append(city.replace("'", " "))
    
    # 中文去后缀：六安市 -> 六安，xx县/区/市 去掉后缀
    if any(city.endswith(suffix) for suffix in ["市", "县", "区", "省"]):
        for suffix in ["市", "县", "区", "省"]:
            if city.endswith(suffix):
                queries.append(city[:-len(suffix)])
                break
    
    # 去重并保持顺序
    seen = set()
    result = []
    for q in queries:
        if q and q not in seen:
            seen.add(q)
            result.append(q)
    
    return result


def _select_best_result(results: list[Dict[str, Any]], original_query: str = "") -> Optional[Dict[str, Any]]:
    """
    从多个结果中选择最佳的一个
    
    优先级：
    1. country_code == "CN"（中国）
    2. 名称包含中文字符（更可能是目标城市）
    3. population 最大
    4. 第一个结果
    """
    if not results:
        return None
    
    # 优先选择中国的
    cn_results = [r for r in results if r.get("country_code", "").upper() == "CN"]
    if cn_results:
        results = cn_results
    
    # 如果原始查询包含中文，优先选择名称包含中文的结果
    if original_query and any('\u4e00' <= c <= '\u9fff' for c in original_query):
        chinese_results = [r for r in results if any('\u4e00' <= c <= '\u9fff' for c in str(r.get("name", "")))]
        if chinese_results:
            results = chinese_results
    
    # 按 population 排序（降序）
    def get_population(r: Dict[str, Any]) -> float:
        pop = r.get("population", 0)
        return float(pop) if pop else 0.0
    
    results.sort(key=get_population, reverse=True)
    
    return results[0] if results else None


def _try_open_meteo_geocoding(query: str, language: str) -> Optional[list[Dict[str, Any]]]:
    """
    尝试使用 Open-Meteo 地理编码
    
    返回: results 列表或 None（失败/超时）
    """
    try:
        if DEBUG:
            print(f"[Weather] Open-Meteo 查询: {query} (lang={language})")
        response = requests.get(
            GEOCODING_API,
            params={
                "name": query,
                "count": 10,
                "language": language,
                "format": "json",
            },
            timeout=(3, WEATHER_TIMEOUT_SECONDS),
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if DEBUG and results:
            print(f"[Weather] Open-Meteo 找到 {len(results)} 个结果")
        return results if results else None
    except requests.Timeout:
        if DEBUG:
            print(f"[Weather] Open-Meteo 请求超时: {query}")
        return None
    except requests.RequestException as e:
        if DEBUG:
            print(f"[Weather] Open-Meteo 请求失败: {e}")
        return None
    except Exception as e:
        if DEBUG:
            print(f"[Weather] Open-Meteo 处理失败: {e}")
        return None


def _try_nominatim_geocoding(query: str) -> Optional[list[Dict[str, Any]]]:
    """
    尝试使用 Nominatim 地理编码（备用）
    
    返回: results 列表或 None（失败/超时）
    """
    try:
        if DEBUG:
            print(f"[Weather] Nominatim 查询: {query}")
        response = requests.get(
            NOMINATIM_API,
            params={
                "q": query,
                "format": "json",
                "limit": 5,
                "accept-language": "zh-CN",
            },
            headers={
                "User-Agent": "float_words/1.0 (contact: none)",
            },
            timeout=(3, WEATHER_TIMEOUT_SECONDS),
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            return None
        
        # 转换 Nominatim 格式到 Open-Meteo 格式
        results = []
        for item in data:
            results.append({
                "name": item.get("display_name", "").split(",")[0],
                "latitude": float(item.get("lat", 0)),
                "longitude": float(item.get("lon", 0)),
                "country_code": item.get("address", {}).get("country_code", "").upper() if isinstance(item.get("address"), dict) else "",
                "country": item.get("address", {}).get("country", "") if isinstance(item.get("address"), dict) else "",
                "population": 0,  # Nominatim 通常不提供 population
            })
        
        if DEBUG and results:
            print(f"[Weather] Nominatim 找到 {len(results)} 个结果")
        return results if results else None
    except requests.Timeout:
        if DEBUG:
            print(f"[Weather] Nominatim 请求超时: {query}")
        return None
    except requests.RequestException as e:
        if DEBUG:
            print(f"[Weather] Nominatim 请求失败: {e}")
        return None
    except Exception as e:
        if DEBUG:
            print(f"[Weather] Nominatim 处理失败: {e}")
        return None


def resolve_city_to_latlon(city: str) -> Optional[Tuple[float, float, str]]:
    """
    解析城市名称到经纬度
    
    返回: (lat, lon, display_name) 或 None
    
    实现策略：
    1. 检查缓存
    2. 生成城市名变体
    3. 对每个变体，依次尝试 zh、en 语言
    4. 从结果中筛选最佳（优先 CN，按 population）
    5. 如果 Open-Meteo 全部失败，尝试 Nominatim 备用
    """
    if not city or not city.strip():
        return None

    city_key = city.strip()
    
    # 检查地理编码缓存
    geo_cache = _read_json_cache(GEO_CACHE_FILE)
    if city_key in geo_cache:
        cached = geo_cache[city_key]
        if _is_cache_valid(cached.get("ts", 0), GEO_CACHE_TTL):
            if DEBUG:
                print(f"[Weather] 使用地理编码缓存: {city_key}")
            return (
                cached.get("lat"),
                cached.get("lon"),
                cached.get("name", city_key),
            )

    # 生成查询变体
    queries = _gen_city_queries(city_key)
    if not queries:
        if DEBUG:
            print(f"[Weather] 无法生成查询变体: {city_key}")
        return None

    all_results = []
    has_timeout = False

    # 对每个查询变体，依次尝试 zh、en
    for query in queries:
        for language in ("zh", "en"):
            results = _try_open_meteo_geocoding(query, language)
            if results is None:
                # None 表示超时或网络错误
                has_timeout = True
                continue
            if results:
                # 有结果，添加到总列表
                all_results.extend(results)
                break  # 找到结果就跳出语言循环，继续下一个查询变体

    # 如果 Open-Meteo 全部失败（超时或无结果），尝试 Nominatim
    if not all_results:
        if DEBUG:
            print(f"[Weather] Open-Meteo 无结果，尝试 Nominatim 备用")
        for query in queries:
            results = _try_nominatim_geocoding(query)
            if results:
                all_results.extend(results)
                break  # 找到结果就停止

    # 筛选最佳结果
    best_result = _select_best_result(all_results, city_key)
    
    if not best_result:
        # 区分超时和"未找到"
        if has_timeout:
            if DEBUG:
                print(f"[Weather] 请求超时，无法获取城市信息: {city_key}")
        else:
            if DEBUG:
                print(f"[Weather] 未找到城市: {city_key}")
        return None

    lat = best_result.get("latitude")
    lon = best_result.get("longitude")
    name = best_result.get("name", city_key)
    country = best_result.get("country", "")
    country_code = best_result.get("country_code", "")

    if lat is None or lon is None:
        if DEBUG:
            print(f"[Weather] 地理编码结果无效: {best_result}")
        return None

    # 保存到缓存
    geo_cache[city_key] = {
        "ts": time.time(),
        "lat": lat,
        "lon": lon,
        "name": name,
        "country": country,
        "country_code": country_code,
    }
    _write_json_cache(GEO_CACHE_FILE, geo_cache)

    if DEBUG:
        print(f"[Weather] 地理编码成功: {city_key} -> {name} ({lat}, {lon})")
    return (lat, lon, name)


def fetch_current_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    获取当前天气
    
    返回: {
        "time": "2026-01-22T13:00",
        "temperature_c": 12.3,
        "weather_code": 3,
        "wind_speed_ms": 1.0,
        "wind_direction_deg": 45,
    } 或 None
    """
    city_key = f"{lat:.2f},{lon:.2f}"
    
    # 检查天气缓存
    weather_cache = _read_json_cache(WEATHER_CACHE_FILE)
    if city_key in weather_cache:
        cached = weather_cache[city_key]
        if _is_cache_valid(cached.get("ts", 0), WEATHER_CACHE_TTL):
            if DEBUG:
                print(f"[Weather] 使用天气缓存: {city_key}")
            return cached

    # 请求天气 API
    try:
        if DEBUG:
            print(f"[Weather] 请求天气: ({lat}, {lon})")
        response = requests.get(
            FORECAST_API,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code,wind_speed_10m,wind_direction_10m",
                "timezone": "auto",
            },
            timeout=(3, WEATHER_TIMEOUT_SECONDS),
        )
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        current_units = data.get("current_units", {})

        if not current:
            if DEBUG:
                print(f"[Weather] 天气数据为空: {data}")
            return None

        # 提取字段
        temp_c = current.get("temperature_2m")
        weather_code = current.get("weather_code")
        wind_speed_kmh = current.get("wind_speed_10m")
        wind_direction_deg = current.get("wind_direction_10m")
        time_str = current.get("time", "")

        # 转换风速单位（km/h -> m/s）
        wind_speed_ms = None
        if wind_speed_kmh is not None:
            # 检查单位
            unit = current_units.get("wind_speed_10m", "km/h")
            if unit == "km/h":
                wind_speed_ms = wind_speed_kmh / 3.6
            elif unit == "m/s":
                wind_speed_ms = wind_speed_kmh
            else:
                # 默认假设是 km/h
                wind_speed_ms = wind_speed_kmh / 3.6

        # 构建结果
        result = {
            "ts": time.time(),
            "time": time_str,
            "temperature_c": temp_c,
            "weather_code": weather_code,
            "wind_speed_ms": wind_speed_ms,
            "wind_direction_deg": wind_direction_deg,
        }

        # 保存到缓存
        weather_cache[city_key] = result
        _write_json_cache(WEATHER_CACHE_FILE, weather_cache)

        if DEBUG:
            print(f"[Weather] 天气获取成功: {result}")
        return result

    except requests.RequestException as e:
        if DEBUG:
            print(f"[Weather] 天气请求失败: {e}")
        return None
    except Exception as e:
        if DEBUG:
            print(f"[Weather] 天气处理失败: {e}")
        return None


def format_weather(info: Dict[str, Any]) -> str:
    """
    格式化天气信息为字符串
    
    格式: "12℃，多云，风1.0m/s" 或 "12℃，多云，风1.0m/s(东北)"
    """
    if not info:
        return ""

    parts = []

    # 温度
    temp = info.get("temperature_c")
    if temp is not None:
        parts.append(f"{int(round(temp))}℃")

    # 天气描述
    code = info.get("weather_code")
    if code is not None:
        desc = WEATHER_CODE_MAP.get(code, f"天气码{code}")
        parts.append(desc)

    # 风速（可选）
    wind_speed = info.get("wind_speed_ms")
    if wind_speed is not None:
        wind_str = f"风{wind_speed:.1f}m/s"
        
        # 风向（可选）
        wind_dir_deg = info.get("wind_direction_deg")
        if wind_dir_deg is not None:
            wind_dir = _degrees_to_direction(wind_dir_deg)
            if wind_dir:
                wind_str += f"({wind_dir})"
        
        parts.append(wind_str)

    return "，".join(parts) if parts else ""


def get_weather_string(city: str) -> str:
    """
    主入口：获取天气字符串
    
    输入: city (str) - 城市名称
    输出: weather (str) - 格式化的天气字符串，失败返回空字符串
    """
    if not city or not city.strip():
        return ""

    try:
        # 步骤1: 城市 → 经纬度
        geo_result = resolve_city_to_latlon(city)
        if not geo_result:
            return ""

        lat, lon, _ = geo_result

        # 步骤2: 经纬度 → 当前天气
        weather_info = fetch_current_weather(lat, lon)
        if not weather_info:
            return ""

        # 步骤3: 格式化
        return format_weather(weather_info)

    except Exception as e:
        if DEBUG:
            print(f"[Weather] get_weather_string 失败: {e}")
        return ""
