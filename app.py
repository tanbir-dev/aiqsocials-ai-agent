from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

@app.route('/voice', methods=['POST'])
def voice():
    response = VoiceResponse()
    response.say("Hi, you've reached AIQsocials! I'm Sarah, your AI assistant. We're getting your AI agent ready. Please call back in 5 minutes!")
    return str(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

