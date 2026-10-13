# 🌾 Smart Agriculture Assistant

An AI-powered decision support system for modern agronomists and farmers. It recommends the optimal crop for given soil and climate conditions, accurately diagnoses foliar plant leaf diseases from photos, provides curated agronomic treatment advice, and answers agricultural inquiries through an AI chatbot.

**🔗 Live Demo:** [https://smart-agriculture-assistant-livid.vercel.app](https://smart-agriculture-assistant-livid.vercel.app)  
**⚙️ Backend API:** [https://smart-agriculture-backend-4j3w.onrender.com](https://smart-agriculture-backend-4j3w.onrender.com) (interactive docs at `/docs`)

> ⏳ **Free Tier Cold-Starts:** The backend is hosted on Render free tier (512 MB RAM) and sleeps when idle. The first request after an idle period takes ~45–60 seconds to wake up. Individual disease models (~210 MB) are lazy-loaded into memory on demand.

---

## ✨ Features

| Feature | Description | Technology |
|---|---|---|
| 🌱 **Crop Recommendation** | Recommends optimal crop based on soil nutrients (N, P, K), pH, temperature, humidity, and rainfall | CatBoost classifier with standard scaling |
| 🍃 **Plant Disease Detection** | Upload leaf photo to diagnose foliar diseases with top-3 candidates, confidence thresholding, and treatment remedies | Fine-tuned ResNet50 (13 crops, 33 models, /255.0 normalization) |
| 🤖 **Agriculture Chatbot** | Farm-only advisory for irrigation, fertilizers, pests, and disease management; uses active prediction as context | Google Gemini API (google-genai) |
| ⚡ **Client-Side Optimization** | Automatic canvas image compression to 512px before upload; shrinks 10 MB smartphone photos to ~80 KB | HTML5 Canvas + Web API |

Works seamlessly on both desktop and mobile devices.

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐       HTTPS / JSON       ┌─────────────────────────────────────┐
│       Frontend (React + Vite)   │ ───────────────────────► │          Backend (FastAPI)          │
│       Hosted on Vercel          │ ◄─────────────────────── │          Hosted on Render           │
│  • Canvas Client-Side Resizing  │                          │  • CatBoost crop recommendation     │
│  • Instant UI & Warmup States   │                          │  • ResNet50 disease classification  │
│  • Top-3 Predictions & Remedies │                          │  • Gemini farming-only chatbot      │
└─────────────────────────────────┘                          └─────────────────────────────────────┘
```

> **Why Frontend on Vercel & Backend on Render?**  
> Vercel Serverless Functions have a hard 250 MB unzipped limit and a 10s execution timeout. TensorFlow alone is >400 MB and deep learning model weights are ~210 MB each. Therefore, the backend runs as a persistent service on Render, while the lightweight static React frontend builds on Vercel.

---

## 📁 Project Structure

```
Smart_Agriculture_Assistant/
├── backend/                 # FastAPI server (deployed on Render)
│   ├── main.py              # App setup, CORS, endpoints (/health, /api/*)
│   ├── crop.py              # Crop recommendation logic (CatBoost)
│   ├── disease.py           # Disease detection (ResNet50, lazy-loader, /255.0 norm)
│   ├── chatbot.py           # Gemini chatbot service with prediction context
│   ├── test_api_local.py    # Local API endpoint verification test
│   ├── models/              # Trained models and label encoders
│   ├── requirements.txt     # Pinned backend dependencies
│   ├── render.yaml          # Render service deployment blueprint
│   └── runtime.txt          # Python 3.11.9 runtime for Render
│
├── frontend/                # React + Vite application (deployed on Vercel)
│   ├── src/
│   │   ├── App.jsx          # Root container with Header and navigation
│   │   ├── api.js           # API client (checkHealth, predictDisease, etc.)
│   │   ├── components/      # CropTab, DiseaseTab, ChatTab, ResultCard
│   │   └── index.css        # Clean Agriculture design tokens
│   ├── package.json
│   └── vite.config.js
│
├── ml/                      # Research, preprocessing, and notebooks
│   ├── notebooks/           # Model training and evaluation
│   ├── preprocessing/       # Dataset stratified splitting & LabelEncoders
│   └── prediction/          # Offline CLI prediction scripts
│
├── requirements.txt         # Root requirements mirror for build tools
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Overall backend health and subsystem readiness |
| `GET` | `/api/disease/health` | Diagnostic status for disease detection models & memory |
| `GET` | `/api/disease/crops` | List of all 13 supported crop species |
| `POST` | `/api/crop/predict` | Soil and climate metrics → recommended crop & confidence |
| `POST` | `/api/disease/predict` | Leaf image + crop key → diagnosis, top-3 candidates, treatment |
| `POST` | `/api/chat` | Farming question + history + context → agronomic answer |

Interactive OpenAPI documentation is live at `/docs` on the backend server.

---

## 🚀 Run Locally

### Prerequisites
- Python 3.11
- Node.js 18 or newer
- A [Gemini API key](https://aistudio.google.com/)

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd Smart_Agriculture_Assistant
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env        # edit .env and insert GEMINI_API_KEY
uvicorn main:app --reload --port 8000
```
Backend API will be running at `http://127.0.0.1:8000`.

### 3. Frontend Setup
```bash
cd ../frontend
npm install
cp .env.example .env        # set VITE_API_URL=http://localhost:8000
npm run dev
```
Frontend will be available at `http://localhost:5173`.

### 4. Application Runner (Single Command)
From the project root:
```bash
python app.py
```
This automatically launches both the backend on port 8000 and the Vite frontend on port 5173.

---

## 🔐 Environment Variables

**Backend (`backend/.env`)**

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key for chatbot | *(Required for chat)* |
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) | `http://localhost:5173,http://127.0.0.1:5173` |
| `HF_REPO_ID` | Hugging Face repository for model downloads | `DhruvKatharotiya/smart-agriculture-models` |
| `MODEL_BASE_URL` | Optional direct CDN URL fallback | `None` |
| `DISEASE_CONFIDENCE_THRESHOLD` | Threshold below which diagnosis is marked Uncertain | `0.60` |
| `MAX_IMAGE_SIZE_BYTES` | Maximum image upload size | `10485760` (10 MB) |

**Frontend (`frontend/.env`)**

| Variable | Description | Example |
|---|---|---|
| `VITE_API_URL` | Backend server URL (no trailing slash) | `https://smart-agriculture-backend-4j3w.onrender.com` |

---

## ☁️ Deployment

### 1. Backend on Render
1. Create a new **Web Service** on Render and select your GitHub repository.
2. Root Directory: `backend`
3. Environment: `Python 3` (Python 3.11.9)
4. Build Command:
   ```bash
   pip install -r requirements.txt
   ```
5. Start Command:
   ```bash
   gunicorn -w 1 -k uvicorn.workers.UvicornWorker -t 300 --graceful-timeout 300 --bind 0.0.0.0:$PORT main:app
   ```
   *(Why `-w 1` and `-t 300`? Using 1 worker prevents loading duplicate 210 MB models into Render's 512 MB RAM limit. A 300s timeout prevents premature worker restarts while downloading model weights on cold starts).*
6. Add Environment Variables:
   - `GEMINI_API_KEY` = your secret Gemini key
   - `CORS_ORIGINS` = `*` (or your Vercel frontend URL)
   - `HF_REPO_ID` = `DhruvKatharotiya/smart-agriculture-models`

### 2. Frontend on Vercel
1. Import the repository on Vercel.
2. Root Directory: `frontend`
3. Framework Preset: **Vite**
4. Environment Variables:
   - `VITE_API_URL` = `https://smart-agriculture-backend-4j3w.onrender.com`
5. Deploy.

---

## 🧪 Verification & Testing

To test the entire pipeline locally:
```bash
# In the repository root with virtual environment activated:
python backend/test_api_local.py
```
This tests:
1. `GET /health` and `GET /api/disease/health`
2. `POST /api/crop/predict` with sample soil parameters
3. `POST /api/disease/predict` with leaf images (verifying top-3 predictions and remedies)
4. `POST /api/chat` with and without disease context

---

## 🛠️ Tech Stack

- **Frontend:** React, Vite, Lucide Icons, Vanilla CSS Design System
- **Backend:** Python 3.11, FastAPI, Uvicorn, Gunicorn
- **Machine Learning:** TensorFlow/Keras 2.x/3.x (ResNet50), CatBoost, Scikit-Learn, NumPy, Pillow
- **AI Chatbot:** Google GenAI SDK (`google-genai`), Gemini Models
- **Cloud Hosting:** Vercel (Frontend), Render (Backend), Hugging Face Hub (Model storage)
