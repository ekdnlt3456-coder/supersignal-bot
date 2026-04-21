from flask import Flask, request, jsonify
import requests
from datetime import datetime
import json
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID        = os.environ.get("CHAT_ID", "")

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        print(f"[✅ 전송 성공] {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"[❌ 전송 실패] {e}")

def build_message(data: dict) -> str:
    signal  = data.get("signal", "")
    ticker  = data.get("ticker", "")
    price   = float(data.get("price", 0))
    tf      = data.get("interval", "")
    time_   = data.get("time", datetime.now().strftime("%Y-%m-%d %H:%M"))

    if signal == "매수":
        stop  = round(price * 0.99, 2)
        tp1   = round(price * 1.01, 2)
        tp2   = round(price * 1.02, 2)
        tp3   = round(price * 1.03, 2)
        return (
            f"🚀 매수 신호 발생 🚀\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📌 종목: <b>{ticker}</b>\n"
            f"⏱ 타임프레임: {tf}\n"
            f"💰 진입가: <b>{price}</b>\n"
            f"🛑 손절가: <b>{stop}</b>\n"
            f"🎯 익절 1: <b>{tp1}</b>\n"
            f"🎯 익절 2: <b>{tp2}</b>\n"
            f"🎯 익절 3: <b>{tp3}</b>\n"
            f"🕐 시간: {time_}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"⚠️ 본 신호는 관점 공유용입니다.\n"
            f"투자의 책임은 본인에게 있습니다."
        )
    elif signal == "매도":
        stop  = round(price * 1.01, 2)
        tp1   = round(price * 0.99, 2)
        tp2   = round(price * 0.98, 2)
        tp3   = round(price * 0.97, 2)
        return (
            f"🐻 매도 신호 발생 🐻\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📌 종목: <b>{ticker}</b>\n"
            f"⏱ 타임프레임: {tf}\n"
            f"💰 진입가: <b>{price}</b>\n"
            f"🛑 손절가: <b>{stop}</b>\n"
            f"🎯 익절 1: <b>{tp1}</b>\n"
            f"🎯 익절 2: <b>{tp2}</b>\n"
            f"🎯 익절 3: <b>{tp3}</b>\n"
            f"🕐 시간: {time_}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"⚠️ 본 신호는 관점 공유용입니다.\n"
            f"투자의 책임은 본인에게 있습니다."
        )
    elif signal == "상승추세":
        return "📗 지금은 상승추세 입니다."
    elif signal == "하락추세":
        return "📕 지금은 하락추세 입니다."
    else:
        return f"🔔 {signal}"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw = request.data.decode("utf-8")
            try:
                data = json.loads(raw)
            except:
                data = {"signal": raw}
        print(f"[📩 수신] {data}")
        send_telegram(build_message(data))
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/test/up", methods=["GET"])
def test_up():
    data = {"signal": "매수", "ticker": "ETHUSD", "price": "3200.00", "interval": "15", "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    send_telegram(build_message(data))
    return "매수 신호 전송 완료!", 200

@app.route("/test/down", methods=["GET"])
def test_down():
    data = {"signal": "매도", "ticker": "ETHUSD", "price": "3200.00", "interval": "15", "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    send_telegram(build_message(data))
    return "매도 신호 전송 완료!", 200

@app.route("/test", methods=["GET"])
def test():
    send_telegram("🧪 <b>테스트 메시지</b>\nRailway 서버가 정상 연결되었습니다! ✅")
    return "테스트 메시지 전송 완료!", 200

@app.route("/", methods=["GET"])
def home():
    return "✅ Supertrend 신호 서버 실행 중!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
