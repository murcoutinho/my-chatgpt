from flask_socketio import emit
import openai
import pyaudio
import wave
from pynput import keyboard
import threading
import time
import os

#To setup api key, follow this guide: https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
openai.api_key = os.environ["OPENAI_API_KEY"]

def chat(question):
    accumulated_response = ""
    for resp in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a useful assistant."},
                {"role": "user", "content": question},
            ],
        max_tokens=120,
        temperature=0.5,
        stream=True
    ):

        if "content" in resp["choices"][0]["delta"]:
            accumulated_response += resp["choices"][0]["delta"]["content"]
            emit('response', {'response_text': accumulated_response}, namespace='/chat')


def record_audio(output_filename, channels=1, rate=44100, chunk=1024, format=pyaudio.paInt16, max_duration=10):
    audio = pyaudio.PyAudio()

    stream = audio.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

    frames = []
    recording = True
    start_time = time.time()

    listener = keyboard.Listener(on_press=None)  # Initialize the listener outside the function

    def on_press(key):
        nonlocal recording, listener
        if key == keyboard.Key.space:
            recording = False
            listener.stop()  # Stop the listener when the space key is pressed

    listener.on_press = on_press  # Assign the on_press function

    space_key_thread = threading.Thread(target=listener.start)  # Start the listener thread
    space_key_thread.start()

    while recording:
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_duration:
            recording = False
            listener.stop()  # Stop the listener when the maximum duration is reached
            break
        data = stream.read(chunk)
        frames.append(data)

    space_key_thread.join()  # Wait for the space_key_thread to finish

    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    with wave.open(output_filename, 'wb') as wave_file:
        wave_file.setnchannels(channels)
        wave_file.setsampwidth(audio.get_sample_size(format))
        wave_file.setframerate(rate)
        wave_file.writeframes(b''.join(frames))

def chat_with_audio():
    record_audio("output.wav")
    
    with open("output.wav", "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']
