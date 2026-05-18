# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language Constraint

使用中文回答所有问题。

## Project Overview

AIWardrobe is a full-stack web application for managing clothing items and generating AI-powered outfit recommendations. It consists of a React + Vite frontend and a FastAPI backend, with MySQL for persistence (SQLite compatible).

## Common Commands

### Development
```bash
# Copy environment template
cp backend/.env.example backend/.env

# Start all services (macOS/Linux)
./start.sh

# Start all services (Windows)
start.bat

# Or manually run separately:
# Backend
cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

### Frontend
```bash
cd frontend
npm run dev      # Development server on port 5173
npm run build    # Production build
npm run lint     # ESLint check
npm run preview  # Preview production build
```

### Backend
```bash
cd backend
uvicorn main:app --reload --port 8000  # API server on port 8000
# API docs available at http://localhost:8000/docs
```

### Docker
```bash
# 构建并启动 (Windows/WSL)
powershell.exe -NoProfile -Command "& {Set-Location 'C:\sunyahuiProject\AIWardrobe'; docker compose build}"
powershell.exe -NoProfile -Command "& {Set-Location 'C:\sunyahuiProject\AIWardrobe'; docker compose up -d}"

# 强制重建容器
powershell.exe -NoProfile -Command "& {Set-Location 'C:\sunyahuiProject\AIWardrobe'; docker compose down; docker compose up -d --force-recreate}"

# 查看日志
powershell.exe -NoProfile -Command "& {Set-Location 'C:\sunyahuiProject\AIWardrobe'; docker compose logs -f}"
```

**注意**：在 Windows/WSL 环境下调用 Docker 必须使用 `powershell.exe`，不能直接在 bash 中调用。

### Docker 镜像
- 镜像地址：`ghcr.io/namesunyahui/aiwardrobe:latest`
- 部署服务器时使用：`docker pull ghcr.io/namesunyahui/aiwardrobe:latest`

## Architecture

### Technology Stack
- **Frontend**: React 19, Vite 7, Tailwind CSS 4, React Router 7, i18next
- **Backend**: FastAPI, Python, MySQL (SQLAlchemy + aiomysql)
- **AI Services**: Google Gemini, OpenAI-compatible APIs, rembg (支持轻量模型 u2netp/silueta)
- **Weather API**: 和风天气 QWeather (中文) / Open-Meteo (日语/英语)
- **Horoscope**: 自研动态运势生成算法（每日更新）

### Directory Structure
```
AIWardrobe/
├── CLAUDE.md                    # 本文件 - Claude Code 项目指南
├── Claude-Code-Skills.md        # 斜杠命令和技能完整指南
├── README.md                    # 项目英文 README
├── README.zh-CN.md              # 项目中文 README
├── design-system/               # 规划文件目录
│   ├── task_plan.md             # 任务规划
│   ├── findings.md              # 研究发现
│   └── progress.md              # 进度追踪
├── docs/                        # 项目文档（待建设）
│   └── images/                  # 文档图片
├── 错误文档/                     # 错误记录文档
├── frontend/                    # React SPA (port 5173)
│   └── src/
│       ├── pages/               # 路由页面
│       ├── components/          # UI 组件
│       ├── contexts/            # React contexts
│       └── utils/               # API 工具
└── backend/                     # FastAPI (port 8000)
    ├── api/                     # 路由处理
    ├── services/                # 业务逻辑
    ├── domain/                  # 数据模型
    └── storage/                 # 数据库和配置
