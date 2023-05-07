from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from chat import chat, chat_with_audio, stop_recording_event

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/', methods=['GET'])
def template_selector():
    return render_template('template_selector.html')

@app.route('/chat', methods=['GET'])
def select_chat():
    return render_template('chat.html')

@app.route('/transcribe_audio', methods=['GET'])
def transcribe_audio():
    transcript_text = chat_with_audio()
    return jsonify(transcript_text=transcript_text)

@socketio.on('submit_question', namespace='/chat')
def handle_submit_question(data):
    question = data['question']
    chat(question)

@app.route('/stop_recording', methods=['GET'])
def stop_recording():
    stop_recording_event.set()
    return jsonify(status="success")

if __name__ == '__main__':
    socketio.run(app)
