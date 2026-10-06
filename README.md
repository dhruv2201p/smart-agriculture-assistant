# 🌾 Smart Agriculture Assistant

A full-stack, AI-driven agricultural decision support platform separated into a **FastAPI Backend** and a **React + Vite Frontend**, with research/training artifacts stored in `ml/`.

---

## 🏛️ Project Architecture

```text
Smart_Agriculture_Assistant/
├── backend/                  # 🚀 FastAPI Backend (Deploy to Render)
│   ├── main.py               # REST API endpoints, CORS, health check
│   ├── crop.py               # CatBoost crop recommendation inference
│   ├── disease.py            # Lazy-loaded ResNet50 disease diagnosis + on-demand downloader
│   ├── chatbot.py            # Gemini agriculture assistant (google-genai SDK)
│   ├── models/               # Model weights, scalers, and label encoders
│   ├── requirements.txt      # Backend Python dependencies
│   ├── runtime.txt           # Python 3.11.9 for Render compatibility
│   ├── render.yaml           # Render deployment blueprint
│   └── .env.example          # Backend environment variables template
│
├── frontend/                 # 🌐 React + Vite Frontend (Deploy to Vercel)
│   ├── src/
│   │   ├── App.jsx           # Main UI with Crop, Disease, and Chatbot tabs
│   │   ├── api.js            # API client calling VITE_API_URL
│   │   ├── main.jsx          # React entrypoint
│   │   └── index.css         # Styling
│   ├── index.html            # HTML shell
│   ├── package.json          # Dependencies and build scripts
│   ├── vite.config.js        # Vite build configuration
│   ├── vercel.json           # Vercel SPA routing rewrites
│   └── .env.example          # Frontend environment variables template
│
├── ml/                       # 🔬 Research, Training & Data (NOT deployed)
│   ├── notebooks/            # Jupyter notebooks (EDA, Model Evaluation)
│   ├── preprocessing/        # Dataset preprocessing scripts
│   ├── prediction/           # Legacy prediction scripts kept for reference
│   ├── reports/              # Model evaluation metrics & confusion matrices
│   └── data/                 # Raw datasets (32GB local leaf images)
│
├── .gitignore                # Protects secrets, cache, node_modules, and large weights
└── README.md                 # Setup, local run, and deployment documentation
```

---

## 💻 Local Development Setup

### 1. Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **Node.js 18+** & npm

---

### 2. Backend Setup & Run

1. Open a terminal and navigate to `backend/`:
   ```bash
   cd backend
   ```

2. Activate your virtual environment:
   ```bash
   # Windows
   ..\.venv\Scripts\activate

   # macOS / Linux
   source ../.venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in `backend/` (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   Add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   PORT=8000
   ```

5. Start the FastAPI development server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The backend API will be live at `http://localhost:8000`. You can inspect the interactive documentation at `http://localhost:8000/docs`.

---

### 3. Frontend Setup & Run

1. Open a separate terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in `frontend/` (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   Set the API URL:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   Open your browser at `http://localhost:5173`.

---

## ☁️ Production Deployment Guide

### Deploy Backend on Render

1. **Push your code to GitHub**.
2. Log in to [Render Dashboard](https://dashboard.render.com/) and click **New +** → **Web Service**.
3. Connect your GitHub repository `smart-agriculture-assistant`.
4. Configure the settings:
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.11.9`
   - `GEMINI_API_KEY`: *(Your Google Gemini API key)*
   - `CORS_ORIGINS`: `*` *(or your Vercel frontend URL once deployed)*
   - `HF_REPO_ID`: *(Optional Hugging Face repo if storing large `.keras` models online)*
6. Click **Deploy Web Service**. Your backend URL will be e.g. `https://smart-agriculture-backend.onrender.com`.

---

### Deploy Frontend on Vercel

1. Log in to [Vercel Dashboard](https://vercel.com/) and click **Add New...** → **Project**.
2. Select your repository `smart-agriculture-assistant`.
3. In the project configuration:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click *Edit* and select **`frontend`**
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Under **Environment Variables**, add:
   - `VITE_API_URL`: `https://smart-agriculture-backend.onrender.com` *(your live Render backend URL)*
5. Click **Deploy**. Vercel will build and provide your live frontend link.

---

## 📦 How to Store Large `.keras` Models on Hugging Face (Optional)

GitHub has a 100MB file limit. While `models/crop_model.pkl` is small enough to commit, the 13 deep-learning `.keras` files (~200MB each) can be hosted for free on Hugging Face:

1. Create a free account on [Hugging Face](https://huggingface.co/) and create a new public Model repo: e.g. `your-username/smart-agriculture-models`.
2. Upload the `.keras` files to a `disease/` folder inside that repo:
   ```bash
   pip install huggingface_hub
   python -c "from huggingface_hub import HfApi; api = HfApi(); api.upload_folder(folder_path='backend/models/disease', repo_id='your-username/smart-agriculture-models', path_in_repo='disease', repo_type='model')"
   ```
3. Set the environment variable on Render:
   ```env
   HF_REPO_ID=your-username/smart-agriculture-models
   ```
4. The backend will automatically download missing `.keras` files on demand and cache them.

---

## 🧪 Testing the API Endpoints

Once the backend is running, verify with `curl` or Python:

- **Health Check**:
  ```bash
  curl http://localhost:8000/health
  ```
- **Crop Recommendation**:
  ```bash
  curl -X POST http://localhost:8000/api/crop/predict \
    -H "Content-Type: application/json" \
    -d '{"nitrogen": 90, "phosphorus": 42, "potassium": 43, "temperature": 20.8, "humidity": 82, "ph": 6.5, "rainfall": 202}'
  ```
- **Agriculture Chatbot**:
  ```bash
  curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "What is the best fertilizer for rice?", "history": []}'
  ```