```

### API Structure
| Prefix | Purpose |
|--------|---------|
| `/api/auth` | User authentication (register, login, token refresh, profile) |
| `/api/settings` | User preferences (theme, language, location, zodiac, notifications) |
| `/api/avatar` | User avatar upload, get, delete |
| `/api/upload` | Upload and process clothing images |
| `/api/wardrobe`, `/api/clothes` | Clothing CRUD operations |
| `/api/admin/users` | Admin user management (list, detail, enable/disable, promote/demote) |
| `/api/admin/stats` | Admin statistics |
| `/api/config`, `/api/models` | LLM configuration management |
| `/api/weather`, `/api/cities` | Weather data for recommendations |
| `/api/recommendation` | AI outfit recommendations |
| `/api/recommendations/history` | Recommendation history & favorites |
| `/api/horoscope` | Daily horoscope (cached) |

### Database Schema
MySQL 数据库，包含以下主要表：
- **users**: 用户账户信息
- **user_settings**: 用户偏好设置
- **clothes**: 衣物 items，包含 category, item, style/season/usage_semantics (JSON), color, description, image_key
- **recommendation_records**: AI 推荐历史
- **horoscope_record**: 星座运势缓存数据

### Key Configuration
- Backend reads from `backend/.env` for API keys (GEMINI_API_KEY, QWEATHER_API_KEY)
- LLM config persisted to `backend/storage/llm_config.json`
- Database: MySQL (通过环境变量配置) 或 SQLite（默认兼容）
- MySQL 配置环境变量：MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
- SQLite 配置：DB_FILE_PATH（仅当未配置 MySQL 时使用）
- MinIO 图片存储：MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET, MINIO_SECURE

## Workflow Constraints

### 编译检查（必须）
- **前端代码**：每次修改后必须运行 `npm run build` 检查编译是否成功
- **后端代码**：每次修改后必须验证后端能正常启动
- **编译失败**：如果编译失败，必须立即修复问题，不能留到后面处理
- 检查编译没有问题后再报告任务完成

### 规划文件
- 使用 planning-with-files skill 时，计划文件必须放在 `design-system/` 目录下
- 包含：task_plan.md, findings.md, progress.md

### 编码前
- 开始任何编码任务前，使用 `Skill` 工具调用 `karpathy-guidelines` skill

### 编码后
- 编码任务完成后，使用 `Skill` 工具调用 `neat-freak` skill 更新全部文档

### 敏感信息处理
- **禁止提交**：密码、API Key、Token、密钥等敏感信息禁止提交到 Git
- **环境变量**：使用 `.env` 文件存储敏感信息（已在 .gitignore 中排除）
- **示例配置**：提供 `.env.example` 文件作为模板，包含所有需要的环境变量占位符
- **pre-commit 钩子**：已配置 Git pre-commit 钩子，自动检测可能泄露的敏感信息
- **检测模式**：包括 password=, api_key=, secret=, access_token=, AWS keys, GitHub tokens, OpenAI keys 等

## Claude Code 技能参考

本项目已配置丰富的 Claude Code 技能，详细信息请参考：
- **技能和斜杠命令**：`Claude-Code-Skills.md`

### 常用技能速查

```bash
# 代码理解
Skill(understand)              # 综合代码理解
Skill(understand-diff)         # 理解代码变更
Skill(understand-explain)      # 解释代码
Skill(understand-domain)       # 理解领域模型
Skill(understand-onboard)      # 新成员入职

# 代码质量
/skill simplify                # 简化代码
/skill security-review         # 安全审查
/skill review                  # PR 审查

# 前端设计
Skill(frontend-design)         # 创建高质量前端界面

# 自动化测试
Skill(agent-browser)           # 浏览器自动化
Skill(playwright-cli)          # Playwright 测试

# 搜索研究
Skill(tavily-search)           # 网络搜索
Skill(scrapling-official)      # 网页抓取
Skill(find-skills)             # 发现技能

# UI/UX
Skill(ui-ux-pro-max)           # 高级 UI/UX 分析
Skill(baseline-ui)             # UI 基线验证
Skill(frontend-design)         # 前端界面设计

# 项目规划
Skill(planning-with-files)     # 文件式规划
Skill(planning-with-files-skill) # 文件规划技能版
Skill(loop)                    # 循环执行任务

# 文档处理
Skill(docx)                    # Word 文档处理
Skill(pptx)                    # PowerPoint 处理
Skill(humanizer-zh)            # AI 文本人性化

# 系统
Skill(init)                    # 初始化项目
Skill(neat-freak)              # 同步文档和记忆
Skill(syh-docker)              # Docker 调用
```

## Important Notes

- Frontend proxies API requests to backend via Vite dev server configuration
- Images are stored in MinIO object storage (`aiwardrobe` bucket)
- Image compression is applied on upload (max 1024x1024, PNG format)
- The backend serves both API routes and the built frontend in production
- CI/CD builds multi-platform Docker images (linux/amd64, linux/arm64) pushed to ghcr.io