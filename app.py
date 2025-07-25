from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

@app.route('/voice', methods=['POST'])
def voice():
    response = VoiceResponse()
    
    # Enhanced voice with volume boost
    response.say(
        "Hello! You've reached AIQsocials, your premier AI automation agency. "
        "I'm Sarah, your dedicated AI assistant. We're currently fine-tuning "
        "your personalized AI solutions. Please call back in just a few minutes "
        "and I'll be ready to help you grow your business!",
        voice='Polly.Joanna',
        language='en-US',
        rate='medium',  # Optimal speech rate
        volume='loud'   # Amplify volume
    )
    
    return str(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
