# CityWalk HTML 模板说明

`assets/` 目录下存放两个 HTML 模板文件，作为生成新城市 CityWalk 页面的起点：

- `map_template.html` — 交互地图版模板
- `text_template.html` — 纯文字清单版模板

## 使用方式

生成新城市时，复制对应模板，替换占位内容：

1. 复制模板到工作区：`{city}_citywalk_map.html` / `{city}_citywalk_text.html`
2. 替换所有 `{{CITY}}` 为城市名
3. 替换 `{{CITY_PINYIN}}` 为城市拼音（文件名用）
4. 在 `routes` 对象中填入该城市的路线数据
5. 调整配色变量（可选，默认暖色调）

## 模板中的占位符

| 占位符 | 说明 |
|--------|------|
| `{{CITY}}` | 城市中文名（如"揭阳"） |
| `{{CITY_PINYIN}}` | 城市拼音（如"jieyang"） |
| `{{CITY_EN}}` | 城市英文名（如"Jieyang"） |
| `{{ROUTE_COUNT}}` | 路线数量 |
| `{{SUBTITLE}}` | 副标题描述 |

## 路线数据结构

```javascript
var routes = {
  r1: {
    color: '#c0522a',  // 路线颜色
    stations: [
      {name: '站点名', lat: 23.xxx, lng: 116.xxx, note: '一句话备注'}
    ]
  },
  // r2, r3, ...
};
```

## 配色方案

```
--terracotta: #c0522a  路线一（历史/老城）
--amber: #d4942a       路线二（美食）
--sea: #2a5c6e         路线三（自然/海景）
--purple: #7a5c8a      路线四（艺术/古村）
--green: #2a7a5c       路线五（海岛/郊外）
```
