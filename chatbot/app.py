"""
Smart Agriculture Assistant - Web Application
Streamlit UI combining Crop Recommendation, Plant Disease Detection, and AI Chatbot.
"""

import os
import sys

# Ensure UTF-8 encoding on Windows
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from io import BytesIO
from PIL import Image
import streamlit as st
from dotenv import load_dotenv

# Ensure root directory is accessible for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

from chatbot.agri_chatbot import AgriChatbot
from chatbot.crop_helper import predict_crop_recommendation
from chatbot.disease_helper import get_available_plants, predict_disease


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = AgriChatbot()

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0

    if "crop_result" not in st.session_state:
        st.session_state.crop_result = None

    if "disease_result" not in st.session_state:
        st.session_state.disease_result = None

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []


def render_crop_tab():
    st.header("🌱 Soil & Climate Crop Recommendation")
    st.markdown(
        "Enter your soil nutrients and local climate parameters to discover the most suitable crop."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🧪 Soil Nutrients")
        nitrogen = st.number_input("Nitrogen (N) content (kg/ha)", min_value=0.0, max_value=300.0, value=90.0, step=1.0)
        phosphorus = st.number_input("Phosphorus (P) content (kg/ha)", min_value=0.0, max_value=200.0, value=42.0, step=1.0)
        potassium = st.number_input("Potassium (K) content (kg/ha)", min_value=0.0, max_value=250.0, value=43.0, step=1.0)
        ph = st.number_input("Soil pH level", min_value=1.0, max_value=14.0, value=6.5, step=0.1)

    with col2:
        st.subheader("🌤️ Climate Conditions")
        temperature = st.number_input("Average Temperature (°C)", min_value=-10.0, max_value=60.0, value=20.8, step=0.1)
        humidity = st.number_input("Relative Humidity (%)", min_value=0.0, max_value=100.0, value=82.0, step=1.0)
        rainfall = st.number_input("Rainfall (mm)", min_value=0.0, max_value=1000.0, value=202.0, step=1.0)

    if st.button("🔮 Predict Suitable Crop", type="primary", use_container_width=True):
        with st.spinner("Analyzing soil and climate data..."):
            try:
                crop, confidence = predict_crop_recommendation(
                    nitrogen=nitrogen,
                    phosphorus=phosphorus,
                    potassium=potassium,
                    temperature=temperature,
                    humidity=humidity,
                    ph=ph,
                    rainfall=rainfall
                )

                inputs_dict = {
                    "N": nitrogen,
                    "P": phosphorus,
                    "K": potassium,
                    "temperature": temperature,
                    "humidity": humidity,
                    "ph": ph,
                    "rainfall": rainfall
                }

                st.session_state.crop_result = {
                    "crop": crop,
                    "confidence": confidence,
                    "inputs": inputs_dict
                }

                # Update chatbot active context
                st.session_state.chatbot.set_crop_context(
                    crop=crop,
                    inputs=inputs_dict,
                    confidence=confidence
                )

            except Exception as e:
                st.error(f"Error during crop recommendation: {e}")

    if st.session_state.crop_result:
        res = st.session_state.crop_result
        st.success(f"### 🌾 Recommended Crop: **{res['crop'].capitalize()}**")
        st.metric(label="Model Confidence", value=f"{res['confidence']:.2f}%")

        st.info(
            f"💡 **Chatbot Context Updated!** The chatbot now knows your recommended crop is **{res['crop'].capitalize()}**. "
            "You can head to the **AI Chatbot** tab to ask management and fertilizer questions."
        )


def render_disease_tab():
    st.header("🍃 Plant Leaf Disease Detection")
    st.markdown("Upload an image of a plant leaf to identify plant diseases using deep learning (ResNet50).")

    available_plants = get_available_plants()
    plant_options = {v: k for k, v in available_plants.items()}

    selected_display = st.selectbox(
        "Select Crop / Plant Type:",
        options=list(plant_options.keys()),
        index=0
    )
    dataset_key = plant_options[selected_display]

    uploaded_file = st.file_uploader(
        "Choose a leaf image (JPG, JPEG, PNG):",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        col_img, col_info = st.columns([1, 1])
        with col_img:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Leaf Image", use_container_width=True)

        with col_info:
            if st.button("🔍 Detect Disease", type="primary", use_container_width=True):
                with st.spinner("Running deep learning diagnosis..."):
                    try:
                        predicted_disease, confidence = predict_disease(
                            image_input=uploaded_file,
                            dataset_name=dataset_key
                        )

                        st.session_state.disease_result = {
                            "plant": selected_display,
                            "dataset_key": dataset_key,
                            "disease": predicted_disease,
                            "confidence": confidence
                        }

                        # Update chatbot context
                        st.session_state.chatbot.set_disease_context(
                            plant=selected_display,
                            disease=predicted_disease,
                            confidence=confidence
                        )

                    except Exception as e:
                        st.error(f"Error during disease detection: {e}")

            if st.session_state.disease_result:
                d_res = st.session_state.disease_result
                is_healthy = "healthy" in d_res["disease"].lower()

                if is_healthy:
                    st.success(f"### Status: **{d_res['disease']}**")
                else:
                    st.warning(f"### Detected Disease: **{d_res['disease']}**")

                st.metric(label="Detection Confidence", value=f"{d_res['confidence']:.2f}%")
                st.info(
                    f"💡 **Chatbot Context Updated!** The chatbot is now loaded with this diagnosis: "
                    f"**{d_res['plant']} - {d_res['disease']}**. Head to the **AI Chatbot** tab and ask *'How do I treat this?'*"
                )


def render_chatbot_tab():
    st.header("🤖 AI Agriculture Assistant Chatbot")
    st.markdown(
        "Ask questions about crop care, soil health, irrigation, fertilizers, pests, or follow-up on your predictions."
    )

    # Active Context Banner
    context_summary = st.session_state.chatbot.get_context_summary()
    if context_summary:
        col_ctx, col_clear = st.columns([5, 1])
        with col_ctx:
            st.info(f"📌 **Active Prediction Context:** {context_summary}")
        with col_clear:
            if st.button("❌ Clear Context", use_container_width=True):
                st.session_state.chatbot.clear_context()
                st.session_state.crop_result = None
                st.session_state.disease_result = None
                st.rerun()
    else:
        st.caption("ℹ️ No active prediction context. Run Crop Recommendation or Disease Detection to pass context, or ask general farming questions.")

    # Suggested Prompts
    st.markdown("**Quick Prompts:**")
    prompt_cols = st.columns(4)
    suggested_queries = [
        "How do I improve soil health?",
        "What are the best organic fertilizers?",
        "When should I irrigate wheat?",
        "How to prevent pest outbreaks?"
    ]

    if context_summary:
        if st.session_state.disease_result:
            suggested_queries[0] = "How do I treat this disease?"
            suggested_queries[1] = "Are there organic sprays for this?"
        elif st.session_state.crop_result:
            suggested_queries[0] = "What is the best sowing season for this crop?"
            suggested_queries[1] = "What fertilizer dosage is needed?"

    for idx, col in enumerate(prompt_cols):
        with col:
            if st.button(suggested_queries[idx], key=f"quick_{idx}", use_container_width=True):
                user_msg = suggested_queries[idx]
                with st.spinner("Assistant is typing..."):
                    reply = st.session_state.chatbot.send_message(user_msg)
                st.session_state.chat_messages = st.session_state.chatbot.history.copy()
                st.rerun()

    st.divider()

    # Display Chat History
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chatbot.history:
            st.markdown(
                """
                👋 **Hello, Farmer!** I am your Agriculture Assistant.
                - Ask me anything about crops, soil, water management, fertilizers, or diseases.
                - If you ran a prediction, I already know your results!
                """
            )
        else:
            for msg in st.session_state.chatbot.history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    # Chat Input
    user_input = st.chat_input("Ask a farming question...")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = st.session_state.chatbot.send_message(user_input)
                st.markdown(reply)

        st.session_state.chat_messages = st.session_state.chatbot.history.copy()
        st.rerun()

    # Clear Chat History Button
    if st.session_state.chatbot.history:
        st.write("")
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.chatbot.clear_history()
            st.session_state.chat_messages = []
            st.rerun()


def main():
    st.set_page_config(
        page_title="Smart Agriculture Assistant",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()

    # Sidebar configuration and status
    with st.sidebar:
        st.title("🌾 Smart Agri Assistant")
        st.markdown(
            "An intelligent decision support system for modern agriculture and farming."
        )

        st.subheader("🔑 Gemini API Status")
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "your_gemini_api_key_here":
            st.success("✅ Gemini API Key is configured")
        else:
            st.error("⚠️ GEMINI_API_KEY is not configured in .env")
            st.info("Add your Gemini API key to `.env`:\n`GEMINI_API_KEY=your_key`")

        st.divider()
        st.markdown(
            """
            **Features:**
            - 🌾 **Crop Recommendation**: Soil & climate-based CatBoost model.
            - 🍃 **Disease Detection**: 13 crops using fine-tuned ResNet50.
            - 🤖 **Farmer Chatbot**: Gemini-powered contextual advisor.
            """
        )

    # Main Tab Layout
    tab1, tab2, tab3 = st.tabs([
        "🌱 Crop Recommendation",
        "🍃 Plant Disease Detection",
        "🤖 AI Agriculture Chatbot"
    ])

    with tab1:
        render_crop_tab()

    with tab2:
        render_disease_tab()

    with tab3:
        render_chatbot_tab()


if __name__ == "__main__":
    main()
