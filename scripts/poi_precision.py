#!/usr/bin/env python3
"""
长沙 CityWalk POI 精准化脚本
使用腾讯地图 WebService API 批量查询景点精确坐标

API 文档: https://lbs.qq.com/service/webService/webServiceGuide/search/webServiceSearch
"""

import json
import time
import sys

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.parse

API_KEY = "DXVBZ-HRV67-NFVXJ-P7TN4-5DFTH-VGFHG"
CITY = "长沙"

# Nominatim 是备用方案，当腾讯 key 配额耗尽时使用
USE_NOMINATIM = True

# 当前路线数据（从 changsha_citywalk_map.html 提取）
routes = {
    "r1": {
        "name": "湘江人文轴",
        "stations": [
            {"name": "橘子洲头", "lat": 28.1870, "lng": 112.9622},
            {"name": "湘江风光带北段", "lat": 28.1988, "lng": 112.9710},
            {"name": "五一广场", "lat": 28.1967, "lng": 112.9782},
            {"name": "IFS国际金融中心", "lat": 28.1971, "lng": 112.9803},
            {"name": "黄兴南路步行街", "lat": 28.1956, "lng": 112.9791},
        ]
    },
    "r2": {
        "name": "历史老街寻踪",
        "stations": [
            {"name": "天心阁", "lat": 28.1843, "lng": 112.9801},
            {"name": "坡子街", "lat": 28.1906, "lng": 112.9773},
            {"name": "太平老街", "lat": 28.1931, "lng": 112.9777},
            {"name": "文和友（海信广场）", "lat": 28.1973, "lng": 112.9778},
        ]
    },
    "r3": {
        "name": "文化山脉半日游",
        "stations": [
            {"name": "岳麓书院", "lat": 28.1802, "lng": 112.9326},
            {"name": "爱晚亭", "lat": 28.1844, "lng": 112.9317},
            {"name": "岳麓山顶", "lat": 28.1883, "lng": 112.9282},
            {"name": "湖南博物院", "lat": 28.2003, "lng": 112.9737},
        ]
    },
    "r4": {
        "name": "夜味长沙",
        "stations": [
            {"name": "火宫殿", "lat": 28.1913, "lng": 112.9772},
            {"name": "潮宗街历史街区", "lat": 28.2002, "lng": 112.9745},
            {"name": "东瓜山夜市", "lat": 28.1882, "lng": 112.9968},
            {"name": "德思勤城市广场", "lat": 28.1778, "lng": 112.9924},
        ]
    }
}


def search_nominatim(keyword, city=CITY):
    """使用 OpenStreetMap Nominatim 搜索（免费、无额度限制）"""
    import urllib.parse
    query = f"{keyword}, {city}, 中国"
    encoded_q = urllib.parse.quote(query)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded_q}&format=json&limit=5&accept-language=zh"
    headers = {
        "User-Agent": "ChangshaCityWalk/1.0 (POI precision tool)"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json()
    except Exception as e:
        return []


def search_poi(keyword, city=CITY):
    """调用腾讯地图 POI 搜索 API，返回第一个结果的精确坐标"""
    import urllib.parse
    encoded_keyword = urllib.parse.quote(keyword)
    encoded_city = urllib.parse.quote(city)
    url = (f"https://apis.map.qq.com/ws/place/v1/search"
           f"?key={API_KEY}"
           f"&keyword={encoded_keyword}"
           f"&boundary=region({encoded_city},0)"
           f"&output=json")

    try:
        if HAS_REQUESTS:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            # 检测配额耗尽 → 自动切换 Nominatim
            if data.get("status") in (-1, 1008) or "上限" in str(data.get("message", "")):
                print(f"     (腾讯配额耗尽，切换Nominatim...)")
                return search_nominatim(keyword, city)
            return data
        else:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data
    except Exception as e:
        return {"status": -1, "message": str(e)}


def calc_distance(lat1, lng1, lat2, lng2):
    """计算两点间距离（米），使用 Haversine 公式"""
    import math
    R = 6371000  # 地球半径（米）
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))


def find_best_match(poi_list, original_lat, original_lng, name, source="tencent"):
    """从多个 POI 结果中选最匹配的一个，支持腾讯/Nominatim 两种格式"""
    if not poi_list:
        return None

    candidates = []
    for poi in poi_list:
        if source == "nominatim":
            # Nominatim 格式: lat, lon, display_name, type
            p_lat = poi.get("lat")
            p_lng = poi.get("lon")
            if p_lat and p_lng:
                p_lat = float(p_lat)
                p_lng = float(p_lng)
                candidates.append({
                    "name": name,
                    "address": poi.get("display_name", ""),
                    "type": poi.get("type", ""),
                    "lat": p_lat,
                    "lng": p_lng,
                    "distance": calc_distance(original_lat, original_lng, p_lat, p_lng)
                })
        else:
            # 腾讯格式: location { lat, lng }
            loc = poi.get("location", {})
            p_lat = loc.get("lat")
            p_lng = loc.get("lng")
            if p_lat and p_lng:
                candidates.append({
                    "name": poi.get("title", ""),
                    "address": poi.get("address", ""),
                    "lat": p_lat,
                    "lng": p_lng,
                    "distance": calc_distance(original_lat, original_lng, p_lat, p_lng)
                })

    if not candidates:
        return None

    candidates.sort(key=lambda x: x["distance"])
    best = candidates[0]

    if best["distance"] > 2000:
        return {**best, "confidence": "low"}
    elif best["distance"] > 500:
        return {**best, "confidence": "medium"}
    else:
        return {**best, "confidence": "high"}


