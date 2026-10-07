# 🌾 Smart Agriculture Assistant

An AI-powered decision support system for farmers. It recommends the best crop for given soil and climate conditions, diagnoses plant leaf diseases from photos, and answers farming questions through an AI chatbot.

**🔗 Live Demo:** [https://smart-agriculture-assistant-livid.vercel.app](https://smart-agriculture-assistant-livid.vercel.app)
**⚙️ Backend API:** [https://smart-agriculture-backend-4j3w.onrender.com](https://smart-agriculture-backend-4j3w.onrender.com) (interactive docs at `/docs`)

> ⏳ **Note:** The backend is hosted on a free tier and sleeps when idle. The first request after a break can take about a minute. The first disease prediction for each crop is also slower because the model is loaded on demand.

---

## ✨ Features

| Feature | Description | Technology |
|---|---|---|
| 🌱 **Crop Recommendation** | Suggests the most suitable crop from soil nutrients (N, P, K), pH, temperature, humidity and rainfall | CatBoost classifier |
| 🍃 **Plant Disease Detection** | Upload a leaf photo, select the plant, and get the disease diagnosis with a confidence score | Fine-tuned ResNet50 (13 crops, 33 models) |
| 🤖 **Agriculture Chatbot** | Answers questions on cultivation, soil health, irrigation, fertilizers and disease treatment; can use the latest prediction as context | Google Gemini API |

Works on both desktop and mobile screens.

---

## 🏗️ Architecture

```
┌────────────────────┐   HTTPS / JSON    ┌──────────────────────────┐
│  Frontend (React)  │ ────────────────► │  Backend (FastAPI)       │
│  Hosted on Vercel  │ ◄──────────────── │  Hosted on Render        │
└────────────────────┘                   │  • CatBoost crop model   │
                                         │  • ResNet50 disease models│
                                         │  • Gemini chatbot        │
                                         └──────────────────────────┘
```

---

## 📁 Project Structure

```
Smart_Agriculture_Assistant/
├── backend/                 # FastAPI server (deployed on Render)
│   ├── main.py              # App setup, CORS, and API routes
│   ├── crop.py              # Crop recommendation logic
│   ├── disease.py           # Disease detection (lazy-loads models)
│   ├── chatbot.py           # Gemini chatbot logic
│   ├── models/              # Trained models and label encoders
│   ├── requirements.txt
│   ├── runtime.txt          # Python version for Render
│   └── .env.example
│
├── frontend/                # React + Vite app (deployed on Vercel)
│   ├── src/
│   │   ├── App.jsx          # Crop, Disease and Chatbot tabs
│   │   ├── api.js           # API calls (uses VITE_API_URL)
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── .env.example
│
├── ml/                      # Research and training (not deployed)
│   ├── notebooks/           # EDA and model evaluation notebooks
│   ├── preprocessing/       # Data preprocessing scripts
│   ├── reports/             # Metrics and plots
│   └── data/                # Datasets (git-ignored)
│
├── .gitignore
└── README.md
```

> Adjust this tree if your final folder layout differs.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Backend status check |
| POST | `/api/crop/predict` | Soil and climate values → recommended crop and confidence |
| POST | `/api/disease/predict` | Leaf image and crop name → disease and confidence |
| POST | `/api/chat` | Message, history and optional prediction context → chatbot reply |

Interactive API docs are available at `/docs` on the backend URL.

---

## 🚀 Run Locally

### Prerequisites
- Python 3.11
- Node.js 18 or newer
- A [Gemini API key](https://aistudio.google.com/) (free tier available)

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd Smart_Agriculture_Assistant
```

### 2. Backend
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env        # then edit .env and add your keys
uvicorn main:app --reload --port 8000
```
The API runs at `http://localhost:8000` (docs at `http://localhost:8000/docs`).

### 3. Frontend
```bash
cd frontend
npm install
cp .env.example .env        # set VITE_API_URL=http://localhost:8000
npm run dev
```
The app runs at `http://localhost:5173`.

---

## 🔐 Environment Variables

**Backend (`backend/.env`)**

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key for the chatbot |
| `CORS_ORIGINS` | Allowed frontend URLs, comma-separated (e.g. `http://localhost:5173,https://smart-agriculture-assistant-livid.vercel.app`) |
| `HF_REPO_ID` | Hugging Face repository that stores the disease model files |
| `MODEL_BASE_URL` | Alternative direct URL for model downloads (optional) |

**Frontend (`frontend/.env`)**

| Variable | Purpose |
|---|---|
| `VITE_API_URL` | Backend URL, with no trailing slash |

> Never commit `.env` files or API keys to GitHub.

---

## ☁️ Deployment

### Backend on Render
1. Create a new **Web Service** from your GitHub repository and set the root directory to `backend`.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Set Python to 3.11 (via `runtime.txt` or the `PYTHON_VERSION` variable).
5. Add the backend environment variables listed above.

### Frontend on Vercel
1. Import the repository and set the root directory to `frontend`.
2. Framework preset: **Vite**.
3. Add `VITE_API_URL` with your Render backend URL.
4. Deploy, then add the Vercel URL to `CORS_ORIGINS` on Render and redeploy the backend.

### Model files
The disease models (`.keras`, about 200 MB each) are too large for GitHub. They are stored on Hugging Face Hub and downloaded on first use, then cached on the server.

---

## 🧠 Models and Data

- **Crop recommendation:** tabular soil and climate dataset with 7 input features. Several classifiers were compared, and CatBoost was selected. See `ml/notebooks/` for the evaluation.
- **Disease detection:** leaf image dataset organized by plant and disease. A ResNet50 model was fine-tuned for each crop (13 crops).
- **Evaluation:** metrics, confusion matrices and comparison plots are in `ml/reports/` and `ml/notebooks/`.

<!-- Add your final numbers here, for example: -->
<!-- | Model | Accuracy | -->
<!-- |---|---| -->
<!-- | CatBoost (crop) | xx% | -->
<!-- | ResNet50 (disease) | xx% | -->

---

## 📸 Screenshots

<!-- Add screenshots to a docs/ or screenshots/ folder and link them here -->
<!-- ![Crop Recommendation](screenshots/crop.png) -->
<!-- ![Disease Detection](screenshots/disease.png) -->
<!-- ![Chatbot](screenshots/chatbot.png) -->

---

## ⚠️ Limitations

- Predictions are decision support, not a replacement for expert advice. For serious crop or disease problems, consult a local agricultural officer.
- Disease detection works best on clear, well-lit photos of a single leaf, for the supported crops only.
- The chatbot uses a general-purpose language model and can make mistakes.
- Free-tier hosting has limited memory and cold-start delays.

---

## 🛠️ Tech Stack

**Frontend:** React, Vite
**Backend:** Python, FastAPI, Uvicorn
**ML / AI:** CatBoost, TensorFlow / Keras (ResNet50), scikit-learn, Google Gemini (google-genai)
**Hosting:** Vercel (frontend), Render (backend), Hugging Face Hub (model storage)

---

## 👤 Author

**Your Name**
Your college / department · Your email or LinkedIn

---

## 📄 License

Add your license here (for example, MIT) or remove this section.
