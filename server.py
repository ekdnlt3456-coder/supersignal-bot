"""
TradingView → Telegram 신호 전송 서버
Railway 클라우드 배포용
"""

from flask import Flask, request, jsonify
import requests
from datetime import datetime
import json
import os

app = Flask(__name__)

# ============================================================
# ✅ Railway 환경변수에서 자동으로 읽어옵니다 (직접 수정 X)
# ============================================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID        = os.environ.get("CHAT_ID", "")
# ============================================================


def send_telegram(message: str):
    """텔레그램으로 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        print(f"[✅ 전송 성공] {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"[❌ 전송 실패] {e}")


def build_message(data: dict) -> str:
    """수신된 데이터로 텔레그램 메시지 생성"""
    signal = data.get("signal", "알 수 없음")
    ticker = data.get("ticker", "")
    price  = data.get("price", "")
    tf     = data.get("interval", "")
    time_  = data.get("time", datetime.now().strftime("%Y-%m-%d %H:%M"))

    if "상승" in signal:
        icon = "🚀"
        color_tag = "📗"
    elif "하락" in signal:
        icon = "🐻"
        color_tag = "📕"
    else:
        icon = "🔔"
        color_tag = "📘"

    return (
        f"{icon} <b>Supertrend 신호</b> {icon}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{color_tag} 신호: <b>{signal}</b>\n"
        f"📌 종목: <b>{ticker}</b>\n"
        f"💰 가격: <b>{price}</b>\n"
        f"⏱ 타임프레임: {tf}\n"
        f"🕐 시간: {time_}\n"
        f"━━━━━━━━━━━━━━━"
    )


@app.route("/webhook", methods=["POST"])
def webhook():
    """TradingView Webhook 수신"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw = request.data.decode("utf-8")
            try:
                data = json.loads(raw)
            except Exception:
                data = {"signal": raw}

        print(f"[📩 수신] {data}")
        message = build_message(data)
        send_telegram(message)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"[❌ 오류] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/test", methods=["GET"])
def test():
    """연결 테스트"""
    send_telegram(
        "🧪 <b>테스트 메시지</b>\n"
        "Railway 서버가 정상 연결되었습니다! ✅"
    )
    return "테스트 메시지 전송 완료!", 200


@app.route("/", methods=["GET"])
def home():
    return "✅ Supertrend 신호 서버 실행 중!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
