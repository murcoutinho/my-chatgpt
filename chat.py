from datetime import datetime
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

def default_models(question, model = "gpt-3.5-turbo"):
    global last_queries 
    accumulated_response = ""
    system_message = "You are a helpful assistant."
    number_of_previous_messages_as_context = 1

    messages = [{"role": "system", "content": system_message}] + [{"role": "user", "content": message} for message in last_queries[-number_of_previous_messages_as_context:]] + [{"role": "user", "content": question}]
    for resp in openai.ChatCompletion.create(model=model,messages=messages,max_tokens=2048,stream=True):
        if "content" in resp["choices"][0]["delta"]:
            accumulated_response += resp["choices"][0]["delta"]["content"]
            emit('response', {'response_text': accumulated_response}, namespace='/chat')
    return accumulated_response


def query(model, system_message, user_messages):
    if not isinstance(user_messages, list):
        print("Not a list")
        return ""
    messages = [{"role": "system", "content": system_message}] + [{"role": "user", "content": message} for message in user_messages]
    try:                 
        response = openai.ChatCompletion.create(model=model,messages=messages)
        answer = response['choices'][0]['message']['content']
        return answer
    except Exception as e:
        print(f"RateLimitError: {e}")
        print("Waiting for seconds before retrying...")
        time.sleep(10)
        return query(system_message, user_messages)


def smart_model(question, model = "gpt-3.5-turbo"):
    global last_queries 
    system_message = "You are a helpful assistant."
    chain_of_thought_prompt = "Question. "+ question + "\nAnswer: Let's work this out in a step by step way to be sure we have the right answer."
    print("\n\n\n")
    print(chain_of_thought_prompt)
    output1 = query(model, system_message, [chain_of_thought_prompt])
    print("\n\n\n")
    print(output1)
    output2 = query(model, system_message, [chain_of_thought_prompt])
    print("\n\n\n")
    print(output2)
    output3 = query(model, system_message, [chain_of_thought_prompt])
    print("\n\n\n")
    print(output3)

    reflexion_prompt = "Question." + question + "\n\nResponse 1- " + output1 + "\n\nResponse 2-" + output2 + "\n\nResponse 3-" + output3 + "\n\nYou are a researcher tasked with investigating the 3 response options provided. List the flaws and faulty logic of each answer option. Let's work this out in a step by step way to be sure we have all the errors:"
    rout = query(model, system_message, [reflexion_prompt])
    print("\n\n\n")
    print(rout)


    dera_prompt = "Question. "+ question + "\n\nResponse 1- " + output1 + "\n\nResponse 2-" + output2 + "\n\nResponse 3-" + output3 + "\n\nResearcher conclusion- " + rout + "\n\nYou are a resolver tasked with 1) finding which of the 3 answer options the Researcher thought was best 2) improving that answer, and 3) Printing the improved answer in full. Let's work this out in a step by step way to be sure we have the right answer:"
    accumulated_response = ""
    messages = [{"role": "system", "content": system_message}] + [{"role": "user", "content": dera_prompt}]
    for resp in openai.ChatCompletion.create(model=model,messages=messages,max_tokens=2048,stream=True):
        if "content" in resp["choices"][0]["delta"]:
            accumulated_response += resp["choices"][0]["delta"]["content"]
            emit('response', {'response_text': accumulated_response}, namespace='/chat')
    return accumulated_response
 
def chat(question, model = "gpt-3.5-turbo"):
    log_file = "history.log"
    if model in ("gpt-3.5-turbo", "gpt-4"):
        response = default_models(question, model)
    else:
        if model == "smart-gpt-4":
            response = smart_model(question, "gpt-4")
        else:
            response = smart_model(question, "gpt-3.5-turbo")
    
    last_query_json = {
        "question": question,
        "response": response
    }
    last_queries.append(json.dumps(last_query_json))
    
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    last_query_json["date"] = timestamp
    with open(log_file, "a") as f:
        f.write(json.dumps(last_query_json) + "\n")

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
