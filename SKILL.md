---
name: citywalk-planner
description: >
  城市CityWalk路线规划技能。当用户要求为某个城市/目的地制作CityWalk、城市漫步、一日游、
  旅游攻略路线、步行路线规划时使用。支持生成带交互地图的HTML页面和纯文字清单版本。
  支持天气联动、景点开放时间查询、雨天备选路线推荐、城市探索模块。
  Keywords: citywalk, 城市漫步, 旅游路线, 一日游攻略, 步行路线, travel plan, itinerary, 天气, 开放时间, 城市探索。
---

# CityWalk 路线规划

为任意城市生成结构化 CityWalk 路线方案，输出两个 HTML 文件：
- **地图版**（`{city}-citywalk-v2.html`）：交互地图 + 站点面板 + 天气模块 + 开放时间 + 城市探索
- **文字版**（`{city}-citywalk-text.html`）：可打印的时长清单 + 天气提示

## 页面结构标准（v2.0）

生成的 HTML 页面必须包含以下模块，按顺序排列：

### 侧边栏模块（从上到下）

1. **天气卡片** — 访问日期天气、温度、穿衣建议
2. **城市介绍** — 城市名称、别称、一句话简介、城市标签
3. **五一特别提示**（如适用）— 节假日专属提醒
4. **路线列表** — 3-5条主题路线，每条可展开查看站点
5. **美食速查** — 必吃美食网格卡片
6. **我的美食清单**（可选）— 用户自定义美食收藏
7. **出行贴士** — 交通、住宿、预算、注意事项
8. **城市探索** — 四个标签页：人文历史、行政划分、名胜古迹、都市故事

### 地图区域

- 左侧/上方：Leaflet 交互地图
- 路线折线（不同颜色区分）
- 编号标记点（点击联动侧边栏）
- 高德地图瓦片（GCJ-02坐标系）

## 核心功能模块

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
- 路线卡片显示雨天适配标签（雨天友好/雨天谨慎/雨天避开）

### 🏛️ 城市探索模块
- **人文历史**：城市历史沿革、文化特色、历史地位
- **行政划分**：行政区划、城市格局、基本数据（面积、人口、GDP）
- **名胜古迹**：必游古迹、文化场馆、自然风光
- **都市故事**：城市传说、美食故事、文化典故、冷知识

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

### Phase 3 — 生成地图版 HTML（v2.0标准）

将路线数据写入 `{city}-citywalk-v2.html`。

**技术栈**：
- **地图引擎**：Leaflet + 高德地图瓦片（避免腾讯地图API配额限制和鉴权问题）
- **坐标系**：GCJ-02（火星坐标系），与高德瓦片匹配
- **样式框架**：纯 CSS + 原生 JavaScript（无框架依赖）

**核心模块实现**：

#### 1. 天气卡片模块
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
  <div class="weather-date">📅 2026-05-01 五一假期访问</div>
  <div class="weather-tips">
    <span class="tip-tag">👕 短袖+薄外套</span>
    <span class="tip-tag">☂️ 带伞备用</span>
    <span class="tip-tag">🧴 注意防晒</span>
    <span class="tip-tag">👟 舒适步行鞋</span>
  </div>
</div>
```

#### 2. 城市介绍模块
```html
<div class="city-intro">
  <div class="city-name">汕头</div>
  <div class="city-sub">百载商埠 · 海丝门户 · 美食之都<br>1860年开埠，潮汕文化发源地</div>
  <div class="city-tags">
    <span class="city-tag">🏛️ 小公园</span>
    <span class="city-tag">🌊 南澳岛</span>
    <span class="city-tag">🍲 牛肉火锅</span>
  </div>
