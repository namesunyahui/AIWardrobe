# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language Constraint

使用中文回答所有问题。

## Project Overview

AIWardrobe is a full-stack web application for managing clothing items and generating AI-powered outfit recommendations. It consists of a React + Vite frontend and a FastAPI backend, with SQLite for persistence.

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
docker compose up --build -d  # Production build and run
```

## Architecture

### Technology Stack
- **Frontend**: React 19, Vite 7, Tailwind CSS 4, React Router 7, i18next
- **Backend**: FastAPI, Python, SQLite (aiosqlite)
- **AI Services**: Google Gemini, OpenAI-compatible APIs, rembg for background removal

### Directory Structure
```
frontend/          # React SPA (port 5173)
  src/
    pages/        # Route pages: Home, Entry, Wardrobe, ClothesDetail, Outfit, Recommendation
    components/  # UI components
    contexts/    # React contexts (Theme, Upload, Recommendation)
    utils/       # API utilities
backend/          # FastAPI application (port 8000)
  api/           # Route handlers (upload, wardrobe, config, weather, recommendation, horoscope)
  services/      # Business logic (gemini, openai_compatible, recommendation, weather, removebg, segment)
  domain/        # Data models (clothes.py)
  storage/       # Database and config (db.py, config_store.py)
```

### API Structure
| Prefix | Purpose |
|--------|---------|
| `/api/upload` | Upload and process clothing images |
| `/api/wardrobe`, `/api/clothes` | Clothing CRUD operations |
| `/api/config`, `/api/models` | LLM configuration management |
| `/api/weather`, `/api/cities` | Weather data for recommendations |
| `/api/recommendation` | AI outfit recommendations |
| `/api/horoscope` | Daily horoscope (cached) |

### Database Schema
- **clothes**: id, category, item, style/season/usage semantics (JSON), color semantics, description, image_filename, created_at
- **horoscope_record**: Cached horoscope data with LLM reasoning

### Key Configuration
- Backend reads from `backend/.env` for API keys (GEMINI_API_KEY, QWEATHER_API_KEY)
- LLM config persisted to `backend/storage/llm_config.json`
- Database file: `backend/wardrobe.db` (configurable via DB_FILE_PATH)

## Workflow Constraints

### 编码前
- 开始任何编码任务前，使用 `Skill` 工具调用 `karpathy-guidelines` skill

### 编码后
- 编码任务完成后，使用 `Skill` 工具调用 `neat-freak` skill 更新全部文档

## Important Notes

- Frontend proxies API requests to backend via Vite dev server configuration
- Image uploads are stored in `backend/static/uploads/` and served statically
- The backend serves both API routes and the built frontend in production
- CI/CD builds multi-platform Docker images (linux/amd64, linux/arm64) pushed to ghcr.io