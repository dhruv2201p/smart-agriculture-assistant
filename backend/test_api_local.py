"""
Local API Verification Script
Tests all FastAPI endpoints for the Smart Agriculture Assistant backend.
"""

import sys
import io
import time
import requests
from PIL import Image

# Force UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000"


def wait_for_server(max_retries=15):
    print("Connecting to backend server at", BASE_URL)
    for i in range(max_retries):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=3)
            if r.status_code == 200:
                print("Server online!\n")
                return True
        except Exception:
            time.sleep(1)
    print("Could not connect to server.")
    return False


def test_health():
    print("=" * 60)
    print("TEST 1: GET /health")
    print("=" * 60)
    res = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.json()}\n")
    assert res.status_code == 200
    assert res.json().get("status") == "ok"
    print(">>> TEST 1 RESULT: PASSED\n")


def test_crop_prediction():
    print("=" * 60)
    print("TEST 2: POST /api/crop/predict")
    print("=" * 60)
    payload = {
        "nitrogen": 90,
        "phosphorus": 42,
        "potassium": 43,
        "temperature": 20.8,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.0
    }
    print(f"Payload: {payload}")
    res = requests.post(f"{BASE_URL}/api/crop/predict", json=payload)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.json()}\n")
    assert res.status_code == 200
    data = res.json().get("data", {})
    assert "recommended_crop" in data
    print(f">>> Recommended Crop: {data['recommended_crop']} ({data['confidence']}%)")
    print(">>> TEST 2 RESULT: PASSED\n")
    return data


def test_disease_crops_list():
    print("=" * 60)
    print("TEST 3: GET /api/disease/crops")
    print("=" * 60)
    res = requests.get(f"{BASE_URL}/api/disease/crops")
    print(f"Status Code: {res.status_code}")
    crops = res.json().get("crops", [])
    print(f"Supported Crops ({len(crops)}): {[c['name'] for c in crops]}\n")
    assert res.status_code == 200
    assert len(crops) == 13
    print(">>> TEST 3 RESULT: PASSED\n")


def test_disease_prediction():
    print("=" * 60)
    print("TEST 4: POST /api/disease/predict")
    print("=" * 60)

    # Create synthetic leaf image
    img = Image.new("RGB", (224, 224), color=(70, 140, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    files = {"file": ("leaf.jpg", buf, "image/jpeg")}
    data = {"crop_name": "apple"}

    print("Sending leaf image with crop_name='apple'...")
    res = requests.post(f"{BASE_URL}/api/disease/predict", files=files, data=data)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.json()}\n")
    assert res.status_code == 200
    pred = res.json().get("data", {})
    assert "disease" in pred
    print(f">>> Detected: {pred['plant']} - {pred['disease']} ({pred['confidence']}%)")
    print(">>> TEST 4 RESULT: PASSED\n")
    return pred


def test_chat_general():
    print("=" * 60)
    print("TEST 5: POST /api/chat (General Farming Question)")
    print("=" * 60)
    payload = {
        "message": "What is the optimal soil pH for growing wheat?",
        "history": []
    }
    print(f"User: {payload['message']}")
    res = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"Status Code: {res.status_code}")
    reply = res.json().get("reply", "")
    print(f"Reply:\n{reply}\n")
    assert res.status_code == 200
    assert len(reply) > 20
    print(">>> TEST 5 RESULT: PASSED\n")


def test_chat_with_context():
    print("=" * 60)
    print("TEST 6: POST /api/chat (With Disease Prediction Context)")
    print("=" * 60)
    context = {
        "type": "disease",
        "plant": "Apple",
        "disease": "Alternaria leaf spot",
        "confidence": 94.2
    }
    payload = {
        "message": "How do I treat this disease?",
        "history": [],
        "context": context
    }
    print(f"Context: {context}")
    print(f"User: {payload['message']}")
    res = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"Status Code: {res.status_code}")
    reply = res.json().get("reply", "")
    print(f"Reply:\n{reply}\n")
    assert res.status_code == 200
    assert any(term in reply.lower() for term in ["alternaria", "apple", "leaf spot", "fungicide"])
    print(">>> TEST 6 RESULT: PASSED\n")


def test_chat_off_topic():
    print("=" * 60)
    print("TEST 7: POST /api/chat (Off-Topic Question Decline)")
    print("=" * 60)
    payload = {
        "message": "Who won the 2022 World Cup?",
        "history": []
    }
    print(f"User: {payload['message']}")
    res = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"Status Code: {res.status_code}")
    reply = res.json().get("reply", "")
    print(f"Reply:\n{reply}\n")
    assert res.status_code == 200
    assert any(term in reply.lower() for term in ["agriculture", "farming", "farm", "crop", "only"])
    print(">>> TEST 7 RESULT: PASSED\n")


def run_all():
    print("============================================================")
    print("     STARTING SMART AGRICULTURE BACKEND API VERIFICATION     ")
    print("============================================================\n")

    if not wait_for_server():
        sys.exit(1)

    test_health()
    test_crop_prediction()
    test_disease_crops_list()
    test_disease_prediction()
    test_chat_general()
    test_chat_with_context()
    test_chat_off_topic()

    print("============================================================")
    print("           ALL BACKEND API ENDPOINTS VERIFIED!              ")
    print("============================================================\n")


if __name__ == "__main__":
    run_all()