</div>
```

#### 3. 路线模块（含雨天适配标签）
```html
<div class="route-section" id="route-r1">
  <div class="route-header" onclick="toggleRoute('r1')">
    <div class="route-label">
      <div class="route-dot" style="background:var(--route1)"></div>
      <div class="route-title">① 老城开埠之旅</div>
    </div>
    <div class="route-meta">全程约 4km · 建议 5-6 小时 · 6个站点</div>
    <div class="route-weather-tag rain-friendly">✅ 雨天友好 · 骑楼可避雨</div>
  </div>
  <div class="stations" id="stations-r1">
    <div class="station-item" data-route="r1" data-index="0" onclick="focusStation('r1', 0)">
      <div class="station-num" style="background:var(--route1)">1</div>
      <div class="station-info">
        <div class="station-name">小公园中山纪念亭</div>
        <div class="station-hours">🕐 全天开放</div>
        <div class="station-note">汕头老城核心地标，放射状骑楼街区</div>
        <div class="station-duration">⏱️ 建议 1-1.5 小时 · 免费</div>
      </div>
    </div>
  </div>
</div>
```

#### 4. 美食速查模块
```html
<div class="food-section">
  <div class="food-title">🍜 必吃美食速查</div>
  <div class="food-grid">
    <div class="food-item">
      <div class="food-name">牛肉火锅</div>
      <div class="food-loc">杏花吴记/八合里 ¥100-150/人</div>
    </div>
  </div>
</div>
```

#### 5. 城市探索模块（四标签页）
```html
<div class="city-info-section">
  <div class="info-tabs">
    <div class="info-tab active" onclick="switchInfoTab(this, 'history')">📜 人文历史</div>
    <div class="info-tab" onclick="switchInfoTab(this, 'admin')">🏛️ 行政划分</div>
    <div class="info-tab" onclick="switchInfoTab(this, 'landmarks')">🏯 名胜古迹</div>
    <div class="info-tab" onclick="switchInfoTab(this, 'stories')">🌟 都市故事</div>
  </div>
  
  <!-- 人文历史 -->
  <div class="info-content active" id="info-history">
    <div class="info-card">
      <h4>🕰️ 百载商埠</h4>
      <p>城市历史介绍...</p>
      <div class="highlight-box">
        <p><strong>海丝门户</strong>：特色亮点...</p>
      </div>
    </div>
  </div>
  
  <!-- 其他三个标签页... -->
</div>
```

#### 6. Leaflet 地图实现
```javascript
// 初始化地图（高德瓦片）
var map = L.map('map-container').setView([23.3535, 116.7311], 13);

L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
  subdomains: '1234',
  attribution: '© 高德地图'
}).addTo(map);

// 创建编号标记
function createNumberedMarker(lat, lng, number, color, title) {
  var canvas = document.createElement('canvas');
  canvas.width = 32; canvas.height = 40;
  var ctx = canvas.getContext('2d');
  // 绘制倒水滴形状 + 编号
  return L.marker([lat, lng], {
    icon: L.divIcon({
      className: 'custom-marker',
      html: canvas.toDataURL(),
      iconSize: [32, 40],
      iconAnchor: [16, 40]
    })
  }).addTo(map).bindPopup(title);
}

