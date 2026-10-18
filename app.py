import os
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

NTFY_TOPIC = os.getenv("NTFY_TOPIC")
NTFY_URL = os.getenv("NTFY_URL", "https://ntfy.sh").rstrip("/")
ICON_URL = os.getenv(
    "ICON_URL",
    "https://raw.githubusercontent.com/sct/overseerr/develop/public/os_logo_square.png",
)
PORT = int(os.getenv("PORT", 5001))

# Dictionnaire de configuration des notifications Seerr
EVENT_MAPPING = {
    "MEDIA_PENDING": {
        "title": "Demande en attente",
        "tag": "hourglass_flowing_sand",
        "format": lambda user, title, type_str: f"{user} a demandé {type_str} : {title} (en attente de validation).",
    },
    "MEDIA_AUTO_APPROVED": {
        "title": "Demande auto-approuvée",
        "tag": "robot,white_check_mark",
        "format": lambda user, title, type_str: f"{type_str} {title} demandé par {user} a été validé automatiquement.",
    },
    "MEDIA_APPROVED": {
        "title": "Demande validée",
        "tag": "white_check_mark",
        "format": lambda user, title, type_str: f"La demande de {user} pour {type_str} {title} a été approuvée.",
    },
    "MEDIA_DECLINED": {
        "title": "Demande refusée",
        "tag": "x",
        "format": lambda user, title, type_str: f"La demande de {user} pour {type_str} {title} a été refusée.",
    },
    "MEDIA_AVAILABLE": {
        "title": "Média disponible",
        "tag": "tada",
        "format": lambda user, title, type_str: f"{type_str} {title} demandé par {user} est maintenant disponible !",
    },
    "MEDIA_FAILED": {
        "title": "Échec d'ajout",
        "tag": "warning,",
        "format": lambda user, title, type_str: f"Échec de l'ajout de {type_str} {title} dans Radarr/Sonarr.",
    },
}


@app.route("/webhook", methods=["POST"])
def webhook():
    # Parsing du JSON avec gestion des cas particuliers d'encodage
    data = request.get_json(force=True, silent=True) or {}
    if not data:
        return jsonify({"status": "error", "message": "No JSON payload"}), 400

    notification_type = str(data.get("notification_type", "")).upper()

    # Filtre sur les événements de demandes pris en charge
    if notification_type not in EVENT_MAPPING:
        return (
            jsonify(
                {
                    "status": "ignored",
                    "message": f"Event '{notification_type}' non pris en charge",
                }
            ),
            200,
        )

    # Extraction des données de la demande
    subject = data.get("subject", "Titre inconnu")
    poster_image = data.get("image")

    request_info = data.get("request") or {}
    requested_by = request_info.get("requestedBy_username") or "Un utilisateur"

    media_info = data.get("media") or {}
    media_type = media_info.get("media_type", "movie")
    type_str = "le film" if media_type == "movie" else "la série"

    # Construction du message et des en-têtes
    config = EVENT_MAPPING[notification_type]
    notification_title = config["title"]
    notification_message = config["format"](requested_by, subject, type_str)

    headers = {
        "Title": notification_title.encode("utf-8"),
        "Tags": config["tag"],
        "Icon": ICON_URL,
    }

    # Reconstitution de l'URL de l'affiche si Seerr renvoie un chemin relatif TMDb
    if poster_image:
        if poster_image.startswith("/"):
            poster_image = f"https://image.tmdb.org/t/p/w600_and_h900_bestv2{poster_image}"
        headers["Attach"] = poster_image

    target_url = f"{NTFY_URL}/{NTFY_TOPIC}"
    response = requests.post(
        target_url, data=notification_message.encode("utf-8"), headers=headers
    )

    if response.status_code == 200:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "code": response.status_code}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)