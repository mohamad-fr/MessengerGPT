import requests
import os
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "admwjtgp")  # نفس التوكن اللي في الصورة

@app.route('/', methods=['GET'])
def home():
    return "Webhook is live 🟢"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # تحقق من التوكن عند إعداد Webhook من Facebook
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED ✅")
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    elif request.method == 'POST':
        # استقبال بيانات من Facebook
        data = request.get_json()
        print("Received webhook data:", data)
        return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
#This is API key for OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")
# This is page access token that you get from facebook developer console.
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_TOKEN")
# This is API key for facebook messenger.
API="https://graph.facebook.com/v16.0/me/messages?access_token="+PAGE_ACCESS_TOKEN

@app.route('/', methods=['GET'])
def verify():
    # Verify the webhook subscription with Facebook Messenger
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "pogiako":
            return "Verification token missmatch", 403
        return request.args['hub.challenge'], 200
    return "Hello world", 200

@app.route("/", methods=['POST'])
def fbwebhook():
    data = request.get_json()
    try:
        if data['entry'][0]['messaging'][0]['sender']['id']:
            message = data['entry'][0]['messaging'][0]['message']
            sender_id = data['entry'][0]['messaging'][0]['sender']['id']
            chat_gpt_input=message['text']
            print(chat_gpt_input)
            completion = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": chat_gpt_input}])          
            chatbot_res = completion['choices'][0]['message']['content']
            print("ChatGPT Response=>",chatbot_res)
            response = {
                'recipient': {'id': sender_id},
                'message': {'text': chatbot_res}
            }
            requests.post(API, json=response)
    except Exception as e:
        print(e)
        pass
    return '200 OK HTTPS.'
  # Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
