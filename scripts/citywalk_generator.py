#!/usr/bin/env python3
"""
CityWalk HTML 生成器
使用模板引擎加速 HTML 页面生成

使用方法:
    python citywalk_generator.py --config changsha_config.json --output ../docs/
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class CityWalkGenerator:
    """CityWalk HTML 生成器"""
    
    def __init__(self, template_dir: str = "../assets/templates"):
        self.template_dir = Path(template_dir)
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载所有模板文件"""
        template_path = self.template_dir / "citywalk_v2_template.html"
        if template_path.exists():
            self.templates['main'] = template_path.read_text(encoding='utf-8')
        else:
            # 使用内置默认模板
            self.templates['main'] = self._default_template()
    
    def _default_template(self) -> str:
        """默认模板（当外部模板不存在时使用）"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{city_name}} CityWalk 路线地图 | {{visit_date}} {{holiday_name}}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Serif+SC:wght@300;400;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
:root {
  --ink: #1a1410; --warm-dark: #3d2b1f; --terracotta: #c0522a;
  --amber: #d4942a; --sand: #f5efe6; --cream: #faf7f2;
  --sea: #2a5c6e; --muted: #7a6a5a; --border: #ddd0c0;
  --route1: #c0522a; --route2: #d4942a; --route3: #2a5c6e; --route4: #7a5c8a;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Noto Sans SC', sans-serif; background: var(--cream); color: var(--ink); height: 100vh; overflow: hidden; }

/* 布局 */
.main { display: flex; height: calc(100vh - 56px); margin-top: 56px; }
#map-container { flex: 1; position: relative; }
.sidebar { width: 400px; height: 100%; overflow-y: auto; background: var(--cream); border-left: 1px solid var(--border); }

/* 顶部导航 */
.topbar { position: fixed; top: 0; left: 0; right: 0; height: 56px; background: rgba(250,247,242,0.96); backdrop-filter: blur(8px); border-bottom: 1px solid var(--border); display: flex; align-items: center; padding: 0 20px; z-index: 1000; gap: 10px; }
.topbar-title { font-family: 'Ma Shan Zheng', cursive; font-size: 20px; color: var(--terracotta); }
.route-tabs { display: flex; gap: 8px; margin-left: auto; }
.route-tab { padding: 6px 14px; border-radius: 16px; border: 1px solid var(--border); font-size: 12px; cursor: pointer; background: white; color: var(--muted); transition: all 0.2s; }
.route-tab:hover, .route-tab.active { background: var(--terracotta); color: white; border-color: var(--terracotta); }

/* 天气卡片 */
.weather-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 16px 20px; margin: 0 20px 16px; color: white; }
.weather-main { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.weather-icon { font-size: 36px; }
.weather-temp { font-size: 20px; font-weight: 600; }
.weather-desc { font-size: 13px; opacity: 0.9; margin-top: 2px; }
.weather-date { font-size: 12px; opacity: 0.8; margin-bottom: 10px; }
.weather-tips { display: flex; gap: 8px; flex-wrap: wrap; }
.tip-tag { background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 12px; font-size: 11px; }

/* 城市介绍 */
.city-intro { padding: 20px; text-align: center; border-bottom: 1px solid var(--border); }
.city-name { font-family: 'Ma Shan Zheng', cursive; font-size: 36px; color: var(--terracotta); margin-bottom: 8px; }
.city-sub { font-size: 13px; color: var(--muted); line-height: 1.6; margin-bottom: 16px; }
.city-tags { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }
.city-tag { background: var(--sand); padding: 6px 12px; border-radius: 16px; font-size: 12px; color: var(--warm-dark); }

/* 路线模块 */
.route-section { border-bottom: 1px solid var(--border); }
.route-header { padding: 16px 20px; cursor: pointer; transition: background 0.2s; }
.route-header:hover { background: rgba(192,82,42,0.05); }
.route-label { display: flex; align-items: center; gap: 10px; }
.route-dot { width: 12px; height: 12px; border-radius: 50%; }
.route-title { font-family: 'Noto Serif SC', serif; font-size: 16px; font-weight: 600; color: var(--warm-dark); }
.route-meta { font-size: 12px; color: var(--muted); margin-left: 22px; margin-top: 4px; }
.route-weather-tag { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 12px; font-size: 11px; margin-top: 8px; margin-left: 22px; }
.route-weather-tag.rain-friendly { background: #e8f5e9; color: #2e7d32; }
.route-weather-tag.rain-caution { background: #fff3e0; color: #ef6c00; }
.route-weather-tag.rain-avoid { background: #ffebee; color: #c62828; }

/* 站点列表 */
.stations { padding: 0 20px 16px; }
.station-item { display: flex; gap: 12px; padding: 12px; background: white; border-radius: 12px; margin-bottom: 10px; border: 1px solid var(--border); cursor: pointer; transition: all 0.2s; }
.station-item:hover { border-color: var(--terracotta); box-shadow: 0 2px 8px rgba(192,82,42,0.1); }
.station-num { width: 28px; height: 28px; border-radius: 50%; color: white; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; flex-shrink: 0; }
.station-name { font-weight: 600; color: var(--warm-dark); font-size: 14px; }
.station-hours { font-size: 11px; color: var(--terracotta); margin-top: 3px; font-weight: 500; }
.station-hours.closed { color: #c00; font-weight: 600; }
.station-note { font-size: 12px; color: var(--muted); margin-top: 4px; line-height: 1.5; }
.station-duration { font-size: 11px; color: var(--amber); margin-top: 6px; font-weight: 500; }
.station-booking { font-size: 11px; color: var(--sea); margin-top: 3px; font-weight: 500; }

/* 美食模块 */
.food-section { padding: 20px; border-bottom: 1px solid var(--border); }
.food-title { font-family: 'Noto Serif SC', serif; font-size: 16px; font-weight: 600; color: var(--warm-dark); margin-bottom: 16px; }
.food-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.food-item { background: white; border-radius: 12px; padding: 14px; border: 1px solid var(--border); transition: all 0.2s; }
.food-item:hover { border-color: var(--terracotta); transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.food-name { font-weight: 600; color: var(--warm-dark); font-size: 14px; margin-bottom: 4px; }
.food-loc { font-size: 12px; color: var(--muted); }

/* 城市探索模块 */
.city-info-section { padding: 20px; border-bottom: 1px solid var(--border); }
.info-tabs { display: flex; gap: 8px; margin-bottom: 16px; overflow-x: auto; scrollbar-width: none; }
.info-tabs::-webkit-scrollbar { display: none; }
.info-tab { padding: 6px 14px; border-radius: 16px; border: 1px solid var(--border); font-size: 12px; cursor: pointer; white-space: nowrap; background: white; color: var(--muted); transition: all 0.2s; }
.info-tab:hover { border-color: var(--terracotta); color: var(--terracotta); }
.info-tab.active { background: var(--terracotta); color: white; border-color: var(--terracotta); }
.info-content { display: none; }
.info-content.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.info-card { background: white; border-radius: 12px; padding: 16px; border: 1px solid var(--border); margin-bottom: 12px; }
.info-card h4 { font-family: 'Noto Serif SC', serif; font-size: 14px; color: var(--warm-dark); margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
.info-card p { font-size: 13px; color: var(--muted); line-height: 1.8; }
.info-card ul { font-size: 13px; color: var(--muted); line-height: 1.8; padding-left: 16px; }
.info-card li { margin-bottom: 6px; }
.highlight-box { background: linear-gradient(135deg, var(--sand) 0%, #f0ece4 100%); border-left: 3px solid var(--terracotta); padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 12px 0; }
.highlight-box p { font-size: 12px; color: var(--warm-dark); line-height: 1.7; }
.story-grid { display: grid; gap: 12px; }
.story-card { background: white; border-radius: 12px; padding: 16px; border: 1px solid var(--border); }
.story-card h5 { font-size: 13px; color: var(--terracotta); margin-bottom: 8px; font-weight: 600; }
.story-card p { font-size: 12px; color: var(--muted); line-height: 1.7; }
.landmark-list { display: grid; gap: 10px; }
.landmark-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: var(--sand); border-radius: 8px; }
.landmark-item strong { font-size: 13px; color: var(--warm-dark); }
.landmark-item span { font-size: 11px; color: var(--muted); }

/* 出行贴士 */
.tips-section { padding: 20px; background: linear-gradient(135deg, var(--sand) 0%, #f0ece4 100%); }
.tips-title { font-family: 'Noto Serif SC', serif; font-size: 16px; font-weight: 600; color: var(--warm-dark); margin-bottom: 12px; }
.tip-item { font-size: 13px; color: var(--muted); line-height: 1.8; margin-bottom: 8px; padding-left: 16px; position: relative; }
.tip-item::before { content: "•"; color: var(--terracotta); position: absolute; left: 0; font-weight: bold; }

/* 五一特别提示 */
.holiday-alert { background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); border-radius: 12px; padding: 16px 20px; margin: 0 20px 16px; border-left: 4px solid var(--amber); }
.holiday-alert-title { font-weight: 600; color: #e65100; margin-bottom: 10px; font-size: 14px; }
.holiday-alert ul { font-size: 12px; color: var(--muted); line-height: 1.8; padding-left: 16px; }
.holiday-alert li { margin-bottom: 6px; }

/* 响应式 */
@media (max-width: 768px) {
  .main { flex-direction: column; }
  #map-container { height: 50vh; }
  .sidebar { width: 100%; height: 50vh; border-left: none; border-top: 1px solid var(--border); }
  .topbar-title { font-size: 16px; }
  .food-grid { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<!-- 顶部导航 -->
<div class="topbar">
  <div class="topbar-title">🚶 {{city_name}} CityWalk</div>
  <div class="route-tabs">
    {{route_tabs}}
  </div>
</div>

<div class="main">
  <!-- 地图 -->
  <div id="map-container"></div>
  
  <!-- 侧边栏 -->
  <div class="sidebar">
    {{weather_card}}
    {{city_intro}}
    {{holiday_alert}}
    {{route_sections}}
    {{food_section}}
    {{my_food_list}}
    {{tips_section}}
    {{city_explore}}
  </div>
</div>

<script>
// 路线数据
const routes = {{routes_json}};

// 初始化地图
const map = L.map('map-container').setView([{{center_lat}}, {{center_lng}}], {{zoom}});
L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
  subdomains: '1234', attribution: '© 高德地图'
}).addTo(map);

// 创建编号标记
function createNumberedMarker(lat, lng, number, color, title, note) {
  const canvas = document.createElement('canvas');
  canvas.width = 32; canvas.height = 40;
  const ctx = canvas.getContext('2d');
  
  // 倒水滴形状
  ctx.beginPath();
  ctx.moveTo(16, 40);
  ctx.bezierCurveTo(0, 20, 0, 0, 16, 0);
  ctx.bezierCurveTo(32, 0, 32, 20, 16, 40);
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();
  
  // 白色中心圆
  ctx.beginPath();
  ctx.arc(16, 14, 10, 0, Math.PI * 2);
  ctx.fillStyle = '#fff';
  ctx.fill();
  
  // 编号文字
  ctx.fillStyle = color;
  ctx.font = 'bold 14px sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(number, 16, 14);
  
  return L.marker([lat, lng], {
    icon: L.divIcon({
      className: 'custom-marker',
      html: `<img src="${canvas.toDataURL()}" style="width:32px;height:40px;">`,
      iconSize: [32, 40],
      iconAnchor: [16, 40]
    })
  }).addTo(map).bindPopup(`<b>${title}</b><br>${note}`);
}

// 绘制路线
const routeLayers = {};
const markerLayers = {};

Object.keys(routes).forEach(routeId => {
  const route = routes[routeId];
  const color = route.color;
  
  // 绘制折线
  const latlngs = route.stations.map(s => [s.lat, s.lng]);
  routeLayers[routeId] = L.polyline(latlngs, { color: color, weight: 4, opacity: 0.8 }).addTo(map);
  
  // 创建标记
  markerLayers[routeId] = route.stations.map((s, i) => 
    createNumberedMarker(s.lat, s.lng, i + 1, color, s.name, s.note)
  );
});

// 切换路线显示
let currentRoute = Object.keys(routes)[0];

function switchRoute(routeId) {
  currentRoute = routeId;
  
  // 更新标签样式
  document.querySelectorAll('.route-tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.route === routeId);
  });
  
  // 显示/隐藏路线
  Object.keys(routeLayers).forEach(rid => {
    if (rid === routeId) {
      routeLayers[rid].addTo(map);
      markerLayers[rid].forEach(m => m.addTo(map));
    } else {
      routeLayers[rid].remove();
      markerLayers[rid].forEach(m => m.remove());
    }
  });
  
  // 调整地图视野
  const route = routes[routeId];
  const bounds = L.latLngBounds(route.stations.map(s => [s.lat, s.lng]));
  map.fitBounds(bounds, { padding: [50, 50] });
}

// 展开/收起路线
def toggleRoute(routeId) {
  const el = document.getElementById('stations-' + routeId);
  el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

// 聚焦站点
def focusStation(routeId, index) {
  switchRoute(routeId);
  const station = routes[routeId].stations[index];
  map.setView([station.lat, station.lng], 16);
  markerLayers[routeId][index].openPopup();
}

// 切换城市探索标签
def switchInfoTab(tab, contentId) {
  document.querySelectorAll('.info-tab').forEach(t => t.classList.remove('active'));
  tab.classList.add('active');
  document.querySelectorAll('.info-content').forEach(c => c.classList.remove('active'));
  document.getElementById('info-' + contentId).classList.add('active');
}

// Tab 点击事件
document.querySelectorAll('.route-tab').forEach(tab => {
  tab.addEventListener('click', () => switchRoute(tab.dataset.route));
});

// 初始化显示第一条路线
switchRoute(currentRoute);
</script>
</body>
</html>'''
    
    def generate(self, config: Dict[str, Any]) -> str:
        """
        根据配置生成 HTML
        
        Args:
            config: 城市配置字典
        
        Returns:
            生成的 HTML 字符串
        """
        html = self.templates['main']
        
        # 基础变量替换
        html = self._replace_basic_vars(html, config)
        
        # 生成各个模块
        html = html.replace('{{weather_card}}', self._gen_weather_card(config.get('weather', {})))
        html = html.replace('{{city_intro}}', self._gen_city_intro(config.get('city', {})))
        html = html.replace('{{holiday_alert}}', self._gen_holiday_alert(config.get('holiday', None)))
        html = html.replace('{{route_tabs}}', self._gen_route_tabs(config.get('routes', [])))
        html = html.replace('{{route_sections}}', self._gen_route_sections(config.get('routes', [])))
        html = html.replace('{{food_section}}', self._gen_food_section(config.get('foods', [])))
        html = html.replace('{{my_food_list}}', self._gen_my_food_list(config.get('my_foods', [])))
        html = html.replace('{{tips_section}}', self._gen_tips_section(config.get('tips', {})))
        html = html.replace('{{city_explore}}', self._gen_city_explore(config.get('explore', {})))
        
        # 生成路线 JSON
        html = html.replace('{{routes_json}}', json.dumps(self._routes_to_json(config.get('routes', [])), ensure_ascii=False))
        
        return html
    
    def _replace_basic_vars(self, html: str, config: Dict) -> str:
        """替换基础变量"""
        replacements = {
            '{{city_name}}': config.get('city', {}).get('name', '城市'),
            '{{visit_date}}': config.get('visit_date', '2026-05-01'),
            '{{holiday_name}}': config.get('holiday_name', ''),
            '{{center_lat}}': str(config.get('center', [28.2, 112.9])[0]),
            '{{center_lng}}': str(config.get('center', [28.2, 112.9])[1]),
            '{{zoom}}': str(config.get('zoom', 13)),
        }
        for key, value in replacements.items():
            html = html.replace(key, value)
        return html
    
    def _gen_weather_card(self, weather: Dict) -> str:
        """生成天气卡片"""
        if not weather:
            return ''
        
        tips_html = ''.join([f'<span class="tip-tag">{tip}</span>' for tip in weather.get('tips', [])])
        
        return f'''
<div class="weather-card">
  <div class="weather-main">
    <span class="weather-icon">{weather.get('icon', '☀️')}</span>
    <div class="weather-info">
      <div class="weather-temp">{weather.get('temp', '22°C / 15°C')}</div>
      <div class="weather-desc">{weather.get('desc', '多云转晴 · 适宜出行')}</div>
    </div>
  </div>
  <div class="weather-date">📅 {weather.get('date', '2026-05-01')} {weather.get('date_note', '')}</div>
  <div class="weather-tips">{tips_html}</div>
</div>'''
    
    def _gen_city_intro(self, city: Dict) -> str:
        """生成城市介绍"""
        tags_html = ''.join([f'<span class="city-tag">{tag}</span>' for tag in city.get('tags', [])])
        
        return f'''
<div class="city-intro">
  <div class="city-name">{city.get('name', '城市')}</div>
  <div class="city-sub">{city.get('subtitle', '')}<br>{city.get('description', '')}</div>
  <div class="city-tags">{tags_html}</div>
</div>'''
    
    def _gen_holiday_alert(self, holiday: Dict) -> str:
        """生成节假日特别提示"""
        if not holiday:
            return ''
        
        tips_html = ''.join([f'<li>{tip}</li>' for tip in holiday.get('tips', [])])
        
        return f'''
<div class="holiday-alert">
  <div class="holiday-alert-title">🎉 {holiday.get('name', '节假日')}特别提示</div>
  <ul>{tips_html}</ul>
</div>'''
    
    def _gen_route_tabs(self, routes: List[Dict]) -> str:
        """生成路线切换标签"""
        tabs = []
        for i, route in enumerate(routes):
            active = 'active' if i == 0 else ''
            tabs.append(f'<div class="route-tab {active}" data-route="r{i+1}">{route.get("short_name", route["name"])}</div>')
        return '\n    '.join(tabs)
    
    def _gen_route_sections(self, routes: List[Dict]) -> str:
        """生成路线列表"""
        sections = []
        for i, route in enumerate(routes):
            route_id = f"r{i+1}"
            color_var = f"var(--route{i+1})"
            display = 'block' if i == 0 else 'none'
            
            # 天气适配标签
            weather_tag = ''
            if route.get('weather_tag'):
                weather_tag = f'<div class="route-weather-tag {route["weather_tag"]["class"]}">{route["weather_tag"]["text"]}</div>'
            
            # 站点列表
            stations_html = []
            for j, station in enumerate(route.get('stations', [])):
                hours_class = 'closed' if '闭馆' in station.get('hours', '') else ''
                booking_html = f'<div class="station-booking">📱 {station["booking"]}</div>' if station.get('booking') else ''
                
                stations_html.append(f'''
        <div class="station-item" data-route="{route_id}" data-index="{j}" onclick="focusStation('{route_id}', {j})">
          <div class="station-num" style="background:{color_var}">{j+1}</div>
          <div class="station-info">
            <div class="station-name">{station['name']}</div>
            <div class="station-hours {hours_class}">🕐 {station.get('hours', '全天开放')}</div>
            {booking_html}
            <div class="station-note">{station.get('note', '')}</div>
            <div class="station-duration">⏱️ {station.get('duration', '建议 1 小时')}</div>
          </div>
        </div>''')
            
            sections.append(f'''
    <div class="route-section" id="route-{route_id}">
      <div class="route-header" onclick="toggleRoute('{route_id}')">
        <div class="route-label">
          <div class="route-dot" style="background:{color_var}"></div>
          <div class="route-title">{route['name']}</div>
        </div>
        <div class="route-meta">{route.get('meta', '')}</div>
        {weather_tag}
      </div>
      <div class="stations" id="stations-{route_id}" style="display:{display}">
        {''.join(stations_html)}
      </div>
    </div>''')
        
        return '\n'.join(sections)
    
    def _gen_food_section(self, foods: List[Dict]) -> str:
        """生成美食速查"""
        if not foods:
            return ''
        
        food_items = ''.join([f'''
        <div class="food-item">
          <div class="food-name">{food['name']}</div>
          <div class="food-loc">{food['loc']}</div>
        </div>''' for food in foods])
        
        return f'''
    <div class="food-section">
      <div class="food-title">🍜 必吃美食速查</div>
      <div class="food-grid">
        {food_items}
      </div>
    </div>'''
    
    def _gen_my_food_list(self, foods: List[Dict]) -> str:
        """生成我的美食清单"""
        if not foods:
            return ''
        
        food_items = ''.join([f'''
        <div class="food-item">
          <div class="food-name">{food['name']}</div>
          <div class="food-loc">{food['loc']}</div>
        </div>''' for food in foods])
        
        return f'''
    <div class="food-section" style="background: linear-gradient(135deg, #fff8f0 0%, #fff0e6 100%);">
      <div class="food-title">⭐ 我的美食清单</div>
      <div class="food-grid">
        {food_items}
      </div>
    </div>'''
    
    def _gen_tips_section(self, tips: Dict) -> str:
        """生成出行贴士"""
        if not tips:
            return ''
        
        tip_items = ''.join([f'<div class="tip-item">{tip}</div>' for tip in tips.get('items', [])])
        
        return f'''
    <div class="tips-section">
      <div class="tips-title">📌 出行贴士</div>
      {tip_items}
    </div>'''
    
    def _gen_city_explore(self, explore: Dict) -> str:
        """生成城市探索模块"""
        if not explore:
            return ''
        
        # 四个标签页
        tabs = [
            ('history', '📜 人文历史', explore.get('history', [])),
            ('admin', '🏛️ 行政划分', explore.get('admin', [])),
            ('landmarks', '🏯 名胜古迹', explore.get('landmarks', [])),
            ('stories', '🌟 都市故事', explore.get('stories', [])),
        ]
        
        # 生成标签按钮
        tab_buttons = '\n        '.join([
            f'<div class="info-tab {"active" if i==0 else ""}" onclick="switchInfoTab(this, \'{tab_id}\')">{tab_name}</div>'
            for i, (tab_id, tab_name, _) in enumerate(tabs)
        ])
        
        # 生成内容区域
        contents = []
        for i, (tab_id, tab_name, cards) in enumerate(tabs):
            cards_html = self._gen_info_cards(cards, tab_id)
            contents.append(f'''
      <div class="info-content {'active' if i==0 else ''}" id="info-{tab_id}">
        {cards_html}
      </div>''')
        
        return f'''
    <div class="city-info-section">
      <div class="info-tabs">
        {tab_buttons}
      </div>
      {''.join(contents)}
    </div>'''
    
    def _gen_info_cards(self, cards: List[Dict], tab_type: str) -> str:
        """生成信息卡片"""
        if not cards:
            return ''
        
        html_cards = []
        for card in cards:
            if tab_type == 'stories':
                # 都市故事使用 story-card 样式
                html_cards.append(f'''
        <div class="story-card">
          <h5>{card.get('title', '')}</h5>
          <p>{card.get('content', '')}</p>
        </div>''')
            elif tab_type == 'landmarks' and card.get('type') == 'list':
                # 名胜古迹列表
                items = ''.join([f'''
            <div class="landmark-item">
              <strong>{item['name']}</strong>
              <span>{item['desc']}</span>
            </div>''' for item in card.get('items', [])])
                html_cards.append(f'''
        <div class="info-card">
          <h4>{card.get('title', '')}</h4>
          <div class="landmark-list">
            {items}
          </div>
        </div>''')
            else:
                # 普通卡片
                highlight = ''
                if card.get('highlight'):
                    highlight = f'''
          <div class="highlight-box">
            <p>{card['highlight']}</p>
          </div>'''
                
                content = card.get('content', '')
                if isinstance(content, list):
                    content = '<ul>' + ''.join([f'<li>{item}</li>' for item in content]) + '</ul>'
                else:
                    content = f'<p>{content}</p>'
                
                html_cards.append(f'''
        <div class="info-card">
          <h4>{card.get('title', '')}</h4>
          {content}
          {highlight}
        </div>''')
        
        if tab_type == 'stories':
            return f'<div class="story-grid">{ "".join(html_cards) }</div>'
        return '\n'.join(html_cards)
    
    def _routes_to_json(self, routes: List[Dict]) -> Dict:
        """将路线数据转换为 JSON 格式（供 JS 使用）"""
        result = {}
        colors = ['#c0522a', '#d4942a', '#2a5c6e', '#7a5c8a', '#5c8a6e']
        
        for i, route in enumerate(routes):
            route_id = f"r{i+1}"
            result[route_id] = {
                'name': route['name'],
                'color': colors[i % len(colors)],
                'stations': [
                    {
                        'name': s['name'],
                        'lat': s['lat'],
                        'lng': s['lng'],
                        'note': s.get('note', '')
                    }
                    for s in route.get('stations', [])
                ]
            }
        
        return result


def main():
    parser = argparse.ArgumentParser(description='CityWalk HTML 生成器')
    parser.add_argument('--config', '-c', required=True, help='配置文件路径 (JSON)')
    parser.add_argument('--output', '-o', default='./', help='输出目录')
    parser.add_argument('--template-dir', '-t', default='../assets/templates', help='模板目录')
    args = parser.parse_args()
    
    # 加载配置
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"错误: 配置文件不存在: {config_path}")
        return 1
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 生成 HTML
    generator = CityWalkGenerator(template_dir=args.template_dir)
    html = generator.generate(config)
    
    # 保存文件
    city_pinyin = config.get('city', {}).get('pinyin', 'city')
    output_path = Path(args.output) / f"{city_pinyin}-citywalk-v2.html"
    output_path.write_text(html, encoding='utf-8')
    
    print(f"✅ 生成成功: {output_path}")
    print(f"   城市: {config.get('city', {}).get('name', 'Unknown')}")
    print(f"   路线数: {len(config.get('routes', []))}")
    print(f"   文件大小: {len(html) / 1024:.1f} KB")
    
    return 0


if __name__ == '__main__':
    exit(main())
