import openai
import requests
from flask import Flask, request
import os

app = Flask(__name__)

# مفاتيح
VERIFY_TOKEN = "admwjtgp"
PAGE_ACCESS_TOKEN = "EAAR6HpC3NZBcBO8ANm0zVyoKf7CleGuZBHeENQU5jn3WWYQ6fl0U1tCDa76Lf284iAgkEDnZBNnWz4HqM1dy5YF7hPVqkMHZCgZAprpQ4oc7oLFPSsxDCo8YWP3GZCB2d8pBVCsBtZAULRre2pyhv14Q6KLJMfJ2CPVYW6JAQy6UF6ZA9aErjFWGocSyqNZABdcH05HHJvayfuEoHH2xcRJxGuZA7c"
OPENAI_API_KEY = "sk-...MOwA"	


openai.api_key = OPENAI_API_KEY
FB_API = f"https://graph.facebook.com/v16.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
print(f"📥 Webhook GET Request → mode: {mode}, token: {token}, challenge: {challenge}")
        if mode == 'subscribe' and token == VERIFY_TOKEN:
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
                        completion = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": user_message}]
                        )
                        bot_response = completion['choices'][0]['message']['content']

                        response_data = {
                            'recipient': {'id': sender_id},
                            'message': {'text': bot_response}
                        }
                        requests.post(FB_API, json=response_data)

        except Exception as e:
            print("❌ Error:", e)

        return "EVENT_RECEIVED", 200

@app.route('/', methods=['GET'])
def home():
    return "✅ Bot is running.", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
