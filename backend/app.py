import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080"])

KNOWN_HASHES = set()

def load_hashes():
    try:
        with open("/app/data/leaked-sha1.txt", "r") as f:
            for line in f:
                KNOWN_HASHES.add(line.strip().lower())
        print(f"Wczytano {len(KNOWN_HASHES)} hashy z /app/data/leaked-sha1.txt")
    except Exception as e:
        print(f"Błąd ładowania hashy: {e}")

load_hashes()

@app.post("/check")
def check():
    data = request.get_json()
    if not data or "hash" not in data:
        return jsonify({"error": "Brak pola hash"}), 400

    h = data["hash"].lower()

    # Walidacja (Krok 5)
    if not re.fullmatch(r"[0-9a-f]{40}", h):
         return jsonify({"error": "Niepoprawny format hasha"}), 400
    
    # Bezpieczne logowanie (Krok 5)
    print(f"Sprawdzam hash: {h[:5]}...")

    # Logika sprawdzania (Krok 2)
    found = h in KNOWN_HASHES
    return jsonify({"found": found})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
