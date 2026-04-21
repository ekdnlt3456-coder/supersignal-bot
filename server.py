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
    signal = data.get("signal", "")

    if signal == "매수":
        return "🟢 이더리움 매수[LONG]신호"
    elif signal == "매도":
        return "🔴 이더리움 매도[SHORT]신호"
    elif signal == "상승추세":
        return "📈 지금 이더리움은 상승추세 입니다."
    elif signal == "하락추세":
        return "📉 지금 이더리움은 하락추세 입니다."
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
    send_telegram(build_message({"signal": "매수"}))
    return "매수 신호 전송 완료!", 200

@app.route("/test/down", methods=["GET"])
def test_down():
    send_telegram(build_message({"signal": "매도"}))
    return "매도 신호 전송 완료!", 200

@app.route("/test/trend/up", methods=["GET"])
def test_trend_up():
    send_telegram(build_message({"signal": "상승추세"}))
    return "상승추세 신호 전송 완료!", 200

@app.route("/test/trend/down", methods=["GET"])
def test_trend_down():
    send_telegram(build_message({"signal": "하락추세"}))
    return "하락추세 신호 전송 완료!", 200

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
