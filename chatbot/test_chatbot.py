"""
Smart Agriculture Assistant - Automated Chatbot Test Suite
Tests 4 required scenarios:
1. General farming question
2. Context-aware follow-up using disease prediction result
3. Off-topic question rejection
4. Missing API key graceful error handling
"""

import os
import sys
from dotenv import load_dotenv

# Ensure proper stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure root directory is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()

from chatbot.agri_chatbot import AgriChatbot


def test_1_general_farming_question():
    print("\n" + "=" * 65)
    print("TEST 1: GENERAL FARMING QUESTION")
    print("=" * 65)

    bot = AgriChatbot()
    question = "What is the optimal soil pH and temperature for growing wheat?"
    print(f"User: {question}\n")

    response = bot.send_message(question)
    print(f"Assistant:\n{response}\n")

    assert response and len(response) > 20, "Response should not be empty"
    print(">>> TEST 1 RESULT: PASSED (Helpful agricultural advice returned)")
    return response


def test_2_disease_context_followup():
    print("\n" + "=" * 65)
    print("TEST 2: CONTEXT-AWARE FOLLOW-UP (PLANT DISEASE DETECTION)")
    print("=" * 65)

    bot = AgriChatbot()

    # Simulate disease detection prediction result
    print("Step 2A: Simulating disease prediction result...")
    plant = "Apple"
    disease = "Alternaria leaf spot"
    confidence = 94.20
    bot.set_disease_context(plant=plant, disease=disease, confidence=confidence)

    summary = bot.get_context_summary()
    print(f"Context Injected: {summary}\n")

    # Follow-up question without naming the disease explicitly
    question_1 = "How do I treat this disease?"
    print(f"User (Turn 1): {question_1}\n")
    response_1 = bot.send_message(question_1)
    print(f"Assistant (Turn 1):\n{response_1}\n")

    # Multi-turn follow-up
    question_2 = "Are there any organic or non-chemical options for it?"
    print(f"User (Turn 2): {question_2}\n")
    response_2 = bot.send_message(question_2)
    print(f"Assistant (Turn 2):\n{response_2}\n")

    assert "alternaria" in response_1.lower() or "apple" in response_1.lower() or "leaf spot" in response_1.lower(), \
        "Response should incorporate the active disease context"
    print(">>> TEST 2 RESULT: PASSED (Successfully applied disease context & multi-turn dialogue)")
    return response_1, response_2


def test_3_off_topic_rejection():
    print("\n" + "=" * 65)
    print("TEST 3: OFF-TOPIC QUESTION REJECTION")
    print("=" * 65)

    bot = AgriChatbot()
    question = "Can you write a Python function to solve the Two Sum problem?"
    print(f"User: {question}\n")

    response = bot.send_message(question)
    print(f"Assistant:\n{response}\n")

    lower_resp = response.lower()
    assert any(w in lower_resp for w in ["agriculture", "farming", "farm", "crop", "decline", "only"]), \
        "Response should politely decline off-topic question"
    print(">>> TEST 3 RESULT: PASSED (Politely declined non-farming query)")
    return response


def test_4_missing_api_key():
    print("\n" + "=" * 65)
    print("TEST 4: MISSING API KEY ERROR HANDLING")
    print("=" * 65)

    # Initialize chatbot with empty key
    bot = AgriChatbot(api_key="")
    question = "What fertilizer is best for sandy soil?"
    print(f"User: {question}\n")

    response = bot.send_message(question)
    print(f"Assistant:\n{response}\n")

    assert "key is missing" in response.lower() or "gemini_api_key" in response.lower(), \
        "Response should give friendly guidance on missing API key"
    print(">>> TEST 4 RESULT: PASSED (Gracefully handled missing API key without crashing)")
    return response


def run_all_tests():
    print("=================================================================")
    print("     STARTING SMART AGRICULTURE ASSISTANT CHATBOT TEST SUITE     ")
    print("=================================================================")

    results = {}
    try:
        results["test1"] = test_1_general_farming_question()
        results["test2"] = test_2_disease_context_followup()
        results["test3"] = test_3_off_topic_rejection()
        results["test4"] = test_4_missing_api_key()

        print("\n" + "=" * 65)
        print("           ALL 4 CHATBOT TEST SCENARIOS PASSED!           ")
        print("=================================================================\n")
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        raise e


if __name__ == "__main__":
    run_all_tests()