def main():
    print("=" * 70)
    print("长沙 CityWalk POI 精准化工具")
    print("=" * 70)
    print()

    all_results = {}

    for route_key, route_info in routes.items():
        print(f"\n📍 路线: {route_info['name']} ({route_key})")
        print("-" * 60)

        for station in route_info["stations"]:
            name = station["name"]
            orig_lat = station["lat"]
            orig_lng = station["lng"]

            print(f"  🔍 搜索: {name} ...", end=" ", flush=True)

            result = search_poi(name)
            time.sleep(0.3)  # 避免请求过快

            # 判断数据来源：Nominatim 返回列表，腾讯返回 dict
            if isinstance(result, list):
                pois = result
                source = "nominatim"
                best = find_best_match(pois, orig_lat, orig_lng, name, source="nominatim")
                if best:
                    delta_lat = best["lat"] - orig_lat
                    delta_lng = best["lng"] - orig_lng
                    print(f"  OSM ✅ {best['confidence']} | "
                          f"{best['lat']:.6f}, {best['lng']:.6f} "
                          f"(偏差 {best['distance']:.0f}m)")
                    if best["confidence"] == "low":
                        print(f"     ⚠️  低置信度，建议人工确认")
                    all_results[name] = {
                        "route": route_key,
                        "original": {"lat": orig_lat, "lng": orig_lng},
                        "corrected": {"lat": best["lat"], "lng": best["lng"]},
                        "delta": {"lat": delta_lat, "lng": delta_lng},
                        "distance": best["distance"],
                        "confidence": best["confidence"],
                        "matched_name": best["name"],
                        "matched_address": best["address"],
                        "source": "openstreetmap",
                    }
                else:
                    print("  OSM ⚠️  无有效结果，保留原始坐标")
                    all_results[name] = {
                        "route": route_key,
                        "original": {"lat": orig_lat, "lng": orig_lng},
                        "corrected": {"lat": orig_lat, "lng": orig_lng},
                        "confidence": "none",
                    }
                time.sleep(1.2)  # Nominatim 限速 1 req/sec
            elif result.get("status") == 0 and result.get("data"):
                pois = result["data"]
                best = find_best_match(pois, orig_lat, orig_lng, name)

                if best:
                    delta_lat = best["lat"] - orig_lat
                    delta_lng = best["lng"] - orig_lng
                    print(f"✅ {best['confidence']} | "
                          f"{best['lat']:.6f}, {best['lng']:.6f} "
                          f"(偏差 {best['distance']:.0f}m)")

                    if best["confidence"] == "low":
                        print(f"     ⚠️  低置信度，原始位置: {orig_lat}, {orig_lng} | "
                              f"建议人工确认")

                    all_results[name] = {
                        "route": route_key,
                        "original": {"lat": orig_lat, "lng": orig_lng},
                        "corrected": {"lat": best["lat"], "lng": best["lng"]},
                        "delta": {"lat": delta_lat, "lng": delta_lng},
                        "distance": best["distance"],
                        "confidence": best["confidence"],
                        "matched_name": best["name"],
                        "matched_address": best["address"],
                    }
                else:
                    print("⚠️  无有效坐标，返回原始值")
                    all_results[name] = {
                        "route": route_key,
                        "original": {"lat": orig_lat, "lng": orig_lng},
                        "corrected": {"lat": orig_lat, "lng": orig_lng},
                        "confidence": "none",
                    }
            else:
                err = result.get("message", result.get("status"))
                print(f"❌ API错误: {err}，保留原始坐标")
                all_results[name] = {
                    "route": route_key,
                    "original": {"lat": orig_lat, "lng": orig_lng},
                    "corrected": {"lat": orig_lat, "lng": orig_lng},
                    "confidence": "api_error",
                    "error": str(err),
                }

    # 输出汇总
    print("\n" + "=" * 70)
    print("📊 汇总报告")
    print("=" * 70)

    high_conf = [r for r in all_results.values() if r.get("confidence") == "high"]
    medium_conf = [r for r in all_results.values() if r.get("confidence") == "medium"]
    low_conf = [r for r in all_results.values() if r.get("confidence") == "low"]

    print(f"  ✅ 高置信度: {len(high_conf)} 个")
    print(f"  ⚠️  中置信度: {len(medium_conf)} 个")
    print(f"  ❌ 低置信度: {len(low_conf)} 个")

    print("\n📝 修正建议（可直接粘贴到 HTML）:")
    print("-" * 60)

    for route_key, route_info in routes.items():
        stations = route_info["stations"]
        lines = []
        for s in stations:
            r = all_results[s["name"]]
            conf = r.get("confidence", "")
            if conf in ("high", "medium"):
                new_lat = r["corrected"]["lat"]
                new_lng = r["corrected"]["lng"]
                d = r.get("distance", 0)
                lines.append(f"  // {s['name']} (修正 {d:.0f}m, {conf})\n"
                             f"  {new_lat:.6f}, {new_lng:.6f}")
            elif conf == "low":
                lines.append(f"  // {s['name']} ⚠️ 需人工确认")
            else:
                lines.append(f"  // {s['name']} (保留原始)")
        print(f"\n  // {route_key} - {route_info['name']}:")
        for l in lines:
            print(l)

    # 保存完整结果到 JSON
    output_path = "/Users/johnson_mac/WorkBuddy/Claw/poi_corrected.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 详细结果已保存至: {output_path}")


if __name__ == "__main__":
    main()
