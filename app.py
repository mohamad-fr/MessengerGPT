import openai
import requests
from flask import Flask, request

app = Flask(__name__)

# 🔐 مفاتيح وتوكنات
VERIFY_TOKEN = "admwjtgp"
PAGE_ACCESS_TOKEN = "EAAR6HpC3NZBcBOZBLJbxHkuZBuQ7gM51cJYnmIHNj4k4UrgOiZBW3wIIjJkNAIfmgDCE4h5Vf8x1Yg3S7uBkRaP1H5g3jiCKHADlvLP6LvyuNJryXdWUcicZA1ZCoHVr68jN3nBYMDlxyvHzWBcaKy4oRZCGVI8UZBxdmQvYe6qyOizWZCacMT8hDU1tHKWFLPxX7sndBqv7KUbZCL2OLfN50ZD"
OPENAI_API_KEY = "sk-...MOwA"  # ← استبدله بمفتاحك الحقيقي

# إعداد OpenAI
openai.api_key = OPENAI_API_KEY

# API فيسبوك
FB_API = f"https://graph.facebook.com/v16.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

# ✅ تحقق من Webhook من فيسبوك
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("✅ Webhook Verified")
            return challenge, 200
        else:
            return "❌ Verification failed", 403

    elif request.method == 'POST':
        data = request.get_json()
        print("📩 Webhook Event Received:", data)

        try:
            for entry in data.get('entry', []):
                for messaging_event in entry.get('messaging', []):
                    sender_id = messaging_event['sender']['id']

                    if 'message' in messaging_event and 'text' in messaging_event['message']:
                        user_message = messaging_event['message']['text']
                        print("📨 User:", user_message)

                        # طلب إلى OpenAI
                        completion = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": user_message}]
                        )
                        bot_response = completion['choices'][0]['message']['content']
                        print("🤖 Bot:", bot_response)

                        # إرسال الرد
                        response_data = {
                            'recipient': {'id': sender_id},
                            'message': {'text': bot_response}
                        }
                        requests.post(FB_API, json=response_data)

        except Exception as e:
            print("❌ Error:", e)

        return "EVENT_RECEIVED", 200

# ✅ اختبار بسيط
@app.route('/', methods=['GET'])
def home():
    return "✅ Bot is running.", 200

# ✅ تشغيل التطبيق
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
