---
name: citywalk-planner
description: >
  城市CityWalk路线规划技能。当用户要求为某个城市/目的地制作CityWalk、城市漫步、一日游、
  旅游攻略路线、步行路线规划时使用。支持生成带交互地图的HTML页面和纯文字清单版本。
  支持天气联动、景点开放时间查询、雨天备选路线推荐。
  Keywords: citywalk, 城市漫步, 旅游路线, 一日游攻略, 步行路线, travel plan, itinerary, 天气, 开放时间。
---

# CityWalk 路线规划

为任意城市生成结构化 CityWalk 路线方案，输出两个 HTML 文件：
- **地图版**（`{city}_citywalk_map.html`）：交互地图 + 站点面板 + 天气模块 + 开放时间
- **文字版**（`{city}_citywalk_text.html`）：可打印的时长清单 + 天气提示

## 新增功能（v2.0）

### 🌤️ 天气联动
- 询问用户**目标访问日期**，查询当日天气预报
- 根据天气自动推荐路线（雨天推荐室内景点路线）
- 在页面顶部显示天气卡片（温度、天气状况、穿衣建议）

### 🕐 景点开放时间
- 搜集每个景点的开放时间、闭馆日、门票信息
- 在站点卡片上标注开放时间
- 标记"周一闭馆"、"需预约"等特殊提示

### 🌧️ 雨天备选
- 为每条户外路线提供室内备选方案
- 天气不佳时自动切换推荐

## 工作流

### Phase 0 — 用户意图确认

当用户请求 CityWalk 规划时，**必须首先询问以下信息**：

#### 必填信息
1. **目标城市** — 如未明确，请用户确认
2. **访问日期** — 格式：`YYYY-MM-DD`，用于查询天气预报
   - 示例："您计划什么时候去？（如：2026-05-01）"

#### 可选信息（用户未主动提供时不追问）
- 出行天数（半天/一天/两天）
- 兴趣偏好（美食/历史/摄影/亲子/文艺）
- 体力状况（轻松/中等/挑战）

#### 天气查询
获取访问日期后，使用 WebSearch 查询：
```
"{城市} {日期} 天气预报"
```

提取信息：
- 天气状况（晴/多云/雨/阴）
- 温度范围（最高/最低）
- 降雨概率
- 穿衣建议

**天气影响路线推荐**：
| 天气 | 推荐路线类型 | 避开的路线 |
|------|-------------|-----------|
| 晴天/多云 | 所有路线均可 | 无 |
| 小雨 | 室内为主路线 | 登山、长时间户外 |
| 大雨/暴雨 | 纯室内路线（博物馆、商场、室内景点） | 所有户外路线 |
| 阴天 | 人文历史路线 | 观景类路线 |

---

### Phase 0.5 — 高德 API Key（可选但推荐）

**为什么需要**：默认使用估算坐标，偏差约 200-500 米。若需精确标点，使用高德 POI API 获取 GCJ-02 精确坐标。

