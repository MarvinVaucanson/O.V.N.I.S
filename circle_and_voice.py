import numpy as np
import sounddevice as sd

def launch_live_mix(_base_frequency, _form, _rotation_speed, mic_weight=0.5):
    fs = 44100 
    amplitude = 0.5
    base_frequency = _base_frequency / _form
    base_frequency_rotate = (base_frequency * _form) + _rotation_speed

    #callback for real time
    def audio_callback(indata, outdata, frames, time, status):
        if status:
            print(f"Statut : {status}")
        # Signal généré
        t = (np.arange(frames) + audio_callback.time) / fs
        left_channel = amplitude * np.sin(2 * np.pi * base_frequency * t)
        right_channel = amplitude * np.sin(2 * np.pi * base_frequency_rotate * t + np.pi / 2)
        generated_signal = np.column_stack((left_channel, right_channel))

        mic_signal = indata * mic_weight
        mixed_signal = generated_signal + mic_signal

        outdata[:] = mixed_signal

        audio_callback.time += frames

    audio_callback.time = 0

    # start audio
    try:
        print("Streaming en direct... Parlez dans le microphone !")
        with sd.Stream(channels=2, samplerate=fs, callback=audio_callback):
            input("Appuyez sur Entrée pour arrêter.\n")
    except Exception as e:
        print(f"Erreur lors du streaming : {e}")

# launch record
launch_live_mix(100, 1, 0.1)
