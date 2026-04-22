# CityWalk HTML 生成器

使用 Python 模板引擎加速 CityWalk HTML 页面生成。

## 快速开始

### 1. 安装依赖

无需额外依赖，使用 Python 3 标准库即可。

### 2. 准备配置文件

创建 JSON 配置文件（参考 `example_changsha.json`）：

```json
{
  "city": {
    "name": "城市名称",
    "pinyin": "pinyin",
    "subtitle": "城市别称",
    "description": "一句话描述",
    "tags": ["标签1", "标签2"]
  },
  "center": [纬度, 经度],
  "zoom": 13,
  "visit_date": "2026-05-01",
  "routes": [...],
  "foods": [...],
  "explore": {...}
}
```

### 3. 生成 HTML

```bash
python citywalk_generator.py --config your_config.json --output ../docs/
```

## 配置文件结构

### 基础信息

```json
{
  "city": {
    "name": "长沙",
    "pinyin": "changsha",
    "subtitle": "星城 · 楚汉名城 · 美食之都",
    "description": "3000年城址不变，网红城市鼻祖",
    "tags": ["🏛️ 岳麓书院", "🌊 橘子洲", "🍜 臭豆腐"]
  },
  "center": [28.2282, 112.9388],
  "zoom": 13,
  "visit_date": "2026-05-01",
  "holiday_name": "五一"
}
```

### 天气信息

```json
{
  "weather": {
    "icon": "⛅",
    "temp": "26°C / 18°C",
    "desc": "多云转阴 · 适宜出行",
    "date": "2026-05-01",
    "date_note": "五一假期访问",
    "tips": ["👕 短袖+薄外套", "☂️ 带伞备用"]
  }
}
```

### 路线配置

```json
{
  "routes": [
    {
      "name": "① 湘江人文轴",
      "short_name": "湘江人文",
      "meta": "全程约 6km · 建议 4-5 小时 · 4个站点",
      "weather_tag": {
        "class": "rain-friendly",
        "text": "✅ 雨天友好 · 全程有遮挡"
      },
      "stations": [
        {
          "name": "岳麓书院",
          "lat": 28.1844,
          "lng": 112.9419,
          "hours": "07:30-18:00",
          "note": "千年学府，中国古代四大书院之一",
          "duration": "⏱️ 建议 1.5 小时 · 门票40元",
          "booking": "需提前预约"
        }
      ]
    }
  ]
}
```

### 美食配置

```json
{
  "foods": [
    { "name": "臭豆腐", "loc": "黑色经典/火宫殿 ¥10-15/份" },
    { "name": "口味虾", "loc": "文和友/虾小龙 ¥128-168/份" }
  ],
  "my_foods": [
    { "name": "我的美食", "loc": "🌟 特色推荐" }
  ]
}
```

### 城市探索模块

```json
{
  "explore": {
    "history": [
      {
        "title": "🕰️ 历史标题",
        "content": "历史内容...",
        "highlight": "<strong>重点</strong>：高亮内容"
      }
    ],
    "admin": [
      {
        "title": "📍 行政区划",
        "content": ["<strong>区名</strong>：描述", "..."]
      }
    ],
    "landmarks": [
      {
        "title": "🏛️ 必游古迹",
        "type": "list",
        "items": [
          { "name": "景点名", "desc": "描述" }
        ]
      }
    ],
    "stories": [
      {
        "title": "🌟 故事标题",
        "content": "故事内容..."
      }
    ]
  }
}
```

### 出行贴士

```json
{
  "tips": {
    "items": [
      "地铁下载「长沙地铁」APP",
      "建议住五一广场附近"
    ]
  }
}
```

## 命令行参数

```
python citywalk_generator.py [选项]

选项:
  -c, --config       配置文件路径 (JSON) [必填]
  -o, --output       输出目录 [默认: ./]
  -t, --template-dir 模板目录 [默认: ../assets/templates]
```

## 生成示例

```bash
# 生成长沙页面
python citywalk_generator.py --config example_changsha.json --output ../docs/

# 输出: ../docs/changsha-citywalk-v2.html
```

## 模板系统

### 内置模板

生成器包含默认模板，无需外部模板文件即可工作。

### 自定义模板

如需自定义模板，创建 `../assets/templates/citywalk_v2_template.html`，使用以下变量：

- `{{city_name}}` - 城市名称
- `{{visit_date}}` - 访问日期
- `{{holiday_name}}` - 节假日名称
- `{{center_lat}}`, `{{center_lng}}` - 地图中心坐标
- `{{zoom}}` - 地图缩放级别
- `{{weather_card}}` - 天气卡片 HTML
- `{{city_intro}}` - 城市介绍 HTML
- `{{holiday_alert}}` - 节假日提示 HTML
- `{{route_tabs}}` - 路线切换标签 HTML
- `{{route_sections}}` - 路线列表 HTML
- `{{food_section}}` - 美食速查 HTML
- `{{my_food_list}}` - 我的美食清单 HTML
- `{{tips_section}}` - 出行贴士 HTML
- `{{city_explore}}` - 城市探索 HTML
- `{{routes_json}}` - 路线数据 JSON

## 与 SKILL.md 配合使用

1. 使用 `SKILL.md` 中的工作流搜集城市信息
2. 将搜集到的信息整理为 JSON 配置文件
3. 使用本生成器快速生成 HTML
4. 生成的 HTML 可直接部署到 GitHub Pages

## 优势

- ⚡ **快速生成**：JSON 配置 → HTML 只需几秒钟
- 🔄 **易于修改**：修改配置重新生成，无需手动编辑 HTML
- 📝 **结构清晰**：配置文件中各模块独立，易于维护
- 🎨 **样式统一**：使用统一模板，确保风格一致
- 🧩 **模块化**：各模块可独立配置和复用
