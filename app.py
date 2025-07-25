from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import json

app = Flask(__name__)

@app.route('/voice', methods=['POST'])
def voice():
    response = VoiceResponse()
    
    # Professional greeting with conversation starter
    gather = Gather(
        input='speech',
        timeout=10,
        speech_timeout='auto',
        action='/process_response',
        method='POST'
    )
    
    gather.say(
        "Hello! You've reached AIQsocials. I'm Sarah, your AI assistant. "
        "I can help you right away while our technician finishes up with another customer. "
        "What's going on with your heating, cooling, or plumbing today?",
        voice='Polly.Joanna',
        language='en-US',
        rate='medium',
        volume='loud'
    )
    
    response.append(gather)
    
    # Fallback if no response
    response.say("I didn't catch that. Let me connect you with our team. Please hold on.")
    response.hangup()
    
    return str(response)

@app.route('/process_response', methods=['POST'])
def process_response():
    speech_result = request.form.get('SpeechResult', '').lower()
    response = VoiceResponse()
    
    # Emergency detection
    emergency_keywords = ['flooding', 'leak', 'no heat', 'no hot water', 'broken pipe', 'emergency']
    
    if any(keyword in speech_result for keyword in emergency_keywords):
        response.say(
            "That sounds urgent! Let me get you emergency service right away. "
            "Can you give me your address so I can dispatch a technician immediately?",
            voice='Polly.Joanna',
            rate='medium',
            volume='loud'
        )
        
        gather = Gather(input='speech', timeout=10, action='/get_address', method='POST')
        response.append(gather)
        
    else:
        response.say(
            "I understand you're having an issue. Let me ask a few quick questions to help you. "
            "Is this something that needs to be fixed today, or can it wait a day or two?",
            voice='Polly.Joanna',
            rate='medium',
            volume='loud'
        )
        
        gather = Gather(input='speech', timeout=10, action='/qualify_urgency', method='POST')
        response.append(gather)
    
    return str(response)

@app.route('/get_address', methods=['POST'])
def get_address():
    address = request.form.get('SpeechResult', '')
    response = VoiceResponse()
    
    response.say(
        f"Got it, {address}. I'm booking you for emergency service. "
        "A technician will be there within 2 hours. "
        "You'll receive a text confirmation with the exact time. "
        "Is the phone number you're calling from the best number to reach you?",
        voice='Polly.Joanna',
        rate='medium',
        volume='loud'
    )
    
    # Here you would integrate with FlexiFunnels webhook
    # send_to_flexifunnels('emergency', address, request.form.get('From'))
    
    response.hangup()
    return str(response)

@app.route('/qualify_urgency', methods=['POST'])
def qualify_urgency():
    urgency = request.form.get('SpeechResult', '').lower()
    response = VoiceResponse()
    
    if 'today' in urgency or 'urgent' in urgency:
        response.say(
            "Perfect. For same-day service, we typically charge between 150 to 300 dollars "
            "for the service call, plus parts if needed. Does that budget work for you?",
            voice='Polly.Joanna',
            rate='medium',
            volume='loud'
        )
        
        gather = Gather(input='speech', timeout=10, action='/book_appointment', method='POST')
        response.append(gather)
        
    else:
        response.say(
            "Great! Since it's not urgent, I can offer you a better rate. "
            "I have availability tomorrow at 10 AM or 2 PM. Which works better for you?",
            voice='Polly.Joanna',
            rate='medium',
            volume='loud'
        )
        
        gather = Gather(input='speech', timeout=10, action='/book_appointment', method='POST')
        response.append(gather)
    
    return str(response)

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    response = VoiceResponse()
    
    response.say(
        "Perfect! I've got you scheduled. You'll receive a text confirmation "
        "with all the details in just a moment. Our technician will call "
        "15 minutes before arrival. Is there anything else I can help you with?",
        voice='Polly.Joanna',
        rate='medium',
        volume='loud'
    )
    
    # Integration point for FlexiFunnels
    # send_booking_to_flexifunnels(request.form)
    
    response.hangup()
    return str(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


