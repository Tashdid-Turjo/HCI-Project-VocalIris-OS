import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json
import numpy as np
import queue

# --- CONFIGURATION ---
MODEL_PATH = "model"
MIC_ID = 11  # Using WASAPI (ID 11) for best stability
TARGET_RATE = 16000
audio_queue = queue.Queue()

print("Loading Vosk Model...")
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, TARGET_RATE)

def callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}")
    # Just push raw data to the queue to keep the driver loop fast
    audio_queue.put(indata.copy())

try:
    # 1. Get the rate Windows REQUIRES for this device
    device_info = sd.query_devices(MIC_ID, 'input')
    native_rate = int(device_info['default_samplerate'])
    
    print(f"Opening {device_info['name']} at Native {native_rate}Hz")

    # 2. Open the stream at the NATIVE rate to avoid -9997
    with sd.InputStream(samplerate=native_rate, 
                        device=MIC_ID, 
                        channels=1, 
                        callback=callback, 
                        dtype='float32'):
        
        print(f"\n--- VocalIris Online (Hardware Sync Active) ---")
        print("Speak now!")
        
        while True:
            # 3. Pull data from queue
            data = audio_queue.get()
            
            # 4. Manual Resample: Calculate the step (e.g., 48000/16000 = 3)
            step = int(native_rate / TARGET_RATE)
            resampled = data[::step]
            
            # 5. Convert to 16-bit PCM for Vosk
            audio_int16 = np.int16(resampled * 32767)
            
            if rec.AcceptWaveform(audio_int16.tobytes()):
                result = json.loads(rec.Result())
                if result['text']:
                    print(f"Detected: {result['text']}")

except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")