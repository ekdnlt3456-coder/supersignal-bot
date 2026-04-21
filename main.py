from flask import Flask, request, jsonify
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

# ============================================================
# 설정값 - 여기만 수정하면 됨
# ============================================================
TELEGRAM_TOKEN = "여기에_봇_토큰_입력"
CHAT_ID        = "여기에_채팅ID_입력"
WEBHOOK_SECRET = "supersignal2024"  # 트레이딩뷰 Alert URL에 붙는 비밀키
# ============================================================

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def send_telegram(message: str):
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }
    resp = requests.post(TELEGRAM_API, json=payload, timeout=10)
    print(f"Telegram response: {resp.status_code} {resp.text}")
    return resp.ok


def build_message(signal: str, symbol: str, price: str, timeframe: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    templates = {
        # 매수 신호
        "BUY": (
            "🚀 <b>매수 신호 발생!</b>\n"
            "━━━━━━━━━━━━━━━━━\n"
            f"📌 종목 : <b>{symbol}</b>\n"
            f"⏱ 타임프레임 : {timeframe}\n"
            f"💰 현재가 : {price}\n"
            f"🕐 시각 : {now}\n"
            "━━━━━━━━━━━━━━━━━\n"
            "✅ 슈퍼트렌드 돌파 확인\n"
            "⚠️ 손절·익절 라인 반드시 확인 후 진입!"
        ),

        # 매도 신호
        "SELL": (
            "🐻 <b>매도 신호 발생!</b>\n"
            "━━━━━━━━━━━━━━━━━\n"
            f"📌 종목 : <b>{symbol}</b>\n"
            f"⏱ 타임프레임 : {timeframe}\n"
            f"💰 현재가 : {price}\n"
            f"🕐 시각 : {now}\n"
            "━━━━━━━━━━━━━━━━━\n"
            "🔴 슈퍼트렌드 하향 돌파 확인\n"
            "⚠️ 숏 포지션 또는 매도 검토!"
        ),

        # 상승 추세 전환
        "상승추세 시작": (
            "📈 <b>상승 추세 전환!</b>\n"
            "━━━━━━━━━━━━━━━━━\n"
            f"📌 종목 : <b>{symbol}</b>\n"
            f"⏱ 타임프레임 : {timeframe}\n"
            f"💰 현재가 : {price}\n"
            f"🕐 시각 : {now}\n"
            "━━━━━━━━━━━━━━━━━\n"
            "🟢 슈퍼트렌드 상승 전환 감지\n"
            "💡 매수 시점 주시 권장"
        ),

        # 하락 추세 전환
        "하락추세 시작": (
            "📉 <b>하락 추세 전환!</b>\n"
            "━━━━━━━━━━━━━━━━━\n"
            f"📌 종목 : <b>{symbol}</b>\n"
            f"⏱ 타임프레임 : {timeframe}\n"
            f"💰 현재가 : {price}\n"
            f"🕐 시각 : {now}\n"
            "━━━━━━━━━━━━━━━━━\n"
            "🔴 슈퍼트렌드 하락 전환 감지\n"
            "💡 매도·관망 검토 권장"
        ),
    }

    return templates.get(signal, f"[신호] {signal}\n종목: {symbol}\n가격: {price}\n시각: {now}")


@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True) or {}

        signal    = str(data.get("signal",    "")).strip()
        symbol    = str(data.get("symbol",    "UNKNOWN")).strip()
        price     = str(data.get("price",     "N/A")).strip()
        timeframe = str(data.get("timeframe", "N/A")).strip()

        if not signal:
            return jsonify({"status": "ignored", "reason": "empty signal"}), 200

        message = build_message(signal, symbol, price, timeframe)
        ok = send_telegram(message)

        print(f"[{datetime.now()}] signal={signal} symbol={symbol} price={price} sent={ok}")
        return jsonify({"status": "ok", "sent": ok}), 200

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"서버 시작 - 포트 {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
