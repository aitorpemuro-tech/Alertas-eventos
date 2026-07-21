import os
import json
import requests
from bs4 import BeautifulSoup

# Variables de entorno obtenidas desde los secretos de GitHub
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Web objetivo (ejemplo: Navarra Arena)
URL_TARGET = "https://www.navarraarena.com/es/agenda"
DB_FILE = "eventos_guardados.json"

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

def cargar_eventos():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def guardar_eventos(eventos):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(list(eventos), f, ensure_ascii=False, indent=2)

def buscar_nuevos_eventos():
    conocidos = cargar_eventos()
    
    # Descargar la web
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL_TARGET, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extraer encabezados o elementos de eventos
    elementos = soup.find_all(["h2", "h3"])
    nuevos = set()

    for el in elementos:
        titulo = el.get_text(strip=True)
        # Filtramos textos muy cortos o genéricos
        if len(titulo) > 5 and titulo not in conocidos:
            nuevos.add(titulo)
            
            # Enviar alerta a Telegram
            msg = f"🚨 *¡NUEVO EVENTO CONFIRMADO EN NAVARRA!*\n\n📌 *{titulo}*\n\n🔗 [Ver en la web]({URL_TARGET})"
            enviar_telegram(msg)
            print(f"Notificado: {titulo}")

    if nuevos:
        conocidos.update(nuevos)
        guardar_eventos(conocidos)
    else:
        print("No se encontraron eventos nuevos.")

if __name__ == "__main__":
    buscar_nuevos_eventos()
