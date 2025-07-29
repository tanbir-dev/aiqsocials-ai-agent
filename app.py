from flask import Flask, request, session
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests
import re

app = Flask(__name__)
app.secret_key = 'sarah_secret_key'

MCP_ENDPOINT = "https://mcp.aiqsocials.com/dispatch"

intent_map = {
    'emergency': ['emergency', 'flood', 'leak', 'burst pipe', 'water everywhere', 'no hot water', 'urgent'],
    'schedule': ['appointment', 'fix', 'schedule', 'today', 'tomorrow', 'book', 'time'],
    'quote': ['price', 'cost', 'estimate', 'how much', 'charge'],
    'cancel': ['cancel', 'change', 'reschedule', 'wrong time', 'not needed']
}

def parse_intent(speech):
    speech = speech.lower()
    for intent, keywords in intent_map.items():
        if any(word in speech for word in keywords):
            return intent
    return 'unknown'

def enrich_emotion(speech):
    if re.search(r'\b(waiting|angry|frustrated|not happy|bad service)\b', speech):
        return 'empathetic'
    elif re.search(r'\bplease|thank you|kindly|help\b', speech):
        return 'friendly'
    return 'neutral'

def prompt(text, action=None, timeout=6, tone='neutral'):
    response = VoiceResponse()
    phrases = {
        'neutral': text,
        'friendly': f"Sure thing. {text}",
        'empathetic': f"I'm really sorry about that. {text}"
    }
    if action:
        gather = Gather(input='speech', timeout=timeout, action=action, method='POST')
        gather.say(phrases[tone], voice='Polly.Joanna')
        response.append(gather)
    else:
        response.say(phrases[tone], voice='Polly.Joanna')
    return response

@app.route('/voice', methods=['POST'])
def voice():
    caller = request.values.get('Caller', 'unknown')
    session['caller'] = caller
    session['retry'] = 0
    return str(prompt("Hello! I'm Sarah from AIQSocials. What can I help you with today?", action='/respond'))

@app.route('/respond', methods=['POST'])
def respond():
    speech = request.values.get('SpeechResult', '').strip().lower()
    tone = enrich_emotion(speech)
    retry = session.get('retry', 0)

    if not speech:
        session['retry'] += 1
        if retry >= 1:
            return str(prompt("Still unclear. Transferring now.", tone=tone).hangup())
        return str(prompt("Could you repeat that one more time?", action='/respond', tone=tone))

    intent = parse_intent(speech)
    session['intent'] = intent

    if intent == 'emergency':
        return str(prompt("Got it. What's your full address?", action='/emergency_address', timeout=8, tone=tone))
    elif intent == 'schedule':
        return str(prompt("Would you like service today or tomorrow?", action='/schedule', timeout=8, tone=tone))
    elif intent == 'quote':
        return str(prompt("Our pricing typically ranges from 150 to 300 dollars. We'll confirm exact rates soon.", tone=tone).hangup())
    elif intent == 'cancel':
        return str(prompt("Understood. No bookings made. Reach out anytime.", tone=tone).hangup())
    else:
        return str(prompt("Thanks. We'll review your request and follow up shortly.", tone=tone).hangup())

@app.route('/emergency_address', methods=['POST'])
def emergency_address():
    address = request.values.get('SpeechResult', '').strip()
    caller = session.get('caller')
    if address:
        requests.post(MCP_ENDPOINT, json={
            "intent": "emergency",
            "caller": caller,
            "address": address
        })
        return str(prompt(f"Help is on its way to {address}. Stay safe.").hangup())
    return str(prompt("Couldn't catch the address. Please call us directly for help.").hangup())

@app.route('/schedule', methods=['POST'])
def schedule():
    time_req = request.values.get('SpeechResult', '').lower()
    tone = enrich_emotion(time_req)
    caller = session.get('caller')

    if 'today' in time_req:
        session['preferred_day'] = 'today'
        return str(prompt("What time today suits you?", action='/confirm_today', tone=tone))
    elif 'tomorrow' in time_req:
        session['preferred_day'] = 'tomorrow'
        return str(prompt("What time tomorrow would you prefer?", action='/confirm_tomorrow', tone=tone))
    return str(prompt("Thanks. We'll reach out shortly.", tone=tone).hangup())

@app.route('/confirm_today', methods=['POST'])
def confirm_today():
    time = request.values.get('SpeechResult', '').strip()
    caller = session.get('caller')
    requests.post(MCP_ENDPOINT, json={
        "intent": "schedule",
        "caller": caller,
        "day": "today",
        "time": time
    })
    return str(prompt(f"Scheduled for today at {time}. You’ll get a confirmation shortly.").hangup())

@app.route('/confirm_tomorrow', methods=['POST'])
def confirm_tomorrow():
    time = request.values.get('SpeechResult', '').strip()
    caller = session.get('caller')
    requests.post(MCP_ENDPOINT, json={
        "intent": "schedule",
        "caller": caller,
        "day": "tomorrow",
        "time": time
    })
    return str(prompt(f"Scheduled for tomorrow at {time}. Confirmation will follow.").hangup())

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
