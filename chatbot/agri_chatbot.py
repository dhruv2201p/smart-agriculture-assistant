"""
Smart Agriculture Assistant - Core Chatbot Module
Powered by the official Google GenAI SDK (google-genai).
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# Configure logger
logger = logging.getLogger("agri_chatbot")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


SYSTEM_PROMPT = """You are an expert agriculture assistant dedicated to helping farmers and growers.

IMPORTANT RULES & GUIDELINES:
1. TOPIC RESTRICTION: You answer ONLY farming, agronomy, and agriculture-related questions (crops, soil health, irrigation, fertilizers, pests, weed management, plant diseases, seasonal farming calendars, weather impacts on farming).
2. OFF-TOPIC QUESTIONS: For any query unrelated to agriculture (e.g., sports, general trivia, movies, coding, math, general politics, entertainment), you MUST politely decline to answer. Explain that you are an agriculture assistant designed specifically for farming and crop-related questions.
3. HONESTY & SAFETY FIRST: If you do not know the answer or if the information is uncertain, state honestly that you do not know instead of guessing. For critical plant infections, toxic pesticides, or significant economic risks, always recommend consulting a local agricultural extension officer, agronomist, or certified farm advisory service.
4. FARMER-FRIENDLY TONE: Use simple, plain, and actionable language that any farmer can easily understand and put into practice. Avoid unnecessary scientific jargon.
5. CONCISE BY DEFAULT: Keep answers short, direct, and actionable (2-4 brief paragraphs or concise bullet points), unless the user explicitly requests an in-depth breakdown or step-by-step treatment plan.
6. CONTEXT AWARENESS: If an active crop recommendation or plant disease detection result is provided below, treat that result as the primary subject of follow-up questions (such as "how do I treat this?", "what fertilizer should I apply?", or "when should I harvest?")."""


class AgriChatbot:
    """
    Agricultural AI Chatbot using the Gemini API.
    Maintains session history and integrates ML predictions as context.
    """

    DEFAULT_MODELS = [
        "gemini-3.5-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-3.8-flash",
        "gemini-flash-latest"
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize the agriculture chatbot.
        :param api_key: Gemini API Key (reads from GEMINI_API_KEY .env if None).
        :param model_name: Primary model to use (defaults to gemini-3.5-flash-lite).
        """
        # Load API key
        if api_key is not None:
            self.api_key = api_key.strip() if isinstance(api_key, str) else api_key
        else:
            self.api_key = (os.getenv("GEMINI_API_KEY") or "").strip()

        # Model configuration
        self.model_name = model_name or self.DEFAULT_MODELS[0]

        # Conversation history: list of {"role": "user" | "assistant", "content": str}
        self.history: List[Dict[str, str]] = []

        # Active prediction context (crop recommendation or plant disease)
        self.active_context: Dict[str, Any] = {}

        # Client initialization
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize the Google GenAI client if credentials are present."""
        if not GENAI_AVAILABLE:
            logger.warning("google-genai library is not installed.")
            return

        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Error initializing Google GenAI client: {e}")
                self.client = None
        else:
            self.client = None

    def set_crop_context(
        self,
        crop: str,
        inputs: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None
    ):
        """
        Set active context from crop recommendation ML prediction.
        """
        self.active_context = {
            "type": "crop",
            "crop": crop,
            "inputs": inputs or {},
            "confidence": confidence
        }

    def set_disease_context(
        self,
        plant: str,
        disease: str,
        confidence: float
    ):
        """
        Set active context from plant disease detection ML model.
        """
        self.active_context = {
            "type": "disease",
            "plant": plant,
            "disease": disease,
            "confidence": confidence
        }

    def clear_context(self):
        """Clear active prediction context."""
        self.active_context = {}

    def get_context(self) -> Dict[str, Any]:
        """Return the current active context dictionary."""
        return self.active_context

    def get_context_summary(self) -> Optional[str]:
        """Return a human-friendly string summary of the active context."""
        if not self.active_context:
            return None

        ctx_type = self.active_context.get("type")
        if ctx_type == "disease":
            plant = self.active_context.get("plant", "Unknown Plant").capitalize()
            disease = self.active_context.get("disease", "Unknown Condition")
            conf = self.active_context.get("confidence", 0.0)
            return f"[Plant Disease Context] {plant} - {disease} ({conf:.1f}% confidence)"

        if ctx_type == "crop":
            crop = self.active_context.get("crop", "Unknown Crop").capitalize()
            inputs = self.active_context.get("inputs", {})
            parts = []
            if "N" in inputs:
                parts.append(f"N:{inputs['N']}")
            if "P" in inputs:
                parts.append(f"P:{inputs['P']}")
            if "K" in inputs:
                parts.append(f"K:{inputs['K']}")
            if "temperature" in inputs:
                parts.append(f"{inputs['temperature']}C")
            if "humidity" in inputs:
                parts.append(f"{inputs['humidity']}% hum")
            if "ph" in inputs:
                parts.append(f"pH {inputs['ph']}")
            if "rainfall" in inputs:
                parts.append(f"{inputs['rainfall']}mm rain")

            conditions_str = f" [{', '.join(parts)}]" if parts else ""
            return f"[Crop Recommendation Context] {crop}{conditions_str}"

        return "Active context loaded."

    def clear_history(self):
        """Clear conversation history for the current session."""
        self.history = []

    def _build_system_instruction(self) -> str:
        """Construct system instruction with active prediction context."""
        instruction = SYSTEM_PROMPT

        if self.active_context:
            ctx_type = self.active_context.get("type")
            instruction += "\n\n--- CURRENT ACTIVE PREDICTION CONTEXT ---"

            if ctx_type == "disease":
                plant = self.active_context.get("plant", "")
                disease = self.active_context.get("disease", "")
                conf = self.active_context.get("confidence", 0.0)
                instruction += f"""
