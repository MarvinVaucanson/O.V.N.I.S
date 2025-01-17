import numpy as np
import sounddevice as sd
import soundfile as sf

fs = 44100
total_duration = 20
base_frequency_left = 440
base_frequency_right = 441 
frequency_multiplier = 2 
segment_normal_duration = 1 
interruption_duration = 1 
amplitude = 0.5

# génération des segments dynamiquement
segments_left = []
segments_right = []

time_normal = np.linspace(0, segment_normal_duration, int(fs * segment_normal_duration), endpoint=False)
time_interruption = np.linspace(0, interruption_duration, int(fs * interruption_duration), endpoint=False)

for i in range(total_duration // (segment_normal_duration + interruption_duration)):
    left_normal = amplitude * np.sin(2 * np.pi * base_frequency_left * time_normal)
    right_normal = amplitude * np.sin(2 * np.pi * base_frequency_right * time_normal)
    
    left_interruption = amplitude * np.sin(2 * np.pi * base_frequency_left * frequency_multiplier * time_interruption)
    right_interruption = amplitude * np.sin(2 * np.pi * base_frequency_right * frequency_multiplier * time_interruption *2)
    
    segments_left.append(left_normal)
    segments_left.append(left_interruption)
    segments_right.append(right_normal)
    segments_right.append(right_interruption)

left_channel = np.concatenate(segments_left)
right_channel = np.concatenate(segments_right)

stereo_sound = np.column_stack((left_channel, right_channel))

sd.play(stereo_sound, samplerate=fs)
sd.wait()

sf.write('output.wav', stereo_sound, fs)
print("Fichier audio sauvegardé en tant que 'output.wav'")