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
    
    # Enhanced emergency detection
    emergency_words = ['flood', 'flooding', 'leak', 'leaking', 'emergency', 'broken pipe', 
                      'no heat', 'no hot water', 'burst pipe', 'water everywhere', 'urgent']
    
    if any(word in speech for word in emergency_words):
        gather = Gather(input='speech', timeout=10, action='/emergency_address', method='POST')
        gather.say("That sounds like an emergency! I need to get you help right away. "
                  "Can you please give me your complete address?", 
                  voice='Polly.Joanna', rate='medium', volume='loud')
        response.append(gather)
    else:
        gather = Gather(input='speech', timeout=8, action='/schedule', method='POST')
        gather.say("I understand. Do you need this fixed today or can it wait until tomorrow?", 
                  voice='Polly.Joanna', rate='medium', volume='loud')
        response.append(gather)
    
    return str(response)

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
    additional = request.form.get('SpeechResult', '').lower()
    response = VoiceResponse()
    
    if 'no' in additional or 'nothing' in additional:
        response.say("Wonderful! Thank you for choosing AIQsocials. Have a great day!", 
                    voice='Polly.Joanna', rate='medium', volume='loud')
    else:
        response.say("I'd be happy to help with that as well. Our technician will discuss that with you during your appointment. "
                    "Thank you for choosing AIQsocials!", 
                    voice='Polly.Joanna', rate='medium', volume='loud')
    
    response.hangup()
    return str(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