// 绘制路线折线
var routeLine = L.polyline([[lat1, lng1], [lat2, lng2]], {
  color: '#c0522a', weight: 4, opacity: 0.8
}).addTo(map);
```

**视觉风格标准**：
- 主色调：暖色系（cream #faf7f2 / terracotta #c0522a / amber #d4942a）
- 字体：Ma Shan Zheng（标题）+ Noto Serif SC（正文）+ Noto Sans SC（UI）
- 布局：桌面端左右分栏（地图左侧，侧边栏右侧400px），移动端上下分栏
- 圆角：卡片 12px，按钮 8px，标签 16px
- 阴影：卡片使用柔和阴影 `0 2px 8px rgba(0,0,0,0.08)`

---

### CSS 样式标准（v2.0）

#### 变量定义
```css
:root {
  --ink: #1a1410;
  --warm-dark: #3d2b1f;
  --terracotta: #c0522a;
  --amber: #d4942a;
  --sand: #f5efe6;
  --cream: #faf7f2;
  --sea: #2a5c6e;
  --muted: #7a6a5a;
  --border: #ddd0c0;
  --route1: #c0522a;
  --route2: #d4942a;
  --route3: #2a5c6e;
  --route4: #7a5c8a;
}
```

#### 模块样式速查

**天气卡片**：
```css
.weather-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px; padding: 16px 20px;
  margin: 0 20px 16px; color: white;
}
.weather-main { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.weather-icon { font-size: 36px; }
.weather-temp { font-size: 20px; font-weight: 600; }
.weather-desc { font-size: 13px; opacity: 0.9; margin-top: 2px; }
.weather-date { font-size: 12px; opacity: 0.8; margin-bottom: 10px; }
.weather-tips { display: flex; gap: 8px; flex-wrap: wrap; }
.tip-tag { background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 12px; font-size: 11px; }
```

**城市介绍**：
```css
.city-intro { padding: 20px; text-align: center; border-bottom: 1px solid var(--border); }
.city-name { font-family: 'Ma Shan Zheng', cursive; font-size: 36px; color: var(--terracotta); margin-bottom: 8px; }
.city-sub { font-size: 13px; color: var(--muted); line-height: 1.6; margin-bottom: 16px; }
.city-tags { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }
.city-tag { background: var(--sand); padding: 6px 12px; border-radius: 16px; font-size: 12px; color: var(--warm-dark); }
```

**路线模块**：
```css
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
```

**站点列表**：
```css
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
```

**美食模块**：
```css
.food-section { padding: 20px; border-bottom: 1px solid var(--border); }
.food-title { font-family: 'Noto Serif SC', serif; font-size: 16px; font-weight: 600; color: var(--warm-dark); margin-bottom: 16px; }
.food-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.food-item { background: white; border-radius: 12px; padding: 14px; border: 1px solid var(--border); transition: all 0.2s; }
.food-item:hover { border-color: var(--terracotta); transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.food-name { font-weight: 600; color: var(--warm-dark); font-size: 14px; margin-bottom: 4px; }
.food-loc { font-size: 12px; color: var(--muted); }
```

**城市探索模块**：
```css
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
```

**出行贴士**：
```css
.tips-section { padding: 20px; background: linear-gradient(135deg, var(--sand) 0%, #f0ece4 100%); }
.tips-title { font-family: 'Noto Serif SC', serif; font-size: 16px; font-weight: 600; color: var(--warm-dark); margin-bottom: 12px; }
.tip-item { font-size: 13px; color: var(--muted); line-height: 1.8; margin-bottom: 8px; padding-left: 16px; position: relative; }
.tip-item::before { content: "•"; color: var(--terracotta); position: absolute; left: 0; font-weight: bold; }
```

**五一特别提示**：
```css
.holiday-alert { background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); border-radius: 12px; padding: 16px 20px; margin: 0 20px 16px; border-left: 4px solid var(--amber); }
.holiday-alert-title { font-weight: 600; color: #e65100; margin-bottom: 10px; font-size: 14px; }
.holiday-alert ul { font-size: 12px; color: var(--muted); line-height: 1.8; padding-left: 16px; }
.holiday-alert li { margin-bottom: 6px; }
```

**布局与响应式**：
```css
/* 主布局 */
.main { display: flex; height: calc(100vh - 56px); margin-top: 56px; }
#map-container { flex: 1; position: relative; }
.sidebar { width: 400px; height: 100%; overflow-y: auto; background: var(--cream); border-left: 1px solid var(--border); }

/* 顶部导航 */
.topbar { position: fixed; top: 0; left: 0; right: 0; height: 56px; background: rgba(250,247,242,0.96); backdrop-filter: blur(8px); border-bottom: 1px solid var(--border); display: flex; align-items: center; padding: 0 20px; z-index: 1000; gap: 10px; }
.topbar-title { font-family: 'Ma Shan Zheng', cursive; font-size: 20px; color: var(--terracotta); }
.route-tabs { display: flex; gap: 8px; margin-left: auto; }
.route-tab { padding: 6px 14px; border-radius: 16px; border: 1px solid var(--border); font-size: 12px; cursor: pointer; background: white; color: var(--muted); transition: all 0.2s; }
.route-tab:hover, .route-tab.active { background: var(--terracotta); color: white; border-color: var(--terracotta); }

/* 响应式 */
@media (max-width: 768px) {
  .main { flex-direction: column; }
  #map-container { height: 50vh; }
  .sidebar { width: 100%; height: 50vh; border-left: none; border-top: 1px solid var(--border); }
  .topbar-title { font-size: 16px; }
  .food-grid { grid-template-columns: 1fr; }
  .sidebar { width: 100%; }
}
```

### Phase 4 — 生成文字版 HTML

将同样的路线数据写入 `{city}-citywalk-text.html`。

**与地图版的区别**：
- 无地图、无 Leaflet、无 JS 交互
- 纯 HTML+CSS 表格，标注每站时长
- 末尾附加交通贴士 + 美食速查 + 城市探索（精简版）
- `@media print` 优化打印分页
- 文件更小（~15KB vs ~50KB），方便手机截图

**文字版结构**：
1. 标题 + 访问日期
2. 天气提示卡片
3. 路线清单（表格形式，含时长、开放时间）
4. 美食速查
5. 城市探索（人文历史 + 名胜古迹，精简版）
6. 出行贴士

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

**使用 GCJ-02（火星坐标系），与高德地图瓦片匹配。**

坐标来源优先级：
1. **高德地图 POI API** — 直接获得 GCJ-02，精度最高 ✅ 推荐
2. **腾讯地图 API** — 获得 GCJ-02，与高德一致
3. **OpenStreetMap Nominatim** — 获得 WGS-84，需要转换
4. 手动估算坐标（最后手段，精度约 200-2000m）

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
// 估算坐标（WGS-84）→ 转换为 GCJ-02 → 用于高德瓦片
const gcj = wgs84ToGcj02(28.1857, 112.9445);
L.marker([gcj.lat, gcj.lng]).addTo(map);
```

**坐标校验清单**：
- [ ] 所有坐标是否在城市合理范围内？
- [ ] 标记是否落入水中/明显错误位置？
- [ ] 相邻站点距离是否合理？（步行 < 3km）


## 文件命名

```
{city}-citywalk-v2.html    # 交互地图版（v2.0标准）
{city}-citywalk-text.html  # 纯文字清单版
```

示例：`shantou-citywalk-v2.html`、`jieyang-citywalk-text.html`

**旧版文件（已归档）**：
- `{city}_citywalk_map.html` — v1.0 地图版（腾讯地图 GL）
- `{city}_citywalk_text.html` — v1.0 文字版

## 已完成的城市

| 城市 | 日期 | 路线数 | 地图引擎 | 状态 | 版本 |
|------|------|--------|----------|------|------|
| 汕头 | 2026-04-22 | 4条 | Leaflet + 高德瓦片 | ✅ | v2.0 |
| 揭阳 | 2026-04-22 | 4条 | Leaflet + 高德瓦片 | ✅ | v2.0 |
| 长沙 | 2026-04-22 | 4条 | Leaflet + 高德瓦片 | ✅ | v2.0 |

## 版本历史

### v2.0（2026-04-22）
- ✨ **全新页面结构**：天气卡片 → 城市介绍 → 路线列表 → 美食速查 → 出行贴士 → 城市探索
- ✨ **城市探索模块**：人文历史、行政划分、名胜古迹、都市故事四个标签页
- ✨ **天气联动功能**：询问访问日期，查询天气预报，雨天推荐室内路线
- ✨ **开放时间标注**：每个景点显示开放时间和闭馆提示
- ✨ **雨天适配标签**：路线卡片显示雨天友好度（雨天友好/谨慎/避开）
- ✨ **技术栈升级**：统一使用 Leaflet + 高德瓦片，避免腾讯地图 API 配额限制
- ✨ **样式标准化**：暖色调统一风格，响应式布局

### v1.0（2026-04-20）
- ✅ 基础 CityWalk 路线规划
- ✅ 交互式地图（腾讯地图 GL / Leaflet）
- ✅ 美食速查和出行贴士
- ⚠️ 地图引擎不统一，部分使用腾讯 GL API 有配额限制