Plant Type: {plant}
Detected Disease / Status: {disease}
Model Confidence: {conf:.2f}%
Note: The farmer recently ran leaf disease detection. If they ask questions like "how do I treat this?", "what spray to use?", or "how to prevent spread?", provide recommendations specifically for {disease} on {plant}.
"""
            elif ctx_type == "crop":
                crop = self.active_context.get("crop", "")
                inputs = self.active_context.get("inputs", {})
                instruction += f"""
Recommended Crop: {crop}
Farmer's Soil & Weather Parameters:
- Nitrogen (N): {inputs.get('N', 'N/A')}
- Phosphorus (P): {inputs.get('P', 'N/A')}
- Potassium (K): {inputs.get('K', 'N/A')}
- Temperature: {inputs.get('temperature', 'N/A')} °C
- Humidity: {inputs.get('humidity', 'N/A')} %
- Soil pH: {inputs.get('ph', 'N/A')}
- Rainfall: {inputs.get('rainfall', 'N/A')} mm
Note: The farmer recently ran crop recommendation based on these parameters. If they ask about management, sowing dates, soil preparation, or irrigation, refer specifically to {crop}.
"""
            instruction += "-----------------------------------------\n"

        return instruction

    def send_message(self, message: str) -> str:
        """
        Send a user question to the chatbot and return the assistant response.
        Handles errors gracefully and preserves conversation history.
        """
        # Validate message
        if not message or not message.strip():
            return "Please type a farming-related question so I can assist you."

        user_query = message.strip()

        # Check package installation
        if not GENAI_AVAILABLE:
            return (
                "⚠️ The Google GenAI library is not installed. "
                "Please run `pip install google-genai` to activate the chatbot."
            )

        # Check API key
        if not self.api_key:
            return (
                "⚠️ Gemini API key is missing. "
                "Please set your `GEMINI_API_KEY` in the `.env` file to start using the assistant."
            )

        # Re-initialize client if necessary
        if self.client is None:
            self._init_client()
            if self.client is None:
                return (
                    "⚠️ Could not initialize Gemini client. "
                    "Please verify that your `GEMINI_API_KEY` in `.env` is valid."
                )

        # Build system instruction
        system_instruction = self._build_system_instruction()

        # Build history contents for Google GenAI SDK
        chat_history: List[types.Content] = []
        for turn in self.history:
            role = "user" if turn["role"] == "user" else "model"
            chat_history.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=turn["content"])]
                )
            )

        # Prepare model candidates for resilience against temporary outages/quotas
        candidate_models = [self.model_name] + [
            m for m in self.DEFAULT_MODELS if m != self.model_name
        ]

        last_error = None
        assistant_reply = None

        for model_candidate in candidate_models:
            try:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3
                )

                # Use official Chat object for multi-turn dialogue
                chat = self.client.chats.create(
                    model=model_candidate,
                    config=config,
                    history=chat_history
                )

                response = chat.send_message(user_query)

                if response and response.text:
                    assistant_reply = response.text.strip()
                    self.model_name = model_candidate  # Stick with working model
                    break
                else:
                    assistant_reply = (
                        "I received an empty response. Please ask your question again."
                    )
                    break

            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                logger.warning(
                    f"Model {model_candidate} returned error: {e}. Trying fallback if available."
                )
                # If error is invalid API key or permissions, fallback won't help
                if "api_key" in err_str or "unauthenticated" in err_str or "api key not valid" in err_str:
                    return (
                        "⚠️ Invalid Gemini API key. "
                        "Please verify your `GEMINI_API_KEY` in the `.env` file."
                    )
                continue

        if assistant_reply is None:
            # All models failed or rate limited / network failure
            err_msg = str(last_error) if last_error else "Unknown error"
            logger.error(f"Chatbot query failed with all candidate models: {err_msg}")

            if "503" in err_msg or "unavailable" in err_msg.lower():
                return (
                    "⚠️ The AI service is currently experiencing very high demand. "
                    "Please wait a moment and try your question again."
                )
            elif "429" in err_msg or "quota" in err_msg.lower():
                return (
                    "⚠️ Gemini API rate limit reached. "
                    "Please wait a short while before sending another message."
                )
            elif "network" in err_msg.lower() or "connection" in err_msg.lower():
                return (
                    "⚠️ Network connection issue. "
                    "Please check your internet connection and try again."
                )
            else:
                return (
                    f"⚠️ An unexpected error occurred while contacting the AI assistant: {err_msg[:120]}. "
                    "Please try again."
                )

        # Store dialogue in history
        self.history.append({"role": "user", "content": user_query})
        self.history.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply
