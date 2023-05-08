from flask_socketio import emit
import openai
import pyaudio
import wave
import threading
import time
import os
import json

#To setup api key, follow this guide: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
openai.api_key = os.environ["OPENAI_API_KEY"]
stop_recording_event = threading.Event()

last_queries = [""]

def chat(question, model = "gpt-3.5-turbo"):
    global last_queries 
    accumulated_response = ""
    system_message = "You are a helpful assistant."
    number_of_previous_messages_as_context = 1

    messages = [{"role": "system", "content": system_message}] + [{"role": "user", "content": message} for message in last_queries[-number_of_previous_messages_as_context:]] + [{"role": "user", "content": question}]
    print(messages)
    for resp in openai.ChatCompletion.create(model=model,messages=messages,max_tokens=2048,stream=True):
        if "content" in resp["choices"][0]["delta"]:
            accumulated_response += resp["choices"][0]["delta"]["content"]
            emit('response', {'response_text': accumulated_response}, namespace='/chat')
    last_queries.append(json.dumps({
        "question": question,
        "response": accumulated_response
    }))

def record_audio(output_filename, channels=1, rate=44100, chunk=1024, format=pyaudio.paInt16, max_duration=100, stop_recording_event=None):
    audio = pyaudio.PyAudio()

    stream = audio.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

    frames = []
    recording = True
    start_time = time.time()
    
    while recording:
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_duration or (stop_recording_event and stop_recording_event.is_set()):
            recording = False
            break
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    with wave.open(output_filename, 'wb') as wave_file:
        wave_file.setnchannels(channels)
        wave_file.setsampwidth(audio.get_sample_size(format))
        wave_file.setframerate(rate)
        wave_file.writeframes(b''.join(frames))

def chat_with_audio():
    global stop_recording_event  # use the global stop_recording_event
    stop_recording_event.clear() # Clear the event before starting a new recording
    record_audio("output.wav", stop_recording_event=stop_recording_event)
    
    with open("output.wav", "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']
