---
name: citywalk-planner
description: >
  城市CityWalk路线规划技能。当用户要求为某个城市/目的地制作CityWalk、城市漫步、一日游、
  旅游攻略路线、步行路线规划时使用。支持生成带交互地图的HTML页面和纯文字清单版本。
  Keywords: citywalk, 城市漫步, 旅游路线, 一日游攻略, 步行路线, travel plan, itinerary。
---

# CityWalk 路线规划

为任意城市生成结构化 CityWalk 路线方案，输出两个 HTML 文件：
- **地图版**（`{city}_citywalk_map.html`）：交互地图 + 站点面板
- **文字版**（`{city}_citywalk_text.html`）：可打印的时长清单

## 工作流

### Phase 0 — 高德 API Key（可选但推荐）

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

搜索目标城市的旅游景点、美食老字号、特色街区、交通方式。

**搜索策略**（用 online-search skill）：
```
"{城市}CityWalk 旅游攻略 景点 美食" --cnt=20
"{城市} 美食 老字号 小吃 街" --cnt=15
"{城市} {核心景点} {核心景点} 坐标 位置" --cnt=15
```

每个城市搜索 3-5 轮，覆盖：景点分布、美食地图、历史文化、交通贴士。

**信息提取要点**：
- 景点名称、地址、门票、建议时长
- 老字号店铺名称、特色菜品、人均价格
- 美食街/夜市位置
- 景点间距离（判断是否可步行）
- 特色体验（日出点、夜景、演出时间等）

### Phase 2 — 路线设计

基于搜集信息，设计 3-5 条主题路线。

**路线分类建议**（按城市特点灵活调整）：
| 类型 | 主题 | 示例 |
|------|------|------|
| 历史文化 | 老城区/古建筑/博物馆 | 古城寻踪、老城寻根 |
| 美食探索 | 老字号/小吃街/夜宵 | 吃货征途、舌尖上的XX |
| 自然风光 | 山/湖/海/公园 | 山水人文、海风诗行 |
| 新城/艺术 | 新区/艺术区/文创 | 新城艺境 |
| 郊外/海岛 | 需自驾的景点群 | 南澳逐浪、水乡古韵 |

**路线排序原则**：
1. 地理位置连贯，不走回头路
2. 早→晚的时间线合理（早餐→午餐→晚餐→宵夜）
3. 登山/户外路线安排在清晨
4. 需自驾的路线单独一条
5. 全程免费的路线优先（性价比高）

**每站标注**：站点名 + 建议时长 + 一句话备注

### Phase 3 — 生成地图版 HTML

将路线数据写入 `{city}_citywalk_map.html`。

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

### Phase 4 — 生成文字版 HTML

将同样的路线数据写入 `{city}_citywalk_text.html`。

**与地图版的区别**：
- 无地图、无 Leaflet、无 JS 交互
- 纯 HTML+CSS 表格，标注每站时长
- 末尾附加交通贴士 + 美食速查
- `@media print` 优化打印分页
- 文件更小（~15KB vs ~30KB），方便手机截图

### Phase 5 — 交付

1. 用 `open` 命令打开两个 HTML 文件预览
2. 口述路线概览（几条线、主题、时长）
3. 指出该城市的独特亮点

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

| 城市 | 日期 | 路线数 | 地图引擎 | 状态 |
|------|------|--------|----------|
| 汕头 | 2026-04-20 | 5条 | Leaflet + 高德瓦片 | ✅ |
| 揭阳 | 2026-04-21 | 4条 | Leaflet + 高德瓦片 | ✅ |
| 长沙 | 2026-04-21 | 4条 | 腾讯地图 GL API | ⚠️ 部分景点坐标待手工校准 |
