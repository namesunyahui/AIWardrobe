<div align="center">

# 👕 AI Smart Wardrobe

[![GitHub Stars](https://img.shields.io/github/stars/leoz9/AIWardrobe?style=social)](https://github.com/leoz9/AIWardrobe/stargazers)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://ghcr.io/leoz9/aiwardrobe)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-20+-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

**Your Personal AI Stylist & Wardrobe Manager**

Upload clothing photos, remove backgrounds automatically, classify garments with AI vision, and get weather-aware outfit recommendations — all in one app.

[English](./README.md) | [简体中文](./README.zh-CN.md) | [日本語](./README.ja.md)

---

<img src="docs/images/screenshot_landing.jpg" width="720" alt="AI Smart Wardrobe Screenshot" />

</div>

## ✨ Features

| Feature | Description |
| :--- | :--- |
| **Smart Upload** | Upload clothing photos, auto-remove backgrounds with `rembg`, analyze category, color, and style via AI vision models |
| **Weather-Based Styling** | Auto-selects based on language: Chinese uses QWeather (fast), Japanese/English uses Open-Meteo, generates outfit suggestions based on real-time weather |
| **Digital Wardrobe** | Browse, search, and manage your clothing in a structured wardrobe view |
| **AI Recommendations** | Supports Gemini and OpenAI-compatible providers for personalized outfit generation |
| **Responsive UI** | Optimized for desktop, tablet, and mobile with a modern Tailwind CSS interface |

## 📸 Screenshots (New UI)

<div align="center">
  <img src="docs/images/screenshot_landing.jpg" width="820" alt="Home / Landing (New UI)" />
</div>

<div align="center">
<table>
<tr>
<td align="center"><img src="docs/images/screenshot_input.jpg" width="280" /><br /><b>New Item Entry</b></td>
<td align="center"><img src="docs/images/screenshot_wardrobe.jpg" width="280" /><br /><b>Wardrobe View</b></td>
</tr>
<tr>
<td align="center"><img src="docs/images/screenshot_recommendation.jpg" width="280" /><br /><b>AI Recommendation</b></td>
<td align="center"><img src="docs/images/screenshot_detail.jpg" width="280" /><br /><b>Clothes Detail</b></td>
</tr>
</table>
</div>

## 🏗️ Tech Stack

<table>
<tr><td><b>Frontend</b></td><td>React + Vite + Tailwind CSS</td></tr>
<tr><td><b>Backend</b></td><td>FastAPI + MySQL</td></tr>
<tr><td><b>AI</b></td><td>Google Gemini / OpenAI-compatible APIs + rembg</td></tr>
<tr><td><b>Deploy</b></td><td>Docker / Docker Compose (amd64 & arm64)</td></tr>
</table>

## 🚀 Getting Started

### Prerequisites

- **Node.js** `v20+` &nbsp;|&nbsp; **Python** `v3.10+`
- [Google Gemini API Key](https://aistudio.google.com/app/apikey) or an OpenAI-compatible API key

### 1. Clone & Configure

```bash
git clone https://github.com/leoz9/AIWardrobe.git
cd AIWardrobe
cp backend/.env.example backend/.env
# Edit backend/.env and fill in your API keys
```

### 2. Install Dependencies

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Frontend
cd frontend && npm install && cd ..
```

### 3. Start

```bash
# One-command start (macOS/Linux)
chmod +x start.sh && ./start.sh

# Windows
start.bat
```

After startup:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

<details>
<summary><b>Manual start (separate terminals)</b></summary>

```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

</details>

## 🐳 Docker Deployment

### Configuration

All configuration is managed via `backend/.env` file, which is automatically bundled into the image:
- MySQL database configuration
- MinIO object storage configuration
- LLM API configuration (model, API key)
- QWeather API configuration
- Initial admin account

### Prerequisites

1. **MySQL Database**: Create an empty database first
```sql
CREATE DATABASE aiwardrobe CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. **MinIO Object Storage**: For image storage (optional)

### Build Image

```bash
# Build image
docker build -t aiwardrobe:latest .

# Package as tar file (for transferring to server)
docker save -o aiwardrobe.tar aiwardrobe:latest
```

### Deploy to Server

```bash
# Option 1: Push to registry (requires docker login first)
docker tag aiwardrobe:latest ghcr.io/namesunyahui/aiwardrobe:latest
docker push ghcr.io/namesunyahui/aiwardrobe:latest

# Option 2: Deploy via tar file
# 1. Upload aiwardrobe.tar to server
# 2. Load image on server
docker load -i aiwardrobe.tar

# 3. Run container (config is bundled in the image)
docker run -d --name aiwardrobe -p 8000:8000 aiwardrobe:latest
```

### Quick Start (Local Build)

```bash
cp backend/.env.example backend/.env
# Edit .env with your API keys and database configuration
docker build -t aiwardrobe:local .
docker run -d --name ai_wardrobe -p 8000:8000 aiwardrobe:local
```

> Note: The `.env` file is bundled into the image with all configurations.

### Using Prebuilt Image

```bash
docker pull ghcr.io/namesunyahui/aiwardrobe:latest
docker run -d --name ai_wardrobe -p 8000:8000 ghcr.io/namesunyahui/aiwardrobe:latest
```

### Docker Compose

```bash
git clone https://github.com/namesunyahui/AIWardrobe.git && cd AIWardrobe
cp backend/.env.example backend/.env  # Edit .env with your API keys and MinIO config
docker compose up --build -d
```

Access at http://localhost:8000 &nbsp;|&nbsp; API docs at http://localhost:8000/docs

Data is persisted in `backend/data` directory, images are stored in MinIO object storage.

## ⭐ Star History

<a href="https://www.star-history.com/#leoz9/AIWardrobe&type=Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=leoz9/AIWardrobe&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=leoz9/AIWardrobe&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=leoz9/AIWardrobe&type=Date" width="860" />
  </picture>
</a>

## 🤝 Contributing

Contributions are welcome! Feel free to open an [Issue](https://github.com/leoz9/AIWardrobe/issues) or submit a [Pull Request](https://github.com/leoz9/AIWardrobe/pulls).

## 📄 License

[MIT](LICENSE) © 2024 leoz9
