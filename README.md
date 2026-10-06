# 🌾 Smart Agriculture Assistant

An AI-powered agricultural decision support system designed to assist farmers and growers with:
1. **🌱 Crop Recommendation**: Machine learning model (CatBoost) predicting suitable crops based on soil nutrients ($N, P, K, pH$) and climate factors ($temperature, humidity, rainfall$).
2. **🍃 Plant Disease Detection**: Deep learning computer vision models (Fine-tuned ResNet50) detecting leaf diseases across 13 major plant varieties.
3. **🤖 Agriculture Chatbot**: Conversational AI assistant powered by Google Gemini (`google-genai` SDK) that answers farming questions, maintains multi-turn session history, and automatically incorporates active crop and disease prediction results as context.

---

## 🚀 Setup & Installation

### 1. Prerequisites & Environment
Ensure you have Python 3.10+ installed. Activate your virtual environment:

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

### 2. Configure Gemini API Key

The chatbot reads the Gemini API key from the `.env` file using the `google-genai` SDK.

1. Create a `.env` file in the project root (or copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```
> **Security Note:** The `.env` file is excluded from Git via `.gitignore`. Never commit your API key.

---

## 💻 Running the Application

### Launch the Web Application (Streamlit)
To start the interactive web application featuring all three tabs (Crop Recommendation, Disease Detection, and AI Chatbot):

```bash
streamlit run app.py
```
*(Alternatively, you can also run `streamlit run chatbot/app.py`)*

Open your browser at `http://localhost:8501`.

---

## 🤖 Chatbot Features & Context Awareness

- **Strict Farming Focus**: The bot answers only agricultural topics (crops, soil, fertilizers, irrigation, pests, plant pathology, seasons). Any off-topic queries are politely declined.
- **Context Injection**: When you run a Crop Recommendation or Disease Detection in the UI, the result (crop name, detected disease, confidence percentage, soil parameters) is passed directly to the chatbot. You can immediately ask follow-up questions like:
  - *"How do I treat this disease?"*
  - *"What organic sprays can I use for this?"*
  - *"When is the best time to sow this crop?"*
- **Multi-Turn Dialogue**: Maintains conversation history throughout the session for continuous back-and-forth guidance.
- **Resilient Error Handling**: Safely handles missing API keys, rate limits, and network issues with clear, friendly messages without crashing.

---

## 🧪 Running Automated Tests

To verify the chatbot functionality, run the automated test suite:

```bash
python chatbot/test_chatbot.py
```

This verifies:
1. **General Farming Question** (Wheat soil pH and temperature requirements)
2. **Context-Aware Follow-Up** (Disease diagnosis follow-up and organic remedy queries)
3. **Off-Topic Rejection** (Declining non-farming questions politely)
4. **Missing API Key Handling** (Graceful error messaging without application crashes)