**获取方式**：
1. 访问 [高德开放平台](https://lbs.amap.com/) 注册账号
2. 控制台 → 应用管理 → 创建新应用 → 添加 Key（服务平台选"Web服务"）
3. 复制 Key 备用

**批量查询脚本**（替换 `YOUR_KEY` 和 POI_ID 列表）：
```bash
#!/bin/bash
KEY="YOUR_KEY"
POIS=("B0I2B0I2B0" "B0J6MOQBTG" "B0FFKJH1K5")  # 从高德地图 URL 提取

for poi in "${POIS[@]}"; do
  echo "=== $poi ==="
  curl -s "https://restapi.amap.com/v3/place/detail?key=$KEY&id=$poi&output=json" | \
    python3 -c "import sys,json; d=json.load(sys.stdin); p=d['pois'][0]; print(f\"{p['name']}: {p['location']}\")"
done
```

**POI_ID 获取**：在高德地图搜索目标地点，URL 中 `&id=XXXXX` 的 XXXXX 即为 POI_ID。

**坐标说明**：高德返回的 `location` 字段为 GCJ-02 坐标（火星坐标系），直接用于高德瓦片地图，无需转换。

### Phase 0.5 — 坐标校验规则（强制）

**⚠️ 坐标来源优先级**：
1. **高德 POI API** → 直接获得 GCJ-02，无需转换 ✅ 最佳
2. **百度/腾讯地图 API** → 获得 BD-09/GCJ-02，需转换
3. **估算坐标** → 默认为 WGS-84，**必须转换**为 GCJ-02

**校验清单**：
- [ ] 所有坐标是否在城市合理范围内？（长沙：lat 28.0-28.3, lng 112.8-113.1）
- [ ] 标记是否落入水中/明显错误位置？（目测检查）
- [ ] 相邻站点距离是否合理？（步行 < 3km，打车 > 3km）

**WGS-84 → GCJ-02 转换函数**（必须内嵌到 HTML）：
```javascript
function wgs84ToGcj02(lat, lng) {
  const a = 6378245.0, ee = 0.00669342162296594323;
  function tLat(x, y) { return -100 + 2*x + 3*y + 0.2*y*y + 0.1*x*y + 0.2*Math.sqrt(Math.abs(x)); }
  function tLng(x, y) { return 300 + x + 2*y + 0.1*x*x + 0.1*x*y + 0.1*Math.sqrt(Math.abs(x)); }
  let dLat = tLat(lng - 105, lat - 35), dLng = tLng(lng - 105, lat - 35);
  const radLat = lat / 180 * Math.PI, magic = 1 - ee * Math.sin(radLat) ** 2;
  const sqrtMagic = Math.sqrt(magic);
  dLat = (dLat * 180) / ((a * (1 - ee)) / (magic * sqrtMagic) * Math.PI);
  dLng = (dLng * 180) / (a / sqrtMagic * Math.cos(radLat) * Math.PI);
  return { lat: lat + dLat, lng: lng + dLng };
}
```

**使用方式**：
```javascript
// 估算坐标（WGS-84）→ 转换后直接用于高德瓦片
const gcj = wgs84ToGcj02(28.1857, 112.9445);
L.marker([gcj.lat, gcj.lng]).addTo(map);
```

### Phase 1 — 情报搜集

搜索目标城市的旅游景点、美食老字号、特色街区、交通方式、**开放时间**。

**搜索策略**（用 online-search skill）：
```
"{城市}CityWalk 旅游攻略 景点 美食" --cnt=20
"{城市} 美食 老字号 小吃 街" --cnt=15
"{城市} {核心景点} {核心景点} 坐标 位置" --cnt=15
"{城市} {核心景点} 开放时间 门票 预约" --cnt=15
```

每个城市搜索 4-6 轮，覆盖：景点分布、美食地图、历史文化、交通贴士、**开放时间**。

**信息提取要点**：
- 景点名称、地址、门票、建议时长
- **开放时间**（平日/周末/节假日是否不同）
- **闭馆日**（周一闭馆？周二闭馆？）
- **预约要求**（是否需要提前预约？）
- 老字号店铺名称、特色菜品、人均价格
- 美食街/夜市位置
- 景点间距离（判断是否可步行）
- 特色体验（日出点、夜景、演出时间等）

**开放时间标注格式**：
```
🕐 开放时间: 08:30-17:00（周一闭馆）
🕐 开放时间: 09:00-21:00（全年无休）
🕐 开放时间: 需提前预约，限流参观
```

### Phase 2 — 路线设计

基于搜集信息、**天气预报**和**开放时间**，设计 3-5 条主题路线。

**路线分类建议**（按城市特点灵活调整）：
| 类型 | 主题 | 示例 | 天气适配 |
|------|------|------|----------|
| 历史文化 | 老城区/古建筑/博物馆 | 古城寻踪、老城寻根 | ✅ 雨天友好 |
| 美食探索 | 老字号/小吃街/夜宵 | 吃货征途、舌尖上的XX | ✅ 雨天友好 |
| 自然风光 | 山/湖/海/公园 | 山水人文、海风诗行 | ⚠️ 雨天备选 |
| 新城/艺术 | 新区/艺术区/文创 | 新城艺境 | ✅ 雨天友好 |
| 郊外/海岛 | 需自驾的景点群 | 南澳逐浪、水乡古韵 | ❌ 雨天避开 |

**路线排序原则**：
1. **根据天气筛选**：雨天优先室内路线（博物馆、商场、室内景点）
2. **根据开放时间排序**：早开的景点排前面，避开闭馆日
3. 地理位置连贯，不走回头路
4. 早→晚的时间线合理（早餐→午餐→晚餐→宵夜）
5. 登山/户外路线安排在清晨（晴天时）
6. 需自驾的路线单独一条
7. 全程免费的路线优先（性价比高）

**每站标注**：站点名 + 建议时长 + 开放时间 + 一句话备注

**雨天备选方案**：
为每条户外路线设计对应的室内备选路线：
- 原路线：岳麓山 → 橘子洲 → 湘江风光带（户外）
- 雨天备选：湖南省博物馆 → 谢子龙影像馆 → IFS国金中心（室内）

### Phase 3 — 生成地图版 HTML

将路线数据写入 `{city}_citywalk_map.html`。

**新增模块（v2.0）**：
1. **天气卡片** — 页面顶部显示访问日期天气
2. **开放时间标注** — 每个站点显示开放时间和闭馆提示
3. **雨天备选提示** — 天气不佳时显示室内备选路线

**技术要点**：
- 使用**腾讯地图 JavaScript API GL**（`https://map.qq.com/api/gljs?v=1.exp&key=YOUR_KEY`）
- 坐标系：腾讯地图使用 GCJ-02（火星坐标系），直接使用 GCJ-02 坐标，**无需 WGS-84 转换**
- 使用 `TMap.MultiMarker` 渲染编号标记点
- 使用 `TMap.MultiPolyline` 渲染路线折线（每条路线不同颜色）
- 点击标记弹出自定义 InfoWindow（`TMap.InfoWindow`）或侧边面板联动
- 右侧 sticky 站点面板，点击标记高亮；顶部 sticky 导航条，切换路线
- 初始化：`new TMap.Map('container', { center: new TMap.LatLng(lat, lng), zoom: 14 })`

**腾讯地图 GL 核心 API 速查**：
```javascript
// 引入
<script src="https://map.qq.com/api/gljs?v=1.exp&key=YOUR_KEY"></script>

// 初始化地图
var map = new TMap.Map('container', {
  center: new TMap.LatLng(28.1941, 112.9836),  // 长沙市中心
  zoom: 13
});

// 多标记（编号图标）
var markerLayer = new TMap.MultiMarker({
  id: 'route1-markers', map: map,
  styles: {
    'num': new TMap.MarkerStyle({ width: 32, height: 32, anchor: {x:16,y:32},
      src: 'data:image/svg+xml,...' })
  },
  geometries: [
    { id: 'p1', styleId: 'num', position: new TMap.LatLng(lat, lng),
      properties: { name: '站点名', note: '备注' } }
  ]
});

// 折线
var polylineLayer = new TMap.MultiPolyline({
  id: 'route1-line', map: map,
  styles: { 'line': { color: '#c0522a', width: 4, borderWidth: 2, borderColor: '#fff' } },
  geometries: [{
    id: 'r1', styleId: 'line',
    paths: [ new TMap.LatLng(lat1, lng1), new TMap.LatLng(lat2, lng2) ]
  }]
});

// 标记点击事件
markerLayer.on('click', function(e) {
  var geo = e.geometry;
  // 弹出侧边面板或 InfoWindow
});
```

**视觉风格**：
- 暖色调（cream/terracotta/amber），参考汕头版配色
- 字体：Ma Shan Zheng（标题）+ Noto Serif SC（正文）+ Noto Sans SC（UI）
- 响应式：桌面端双栏，移动端单栏

**Key 说明**：腾讯地图 API 需要 Key（在 `https://lbs.qq.com/` 申请）。生成时在 script src 中使用占位符 `YOUR_KEY`，并在页面顶部注释说明如何申请替换。

---

### HTML 模板增强（v2.0）

#### 1. 天气卡片模块

在 `.city-intro` 后添加天气卡片：

```html
<!-- 天气卡片 -->
<div class="weather-card">
  <div class="weather-main">
    <span class="weather-icon">☀️</span>
    <div class="weather-info">
      <div class="weather-temp">22°C / 15°C</div>
      <div class="weather-desc">多云转晴 · 适宜出行</div>
    </div>
  </div>
  <div class="weather-date">📅 2026-05-01 访问</div>
  <div class="weather-tips">
    <span class="tip-tag">👕 建议长袖</span>
    <span class="tip-tag">☂️ 带伞备用</span>
    <span class="tip-tag">🧴 注意防晒</span>
  </div>
</div>
```

CSS：
```css
.weather-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 16px 20px;
  margin: 0 20px 16px;
  color: white;
}
.weather-main {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.weather-icon { font-size: 36px; }
.weather-temp { font-size: 20px; font-weight: 600; }
.weather-desc { font-size: 13px; opacity: 0.9; margin-top: 2px; }
.weather-date { font-size: 12px; opacity: 0.8; margin-bottom: 10px; }
.weather-tips { display: flex; gap: 8px; flex-wrap: wrap; }
.tip-tag {
  background: rgba(255,255,255,0.2);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
}
```

#### 2. 开放时间标注

在站点信息中添加开放时间：

```html
<div class="station-info">
  <div class="station-name">湖南省博物馆</div>
  <div class="station-hours">🕐 09:00-17:00（周一闭馆）</div>
  <div class="station-note">马王堆汉墓文物，需提前预约</div>
  <div class="station-duration">⏱️ 建议 2-3 小时</div>
</div>
```

CSS：
```css
.station-hours {
  font-size: 11px;
  color: var(--terracotta);
  margin-top: 3px;
  font-weight: 500;
}
.station-closed {
  color: #c00;
  font-weight: 600;
}
```

#### 3. 雨天备选提示

在路线头部添加天气适配提示：

```html
<div class="route-header">
  <div class="route-label">
    <div class="route-dot" style="background:var(--route1)"></div>
    <div class="route-title">① 湘江人文轴</div>
  </div>
  <div class="route-meta">全程约 6km · 建议 4-5 小时 · 4个站点</div>
  <div class="route-weather-tag rain-friendly">
    🌧️ 雨天友好 · 80% 室内景点
  </div>
</div>
```

CSS：
```css
.route-weather-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  margin-top: 8px;
  margin-left: 22px;
}
.route-weather-tag.rain-friendly {
  background: #e8f5e9;
  color: #2e7d32;
}
.route-weather-tag.rain-caution {
  background: #fff3e0;
  color: #ef6c00;
}
.route-weather-tag.rain-avoid {
  background: #ffebee;
  color: #c62828;
}
```

#### 4. 雨天备选路线面板

当预报有雨时，在侧边栏顶部显示：

```html
<div class="rain-alert">
  <div class="rain-alert-title">🌧️ 雨天备选方案</div>
  <p>预报显示访问日有雨，推荐以下室内路线：</p>
  <div class="rain-routes">
    <div class="rain-route-item active">博物馆之旅</div>
    <div class="rain-route-item">商场美食线</div>
    <div class="rain-route-item">室内文化游</div>
  </div>
</div>
```

CSS：
```css
.rain-alert {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-radius: 12px;
  padding: 16px 20px;
  margin: 0 20px 16px;
  border-left: 4px solid #2196f3;
}
.rain-alert-title {
  font-weight: 600;
  color: #1565c0;
  margin-bottom: 8px;
}
.rain-alert p {
  font-size: 12px;
  color: #424242;
  margin-bottom: 10px;
}
.rain-routes { display: flex; gap: 8px; flex-wrap: wrap; }
.rain-route-item {
  background: white;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
  border: 1px solid #90caf9;
}
.rain-route-item.active {
  background: #2196f3;
  color: white;
  border-color: #2196f3;
}
```

### Phase 4 — 生成文字版 HTML

将同样的路线数据写入 `{city}_citywalk_text.html`。

**与地图版的区别**：
- 无地图、无 Leaflet、无 JS 交互
- 纯 HTML+CSS 表格，标注每站时长
- 末尾附加交通贴士 + 美食速查
- `@media print` 优化打印分页
- 文件更小（~15KB vs ~30KB），方便手机截图

### Phase 5 — 交付

1. 用 `open` 命令打开 HTML 文件预览
2. 口述路线概览：
   - 几条路线、主题、时长
   - **访问日期和天气预报**
   - **雨天备选方案**（如需要）
3. 提醒用户注意：
   - 标注**周一闭馆**的景点
   - 需要**提前预约**的景点
   - 根据天气调整行程建议

## 坐标处理

**腾讯地图 GL 使用 GCJ-02（火星坐标系），与高德地图一致，无需转换。**

坐标来源优先级：
1. **腾讯地图 v2 JS API SearchService**（`qq.maps.SearchService`，10万次/日）— JS API 配额充足，推荐首选
2. **腾讯地图 WebService API**（`/ws/place/v1/search`，5000次/日）— 配额紧张，用于脚本批量查询
3. **OpenStreetMap Nominatim**（免费无限额）— 备选方案，但对中文 POI 精度较差（城市级）
4. 手动估算坐标（最后手段，精度约 200-2000m）

**推荐 POI 搜索（腾讯 v2 JS API，走 JS 配额 10万次/日）**：
```javascript
var searchService = new qq.maps.SearchService({
  complete: function(results) {
    results.detail.forEach(function(poi) {
      console.log(poi.name, poi.latLng.lat, poi.latLng.lng);
    });
  }
});
searchService.setLocation('长沙');
searchService.search('岳麓书院');
```

**腾讯 WebService 批量查询脚本**（`poi_precision.py`，见 `scripts/`）：
- 优先用腾讯 WebService，配额耗尽后自动切换 Nominatim
- 输出置信度（high/medium/low）和距离偏差（米）
- 低置信度结果需人工确认

**坐标格式**：腾讯地图 API 返回 `lat`/`lng` 字段，与 `TMap.LatLng(lat, lng)` 顺序一致，无需对调。

**不需要 WGS-84 → GCJ-02 转换**：腾讯地图瓦片使用 GCJ-02，直接使用 GCJ-02 坐标即可。


## 腾讯地图 GL 踩坑记录

**⚠️ 必须在 HTTP 服务下运行**：腾讯 GL API 不支持 `file://` 协议，直接双击 HTML 会报错。必须启动本地 HTTP 服务：
```bash
cd /path/to/project && python3 -m http.server 8765
# 然后访问 http://localhost:8765/citywalk_map.html
```

**⚠️ MultiMarker 创建时不能 `map: null` 再 `setMap(map)`**：会导致 Pin 不渲染。正确做法：
- 创建时始终 `map: map`
- 隐藏时用 `.hide()`，显示时用 `.show()`
- 或：创建时 `map: null`，切换路线时用 `layer.setMap(map)` / `layer.setMap(null)`

**⚠️ MultiPolyline styles 必须是 TMap.PolylineStyle 实例**：传纯 JS 对象会报运行时错误。
```javascript
styleObj['line'] = new TMap.PolylineStyle({ color: '#c0522a', width: 4 });
```

**⚠️ Pin 图标用 Canvas 生成比 SVG data URI 更可靠**：
```javascript
function makePinIcon(num, color) {
  var c = document.createElement('canvas');
  c.width = 48; c.height = 56;
  var ctx = c.getContext('2d');
  // 倒水滴形状 + 白色中心圆 + 编号文字
  return c.toDataURL('image/png');
}
```

**API 配额陷阱**：
- 腾讯 WebService（`/ws/`）配额仅 **5000次/日**，批量查询很快耗尽
- 腾讯 v2 JS API（`/jsapi_v2/`）配额 **10万次/日**，搜索功能走这个
- 如果 WebService 报错"此key每日调用量已达到上限"，切换 JS API 或 Nominatim


## 文件命名

```
{城市拼音}_citywalk_map.html    # 交互地图版
{城市拼音}_citywalk_text.html   # 纯文字清单版
```

示例：`shantou_citywalk_map.html`、`jieyang_citywalk_text.html`

## 已完成的城市

| 城市 | 日期 | 路线数 | 地图引擎 | 状态 | 版本 |
|------|------|--------|----------|------|------|
| 汕头 | 2026-04-20 | 5条 | Leaflet + 高德瓦片 | ✅ | v1.0 |
| 揭阳 | 2026-04-21 | 4条 | Leaflet + 高德瓦片 | ✅ | v1.0 |
| 长沙 | 2026-04-21 | 4条 | 腾讯地图 GL API | ✅ | v1.0 |
| 上海 | 2026-04-22 | 4条 | Leaflet + 高德瓦片 | ✅ | v1.0 |
| 大理 | 2026-04-22 | 4条 | Leaflet + 高德瓦片 | ✅ | v1.0 |
| 揭阳 | 2026-04-22 | 4条 | Leaflet + 高德瓦片 | ✅ | v1.0 |

## 版本历史

### v2.0（2026-04-22）
- ✨ 新增天气联动功能：询问访问日期，查询天气预报
- ✨ 新增开放时间标注：每个景点显示开放时间和闭馆提示
- ✨ 新增雨天备选方案：天气不佳时自动推荐室内路线
- ✨ 新增天气适配标签：路线卡片显示雨天友好度

### v1.0（2026-04-20）
- ✅ 基础 CityWalk 路线规划
- ✅ 交互式地图（Leaflet / 腾讯地图 GL）
- ✅ 城市信息模块（人文历史、行政划分、名胜古迹、都市故事）
- ✅ 美食速查和出行贴士
