import json
import os
import time

from vosk import Model, KaldiRecognizer
import pyaudio


sample_rate = 16000
chunk_size = 8000
format = pyaudio.paInt16
channels = 1


def load_model():
    global model, rec, p, stream
    # Path to the model
    model_path = "vosk-model-small-en-us-0.15"
    if not os.path.exists(model_path):
        print(f"Please make sure the Vosk model path is correct: {model_path}")
        exit(1)

    model = Model(model_path)

    # Microphone setting
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open stream
    stream = p.open(format=format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk_size)

    # Initialize recognizer
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    print("Recording...")


def start_listening(user_text):
    while True:
        try:
            data = stream.read(chunk_size)
            if rec.AcceptWaveform(data):
                result = rec.Result()
                parsed_json = json.loads(result)
                parsed_result = parsed_json["text"]
                print(f'user text: {parsed_result}')
                user_text.append(parsed_result)

        except Exception as e:
            print(f"Error: {e}")

def stop_listening():
    print("Stopped listening...")
    # Don't forget to stop and close the stream and terminate PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()