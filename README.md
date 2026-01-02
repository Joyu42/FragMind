# FragMind - 碎片化思维整理与日记生成 💭

> 基于 AI Agent 的碎片化思维整理与日记生成系统

## 📖 项目简介

FragMind 是一个创新的智能日记应用，核心理念是"**碎碎念就是生产力**"。它允许你随时记录碎片化的想法，然后通过 AI Agent 自动整理成连贯的日记，帮助你将零散的思维碎片转化为有价值的知识和见解。

### 核心功能

- 📝 **碎片化思维捕捉**：随时记录想法，不需要完整句子
- 🤖 **AI 智能整理**：使用 LLM Agent 将碎片化记录整理成完整日记
- ✅ **智能 Todo 系统**：自然语言创建待办事项（如"明天下午3点开会"）
- 💾 **本地存储**：使用 SQLite 数据库，数据完全本地化
- 🖥️ **桌面 GUI**：基于 PyQt6 的现代化界面

### 设计理念

传统日记需要刻意整理思路，而现代生活节奏快，想法往往是碎片化的。FragMind 让你：

1. **用 AI 语音记录碎片思维**（未来功能）：散步、骑车、洗澡时想到什么说什么
2. **用 AI Agent 把碎片思维再加工**：整理出项目提案、待办事项等
3. **用 AI 识图把纸质记录电子化**（未来功能）：便签纸上的思考一键数字化

## 🚀 快速开始

### 环境要求

- Python 3.10+
- uv（现代 Python 包管理工具）
- LLM API（可选：OpenAI、智谱AI GLM-4、华为盘古）

### 安装步骤

1. **克隆或下载项目**
```bash
cd FragMind
```

2. **安装 uv**（如果还没装）
```bash
# macOS
brew install uv

# 或通过 pip
pip install uv
```

3. **安装项目依赖**
```bash
# 基础依赖
uv sync

# 或者安装包含 LLM 的完整依赖
uv sync --extra llm
```

4. **配置 LLM API**
```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# 推荐使用智谱 AI（有免费额度且符合大作业要求）
```

5. **运行应用**
```bash
uv run python src/main.py

# 或者直接运行（需要在 pyproject.toml 中配置脚本入口）
uv run fragmind
```

## 📁 项目结构

```
FragMind/
├── src/
│   ├── main.py           # 应用入口
│   ├── config.py         # 配置管理
│   ├── models/           # 数据模型
│   │   └── __init__.py   # DiaryEntry, DiarySummary, TodoItem
│   ├── database/         # 数据库层
│   │   └── db_manager.py # SQLite 操作封装
│   ├── services/         # 服务层
│   │   └── llm_service.py # LLM API 调用
│   └── ui/               # GUI 界面
│       └── main_window.py # 主窗口
├── tests/                # 测试文件
├── docs/                 # 文档
├── assets/               # 资源文件
├── pyproject.toml        # 项目配置（uv 标准）
├── uv.lock              # 依赖锁定文件
├── .env.example         # 配置模板
└── README.md            # 项目说明
```

## 🎯 使用指南

### 1. 记录碎片化想法

在左侧输入框中输入任何想法，点击"💾 保存片段"即可记录。

### 2. 生成完整日记

积累一定片段后，点击"✨ 生成今日总结"，AI 会自动将碎片整理成连贯的日记。

### 3. 创建待办事项

在输入框中输入自然语言，如：
- "明天下午3点开会"
- "下周一交Python大作业"
- "提醒我买牛奶"


### uv 常用命令

```bash
# 同步依赖（安装/更新）
uv sync

# 同步并安装可选依赖组
uv sync --extra llm
uv sync --extra dev

# 运行应用
uv run python src/main.py

# 运行测试
uv run pytest

# 添加新依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 删除依赖
uv remove package-name

# 更新所有依赖
uv sync --upgrade

# 显示依赖树
uv pip show --dependency-tree
```
点击"✅ 创建待办"，AI 会自动解析时间、优先级等信息。

## 🔧 技术栈

- **GUI 框架**：PyQt6
- **LLM 集成**：支持 OpenAI、智谱 GLM-4、华为盘古
- **数据存储**：SQLite
- **配置管理**：python-dotenv
- **包管理**：uv（超快的 Python 包管理器）
- **项目管理**：pyproject.toml（PEP 517/518 标准）

## 📝 开发计划

### 已完成 ✅
- [x] 基础项目结构
- [x] 数据模型和数据库层
- [x] LLM 服务集成
- [x] GUI 主窗口框架
- [x] 日记片段记录功能
- [x] AI 总结生成功能
- [x] Todo 自然语言解析

### 进行中 🚧
- [ ] 完善 UI 样式
- [ ] 添加日历视图
- [ ] 搜索和标签功能

### 未来功能 💡
- [ ] 语音输入（语音转文字）
- [ ] 图片 OCR 识别
- [ ] 导出功能（Markdown, PDF）
- [ ] 多端同步（云存储）
- [ ] 数据备份和恢复
- [ ] 深色主题

## 🎓 大作业说明

本项目作为 Python 语言与系统设计课程大作业，具有以下特点：

1. **技术综合性**：涵盖 GUI 开发、数据库操作、API 集成、AI Agent 应用
2. **实用价值**：解决真实的知识管理痛点
3. **可扩展性**：预留了语音、OCR、多端同步等扩展接口
4. **符合要求**：可接入华为昇腾/盘古等国产资源

## 📄 许可证

MIT License

## 👨‍💻 作者

- 课程：Python 语言与系统设计
- 学期：2025-2026 第一学期

## 🙏 致谢

感谢以下开源项目和服务：
- PyQt6
- OpenAI API / 智谱 AI GLM-4
- SQLite
