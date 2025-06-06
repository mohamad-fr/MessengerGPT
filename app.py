s
import os
import openai
from flask import Flask, request

app = Flask(_name_)

# Tokens from environment or default fallback
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "admwjtgp")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_TOKEN", "your_page_token_here")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_openai_key_here")

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

# Facebook Messages API endpoint
FB_API = f"https://graph.facebook.com/v16.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

# ✅ Webhook Verification & Event Handler
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("✅ Webhook Verified")
            return challenge, 200
        else:
            return "❌ Verification failed", 403

    elif request.method == 'POST':
        # Facebook sends events here
        data = request.get_json()
        print("📩 Webhook Event Received:", data)

        try:
            messaging = data['entry'][0]['messaging'][0]
            sender_id = messaging['sender']['id']
            if 'message' in messaging:
                user_message = messaging['message'].get('text')
                if user_message:
                    print("📨 User Message:", user_message)

                    # Send to ChatGPT
                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": user_message}]
                    )
                    bot_response = completion['choices'][0]['message']['content']
                    print("🤖 ChatGPT:", bot_response)

                    # Send response to Facebook Messenger
                    response_data = {
                        'recipient': {'id': sender_id},
                        'message': {'text': bot_response}
                    }
                    requests.post(FB_API, json=response_data)

        except Exception as e:
            print("❌ Error:", e)
        
        return "EVENT_RECEIVED", 200

# ✅ Simple default route (optional)
@app.route('/', methods=['GET'])
def home():
    return "👋 Flask server is running.", 200

# ✅ Run server
if _name_ == '_main_':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

