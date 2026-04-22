# 🚶 CityWalk Planner Skill

一个用于生成城市 CityWalk 路线规划的 WorkBuddy Skill，支持输出交互式地图和纯文字清单两种格式。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ 功能特性

- 🗺️ **交互式地图** - 基于腾讯地图 GL API，支持路线切换、标记点击、站点详情展示
- 📝 **纯文字清单** - 可打印的表格化路线，适合手机截图或纸质携带
- 🎨 **精美视觉** - 暖色调设计，响应式布局，支持桌面端和移动端
- 📍 **坐标精确** - 支持高德/腾讯 POI API 获取精确坐标，内置坐标系转换
- 🔄 **多主题路线** - 支持历史文化、美食探索、自然风光、新城艺术等多种主题

---

## 🚀 快速开始

### 安装 Skill

1. 克隆本仓库到 WorkBuddy skills 目录：

```bash
# 用户级 Skill（推荐）
git clone https://github.com/zljie/citywalk-planner-skill.git ~/.workbuddy/skills/citywalk-planner

# 或项目级 Skill
git clone https://github.com/zljie/citywalk-planner-skill.git ./.workbuddy/skills/citywalk-planner
```

2. 重启 WorkBuddy 或重新加载技能

### 使用方法

在 WorkBuddy 中直接输入：

```
帮我规划一下长沙的 CityWalk 路线
```

或：

```
生成一份汕头一日游攻略
```

---

## 📁 项目结构

```
citywalk-planner/
├── SKILL.md                      # Skill 主文档（工作流说明）
├── README.md                     # 本文件
├── assets/
│   ├── map_template.html         # 交互地图版 HTML 模板
│   └── text_template.html        # 纯文字版 HTML 模板
├── references/
│   ├── gcj02_conversion.md       # GCJ-02 坐标转换参考
│   └── template_guide.md         # 模板使用指南
└── scripts/
    └── poi_precision.py          # POI 坐标批量查询脚本
```

---

## 🗺️ 输出示例

### 交互地图版
- 腾讯地图 GL 渲染
- 多路线切换导航
- 编号标记点 + 路线折线
- 点击标记显示站点详情
- 右侧站点列表联动

### 纯文字版
- 表格化路线展示
- 每站建议时长标注
- 交通贴士 + 美食速查
- 打印优化（`@media print`）
- 文件小巧（~15KB），适合手机截图

---

## ⚙️ 配置说明

### 腾讯地图 API Key（可选但推荐）

1. 访问 [腾讯位置服务](https://lbs.qq.com/) 注册账号
2. 控制台 → 应用管理 → 创建应用 → 添加 Key
3. 服务平台选择 "WebService API"
4. 复制 Key 并在生成 HTML 时替换 `YOUR_KEY`

> 💡 **配额说明**：
> - WebService API：5000 次/日（用于批量坐标查询）
> - JS API v2：10 万次/日（用于地图渲染，配额充足）

### 高德地图 API Key（备选）

如需使用高德 POI 获取精确坐标：

1. 访问 [高德开放平台](https://lbs.amap.com/) 注册
2. 创建应用 → 添加 Key（服务平台选 "Web服务"）
3. 使用 `scripts/poi_precision.py` 批量查询坐标

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 地图引擎 | 腾讯地图 JavaScript API GL |
| 坐标系 | GCJ-02（火星坐标系） |
| 样式 | 原生 CSS + 暖色调设计 |
| 字体 | Ma Shan Zheng / Noto Serif SC / Noto Sans SC |
| 脚本 | Python 3 |

---

## 📝 路线设计原则

1. **地理位置连贯** - 不走回头路，优化步行路径
2. **时间线合理** - 早→晚的时间安排（早餐→午餐→晚餐→宵夜）
3. **体力分配** - 登山/户外路线安排在清晨
4. **交通优化** - 需自驾的路线单独成线
5. **性价比优先** - 全程免费的路线优先推荐

---

## 🌍 已完成城市

| 城市 | 路线数 | 主题覆盖 | 状态 | 在线预览 |
|------|--------|----------|------|----------|
| 长沙 | 4条 | 湘江人文、历史老街、文化山脉、夜味长沙 | ✅ 完整 | [查看地图](https://zljie.github.io/citywalk-planner-skill/changsha-citywalk.html) |
| 上海 | 4条 | 外滩经典、法租界、老城厢、陆家嘴 | ✅ 完整 | [查看地图](https://zljie.github.io/citywalk-planner-skill/shanghai-citywalk.html) |
| 汕头 | 4条 | 小公园老城、开埠文化、海滨风光、潮汕美食 | ✅ 完整 | [查看地图](https://zljie.github.io/citywalk-planner-skill/shantou-citywalk.html) |
| 揭阳 | 4条 | 古城文化、宗教古迹、美食探索、山水风光 | ✅ 完整 | [查看地图](https://zljie.github.io/citywalk-planner-skill/jieyang-citywalk.html) |
| 大理 | 4条 | 古城漫步、洱海环湖、苍山探秘、双廊慢生活 | ✅ 完整 | [查看地图](https://zljie.github.io/citywalk-planner-skill/dali-citywalk.html) |

### 🌐 GitHub Pages 在线预览

本仓库已配置 GitHub Pages，可直接在线查看城市路线地图：

**🔗 首页**: https://zljie.github.io/citywalk-planner-skill/

**📍 各城市直达**:
- [长沙 CityWalk](https://zljie.github.io/citywalk-planner-skill/changsha-citywalk.html)
- [上海 CityWalk](https://zljie.github.io/citywalk-planner-skill/shanghai-citywalk.html)
- [汕头 CityWalk](https://zljie.github.io/citywalk-planner-skill/shantou-citywalk.html)
- [揭阳 CityWalk](https://zljie.github.io/citywalk-planner-skill/jieyang-citywalk.html)
- [大理 CityWalk](https://zljie.github.io/citywalk-planner-skill/dali-citywalk.html)

> 💡 **提示**: 如果链接无法访问，请确保仓库已启用 GitHub Pages（Settings → Pages → Source → Deploy from a branch → main/docs）

---

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

- 腾讯地图 API 提供地图服务
- 高德地图 API 提供 POI 数据
- WorkBuddy 平台提供 Skill 运行环境

---

<p align="center">
  Made with ❤️ for CityWalk lovers
</p>
