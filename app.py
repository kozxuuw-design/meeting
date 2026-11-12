
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import os
import json
import urllib.request
import urllib.parse

app = Flask(__name__)

# Данные Telegram
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


# Открытие сайта
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# Отправка уведомления
@app.route("/api/date", methods=["POST"])
def send_date():
    data = request.get_json(silent=True) or {}

    date = str(data.get("date", ""))
    time = str(data.get("time", ""))
    place = str(data.get("place", "")).strip()

    # Проверяем заполнение
    if not date or not time or not place:
        return jsonify({"error": "Заполните поля"}), 400

    if len(place) > 200:
        return jsonify({"error": "Слишком длинное место"}), 400

    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        datetime.strptime(time, "%H:%M")
    except ValueError:
        return jsonify({"error": "Неверная дата или время"}), 400

    if selected_date < datetime.now().date():
        return jsonify({"error": "Дата уже прошла"}), 400

    if not TOKEN or not CHAT_ID:
        return jsonify({"error": "Telegram не настроен"}), 500

    # Сообщение, которое придёт тебе
    message = (
        "💌 ТЁМА СОГЛАСИЛСЯ НА СВИДАНИЕ! ❤️\n\n"
        f"📅 Дата: {selected_date.strftime('%d.%m.%Y')}\n"
        f"🕒 Время: {time}\n"
        f"📍 Место: {place}\n\n"
        "💗 Подтвердил нашу встречу!\n"
    )

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message
    }).encode("utf-8")

    try:
        telegram_request = urllib.request.Request(
            url,
            data=payload,
            method="POST"
        )

        with urllib.request.urlopen(
            telegram_request,
            timeout=10
        ) as response:
            result = json.load(response)

        if not result.get("ok"):
            raise ValueError("Telegram не подтвердил отправку")

        print("Уведомление отправлено в Telegram!")

        return jsonify({"success": True})

    except Exception:
        app.logger.exception("Ошибка отправки в Telegram")
        return jsonify({"error": "Ошибка отправки"}), 502


if __name__ == "__main__":
    app.run(debug=False)
