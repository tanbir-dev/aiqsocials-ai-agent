from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)

@app.route('/voice', methods=['POST'])
def voice():
    response = VoiceResponse()
    
    gather = Gather(input='speech', timeout=5, action='/simple_response')
    gather.say("Hi! This is Sarah from AIQsocials. What's your heating or plumbing issue today?", 
               voice='Polly.Joanna', rate='fast', volume='loud')
    response.append(gather)
    return str(response)

@app.route('/simple_response', methods=['POST'])
def simple_response():
    speech = request.form.get('SpeechResult', '').lower()
    response = VoiceResponse()
    
    if 'emergency' in speech or 'flooding' in speech:
        response.say("Emergency! I'm booking you now. A technician will call in 30 minutes.", 
                    voice='Polly.Joanna', rate='fast', volume='loud')
    else:
        response.say("Got it! I'll have our technician call you within 2 hours to schedule.", 
                    voice='Polly.Joanna', rate='fast', volume='loud')
    
    response.hangup()
    return str(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
