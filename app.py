from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)

# 🔍 Intent keyword map
intent_map = {
    'emergency': ['emergency', 'flood', 'leak', 'burst pipe', 'water everywhere', 'no hot water', 'urgent'],
    'schedule': ['appointment', 'fix', 'schedule', 'today', 'tomorrow', 'book', 'time'],
    'quote': ['price', 'cost', 'estimate', 'how much', 'charge'],
    'cancel': ['cancel', 'change', 'reschedule', 'wrong time', 'not needed']
}

# 🧠 Intent parser
def parse_intent(speech):
    for intent, keywords in intent_map.items():
        if any(word in speech for word in keywords):
            return intent
    return 'unknown'

# 🎙 Entry voice route - FIXED PAUSE
@app.route('/voice', methods=['POST'])
def voice():
    response = VoiceResponse()
    
    response.say("Hello! You've reached A-I-Q-socials. I'm Sarah, your AI assistant.",
                voice='Polly.Joanna', rate='medium', volume='loud')
    response.pause(length=1.0)
    
    gather = Gather(input='speech', timeout=8, action='/respond', method='POST')
    gather.say("What's your heating, cooling, or plumbing issue today?",
               voice='Polly.Joanna', rate='medium', volume='loud')
    response.append(gather)
    response.say("I didn't hear you clearly. Let me transfer you to our team.")
    response.hangup()
    return str(response)

# 🧠 Smart response routing - ENHANCED FALLBACK
@app.route('/respond', methods=['POST'])
def respond():
    speech_result = request.values.get('SpeechResult')
    response = VoiceResponse()

    # 🔍 Flexible fallback handling - No SpeechResult at all
    if not speech_result:
        response.say("I didn't hear you clearly. Let me transfer you to our team.",
                     voice='Polly.Joanna', rate='medium', volume='loud')
        response.hangup()
        return str(response)
    
    # 🔍 Handle very short/unclear responses
    speech = speech_result.lower().strip()
    if len(speech) < 3:
        gather = Gather(input='speech', timeout=8, action='/respond', method='POST')
        gather.say("Could you please tell me more about your issue?",
                   voice='Polly.Joanna', rate='medium', volume='loud')
        response.append(gather)
        return str(response)

    # 🧠 Intent resolution
    intent = parse_intent(speech)

    if intent == 'emergency':
        gather = Gather(input='speech', timeout=10, action='/emergency_address', method='POST')
        gather.say("That sounds like an emergency! I need to get you help right away. "
                   "Can you please give me your complete address?",
                   voice='Polly.Joanna', rate='medium', volume='loud')
        response.append(gather)

    elif intent == 'schedule':
        gather = Gather(input='speech', timeout=8, action='/schedule', method='POST')
        gather.say("I understand. Do you need this fixed today or can it wait until tomorrow?",
                   voice='Polly.Joanna', rate='medium', volume='loud')
        response.append(gather)

    elif intent == 'quote':
        response.say("Our service pricing typically ranges from 150 to 300 dollars depending on the issue. "
                     "Would you like me to connect you with a technician for more details?",
                     voice='Polly.Joanna', rate='medium', volume='loud')
        response.hangup()

    elif intent == 'cancel':
        response.say("No problem. I won't book anything for now. Let me know if you need help in the future.",
                     voice='Polly.Joanna', rate='medium', volume='loud')
        response.hangup()

    else:
        response.say("Thank you for sharing that. Our support team will review your issue and contact you shortly.",
                     voice='Polly.Joanna', rate='medium', volume='loud')
        response.hangup()

    return str(response)

# 🚨 Emergency flow
@app.route('/emergency_address', methods=['POST'])
def emergency_address():
    address = request.form.get('SpeechResult', '')
    response = VoiceResponse()

    gather = Gather(input='speech', timeout=8, action='/emergency_confirm', method='POST')
    gather.say(f"Got it, so that's {address}. I'm immediately connecting you with our emergency team. "
               "They'll contact you within the next 10 minutes to arrange immediate service. "
               "Is there anything else I can help you with right now?",
               voice='Polly.Joanna', rate='medium', volume='loud')
    response.append(gather)

    return str(response)

@app.route('/emergency_confirm', methods=['POST'])
def emergency_confirm():
    additional = request.form.get('SpeechResult', '').lower()
    response = VoiceResponse()

    if 'no' in additional or 'nothing' in additional:
        response.say("Perfect! Help is on the way. Stay safe and our emergency team will contact you shortly.",
                     voice='Polly.Joanna', rate='medium', volume='loud')
    else:
        response.say("I understand. Our emergency team will address that as well when they contact you. "
                     "Stay safe, and help is coming soon.",
                     voice='Polly.Joanna', rate='medium', volume='loud')

    response.hangup()
    return str(response)

# 📅 Scheduling flow
@app.route('/schedule', methods=['POST'])
def schedule():
    urgency = request.form.get('SpeechResult', '').lower()
    response = VoiceResponse()

    if 'today' in urgency or 'urgent' in urgency:
        gather = Gather(input='speech', timeout=10, action='/confirm_today', method='POST')
        gather.say("For same-day service, our rate is typically 150 to 300 dollars depending on the work needed. "
                   "I can schedule you for today at 2 PM or 4 PM. Which time works better for you?",
                   voice='Polly.Joanna', rate='medium', volume='loud')
        response.append(gather)
    else:
        gather = Gather(input='speech', timeout=10, action='/confirm_tomorrow', method='POST')
        gather.say("Great! For tomorrow, I have 10 AM or 2 PM available. Which time works better for you?",
                   voice='Polly.Joanna', rate='medium', volume='loud')
        response.append(gather)

    return str(response)

@app.route('/confirm_today', methods=['POST'])
def confirm_today():
    time_choice = request.form.get('SpeechResult', '')
    response = VoiceResponse()

    gather = Gather(input='speech', timeout=8, action='/final_confirm', method='POST')
    gather.say(f"Perfect! I have you scheduled for today at {time_choice}. "
               "You'll receive a text confirmation shortly, and our technician will call 15 minutes before arrival. "
               "Is there anything else I can help you with?",
               voice='Polly.Joanna', rate='medium', volume='loud')
    response.append(gather)

    return str(response)

@app.route('/confirm_tomorrow', methods=['POST'])
def confirm_tomorrow():
    time_choice = request.form.get('SpeechResult', '')
    response = VoiceResponse()

    gather = Gather(input='speech', timeout=8, action='/final_confirm', method='POST')
    gather.say(f"Excellent! You're all set for tomorrow at {time_choice}. "
               "You'll get a text confirmation, and our technician will call 15 minutes before arrival. "
               "Can I help you with anything else today?",
               voice='Polly.Joanna', rate='medium', volume='loud')
    response.append(gather)

    return str(response)

@app.route('/final_confirm', methods=['POST'])
def final_confirm():
    user_response = request.form.get('SpeechResult', '').lower()
    response = VoiceResponse()

    if any(word in user_response for word in ['no', 'nothing', 'good', 'fine']):
        response.say("Wonderful! Thank you for choosing A-I-Q-socials. Have a great day!",
                     voice='Polly.Joanna', rate='medium', volume='loud')
    else:
        response.say("Our technician will handle that too. Thank you for choosing A-I-Q-socials!",
                     voice='Polly.Joanna', rate='medium', volume='loud')

    response.hangup()
    return str(response)

# 🚀 Launch config
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
