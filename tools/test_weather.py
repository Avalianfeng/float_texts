"""
测试 Open-Meteo 天气功能

用法：
    python tools/test_weather.py [城市名]

示例：
    python tools/test_weather.py 上海
    python tools/test_weather.py Beijing
    python tools/test_weather.py 北京
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.context.weather_open_meteo import (
    resolve_city_to_latlon,
    fetch_current_weather,
    format_weather,
    get_weather_string,
)

def test_geocoding(city: str):
    """测试地理编码"""
    print(f"\n[测试] 地理编码: {city}")
    print("-" * 50)
    result = resolve_city_to_latlon(city)
    if result:
        lat, lon, name = result
        print(f"✅ 成功: {name}")
        print(f"   经纬度: ({lat}, {lon})")
        return lat, lon
    else:
        print("❌ 失败: 未找到城市")
        return None, None

def test_weather(lat: float, lon: float):
    """测试天气获取"""
    print(f"\n[测试] 天气获取: ({lat}, {lon})")
    print("-" * 50)
    result = fetch_current_weather(lat, lon)
    if result:
        print(f"✅ 成功:")
        print(f"   时间: {result.get('time')}")
        print(f"   温度: {result.get('temperature_c')}℃")
        print(f"   天气码: {result.get('weather_code')}")
        print(f"   风速: {result.get('wind_speed_ms')}m/s")
        print(f"   风向: {result.get('wind_direction_deg')}°")
        return result
    else:
        print("❌ 失败: 无法获取天气")
        return None

def test_format(weather_info):
    """测试格式化"""
    print(f"\n[测试] 格式化")
    print("-" * 50)
    formatted = format_weather(weather_info)
    print(f"✅ 结果: {formatted}")
    return formatted

def test_full_pipeline(city: str):
    """测试完整流程"""
    print(f"\n{'='*60}")
    print(f"[完整测试] 城市: {city}")
    print(f"{'='*60}")
    
    # 步骤1: 地理编码
    lat, lon = test_geocoding(city)
    if lat is None or lon is None:
        return
    
    # 步骤2: 天气获取
    weather_info = test_weather(lat, lon)
    if not weather_info:
        return
    
    # 步骤3: 格式化
    formatted = test_format(weather_info)
    
    # 步骤4: 使用便捷函数
    print(f"\n[测试] 便捷函数 get_weather_string('{city}')")
    print("-" * 50)
    result = get_weather_string(city)
    print(f"✅ 结果: {result}")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        city = " ".join(sys.argv[1:])
    else:
        city = "Lu'an"  # 默认城市
    
    print("=" * 60)
    print("Open-Meteo 天气功能测试")
    print("=" * 60)
    
    test_full_pipeline(city)
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
