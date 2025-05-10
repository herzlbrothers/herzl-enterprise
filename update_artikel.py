import json
from datetime import datetime
import os

# 🔧 Artikel generieren (später durch GPT ersetzen)
def generiere_artikel():
    return {
        "id": f"artikel_{int(datetime.now().timestamp())}",
        "title": "Platzhalter: Neuer KI-Artikel",
        "content": "Dieser Artikel wurde automatisch erstellt. Bald kommt hier echter Content per GPT.",
        "kategorie": "KI",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

# 🔧 Datei-Pfad zum Artikel-Speicher
ARTIKEL_PATH = os.path.join("data", "artikel.json")

# 🔃 Artikeldatei laden oder leere Liste erzeugen
if os.path.exists(ARTIKEL_PATH):
    with open(ARTIKEL_PATH, "r", encoding="utf-8") as f:
        artikel_liste = json.load(f)
else:
    artikel_liste = []

# 🆕 Neuen Artikel anhängen (an erster Stelle)
artikel_liste.insert(0, generiere_artikel())

# 💾 Datei aktualisieren
with open(ARTIKEL_PATH, "w", encoding="utf-8") as f:
    json.dump(artikel_liste, f, indent=2, ensure_ascii=False)

print("✅ Neuer Platzhalter-Artikel hinzugefügt.")
