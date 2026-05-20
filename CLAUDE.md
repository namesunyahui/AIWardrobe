# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language Constraint

使用中文回答所有问题。

## Project Overview

AIWardrobe is a full-stack web application for managing clothing items and generating AI-powered outfit recommendations. It consists of a React + Vite frontend and a FastAPI backend, with MySQL for persistence.

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
├── README.md                    # 项目英文 README
├── README.zh-CN.md              # 项目中文 README
├── design-system/               # 规划文件目录
│   └── aiwardrobe/              # 详细设计文档
│       └── MASTER.md            # 设计主文档
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
- Backend reads from `backend/.env` for API keys
- LLM config persisted to `backend/storage/llm_config.json`
- Database: MySQL (通过环境变量配置)
- MySQL 配置环境变量：MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
- MinIO 图片存储：MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET, MINIO_SECURE
- JWT 配置：JWT_SECRET（必需）

## 开发流程

每次编码任务遵循以下流程：

1. **编码前** → 调用 `/skill karpathy-guidelines` 遵循编码规范
2. **编码中** → 编写代码
3. **编码后** →
   - 前端：运行 `npm run build` 验证编译成功
   - 后端：验证服务能正常启动
   - 确保编译/启动成功后再报告完成
   - 调用 `/skill neat-freak` 同步文档和记忆

### 敏感信息处理
- **禁止提交**：密码、API Key、Token、密钥等敏感信息禁止提交到 Git
- **环境变量**：使用 `.env` 文件存储敏感信息（已在 .gitignore 中排除）
- **示例配置**：提供 `.env.example` 文件作为模板，包含所有需要的环境变量占位符
- **pre-commit 钩子**：已配置 Git pre-commit 钩子，自动检测可能泄露的敏感信息
- **检测模式**：包括 password=, api_key=, secret=, access_token=, AWS keys, GitHub tokens, OpenAI keys 等

## Claude Code 技能参考

本项目已配置丰富的 Claude Code 技能。使用 `/skill` 斜杠命令来调用技能。

### 常用斜杠命令

```bash
/skill understand       # 综合代码理解
/skill simplify        # 简化代码
/skill review          # 代码审查
/skill security-review # 安全审查
/skill neat-freak      # 同步文档和记忆
/skill frontend-design # 前端界面设计
```

### 可用技能分类

- **代码理解**: understand, understand-diff, understand-explain, understand-domain, understand-onboard
- **代码质量**: simplify, review, security-review
- **前端设计**: frontend-design, ui-ux-pro-max, baseline-ui
- **自动化测试**: agent-browser, playwright-cli
- **搜索研究**: tavily-search, scrapling-official, find-skills
- **文档处理**: docx, pptx, humanizer-zh
- **系统**: init, neat-freak, syh-docker, loop

## Important Notes

- Frontend proxies API requests to backend via Vite dev server configuration
- Images are stored in MinIO object storage (`aiwardrobe` bucket)
- Image compression is applied on upload (max 1024x1024, PNG format)
- The backend serves both API routes and the built frontend in production
- CI/CD builds multi-platform Docker images (linux/amd64, linux/arm64) pushed to ghcr.io