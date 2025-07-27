from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)

@app.route('/voice', methods=['POST'])
def voice():
    response = VoiceResponse()
    gather = Gather(input='speech', timeout=8, action='/respond', method='POST')
    gather.say(
        "Hello! You've reached AIQsocials. I'm Sarah, your AI assistant. "
        "What's your heating, cooling, or plumbing issue today?",
        voice='Polly.Joanna', 
        language='en-US', 
        rate='medium', 
        volume='loud'
    )
    response.append(gather)
    response.say("I didn't hear you clearly. Let me transfer you to our team.")
    response.hangup()
    return str(response)

@app.route('/respond', methods=['POST'])
def respond():
    speech = request.form.get('SpeechResult', '').lower()
    response = VoiceResponse()
    
    # Quick emergency detection
    if any(word in speech for word in ['flood', 'leak', 'emergency', 'broken pipe', 'no heat']):
        gather = Gather(input='speech', timeout=8, action='/emergency', method='POST')
        gather.say("That's urgent! What's your address for emergency service?", 
                  voice='Polly.Joanna', rate='medium', volume='loud')
        response.append(gather)
    else:
        gather = Gather(input='speech', timeout=8, action='/schedule', method='POST')
        gather.say("Got it. Do you need this fixed today or can it wait until tomorrow?", 
                  voice='Polly.Joanna', rate='medium', volume='loud')
        response.append(gather)
    
    return str(response)

@app.route('/emergency', methods=['POST'])
def emergency():
    response = VoiceResponse()
    response.say("Perfect! Emergency technician dispatched. You'll get a call within 30 minutes with arrival time.", 
                voice='Polly.Joanna', rate='medium', volume='loud')
    response.hangup()
    return str(response)

@app.route('/schedule', methods=['POST'])
def schedule():
    urgency = request.form.get('SpeechResult', '').lower()
    response = VoiceResponse()
    
    if 'today' in urgency:
        response.say("Same-day service is 150 to 300 dollars. I can schedule you today at 2 PM or 4 PM. Which works?", 
                    voice='Polly.Joanna', rate='medium', volume='loud')
    else:
        response.say("Great! Tomorrow I have 10 AM or 2 PM available. Which time works better for you?", 
                    voice='Polly.Joanna', rate='medium', volume='loud')
    
    gather = Gather(input='speech', timeout=8, action='/confirm', method='POST')
    response.append(gather)
    return str(response)

@app.route('/confirm', methods=['POST'])
def confirm():
    response = VoiceResponse()
    response.say("Perfect! You're scheduled. You'll receive text confirmation and our technician will call 15 minutes before arrival.", 
                voice='Polly.Joanna', rate='medium', volume='loud')
    response.hangup()
    return str(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
