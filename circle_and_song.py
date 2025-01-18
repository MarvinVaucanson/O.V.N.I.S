import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt

def launch_song(_base_frequency, _form, _duration, _rotation_speed):
    # Paramètres
    fs = 44100  # Fréquence d'échantillonnage
    duration = 200  # Durée (secondes)
    amplitude = 0.5  # Amplitude du signal
    base_frequency = _base_frequency/_form  # Fréquence de base (Hz)
    base_frequency_rotate = (base_frequency *_form)+_rotation_speed
    modulation_frequency = 5  # Fréquence de modulation pour les interférences (Hz)
    interference_intensity = 0.1  # Intensité des interférences

    # Génération du signal
    samples = np.linspace(0, duration, int(fs * duration), endpoint=False)

    # Génération des signaux pour les deux canaux
    left_channel = amplitude * np.sin(2 * np.pi * base_frequency * samples)
    right_channel = amplitude * np.sin(2 * np.pi * base_frequency_rotate * samples + np.pi / 2)

    # Combine en stéréo pour le son généré
    stereo_sound = np.column_stack((left_channel, right_channel))

    def draw_graph(mixed_sound_data):
        time = np.linspace(0, len(mixed_sound_data) / fs, num=len(mixed_sound_data))
        # Tracé
        plt.figure(figsize=(70, 6))
        plt.plot(time, mixed_sound_data[:, 0], label="Canal gauche")
        plt.plot(time, mixed_sound_data[:, 1], label="Canal droit")
        plt.legend()
        plt.xlabel("Temps (s)")
        plt.ylabel("Amplitude")
        plt.title("Signal Audio Stéréo")
        plt.grid(True)
        plt.show()
    
    def check_if_kik(mixed_sound_data,wav_data_sound):
        """
        En gros je me dis je peux faire plusieurs choses. Je peux travailler sur le son déjà mixé
        Mais je peux aussi save les indices des kiks et modifier la boucle initial pour les 5 seconde suivante

        Objectif : Afficher la chips aprs chaque kik
        """
        audio_canal_right = mixed_sound_data[:1000,0]
        maxi_normal = max(audio_canal_right)
        print(mixed_sound_data[:900000,0])
        maxi_all = max(mixed_sound_data[:900000,0])

        maxi_moy = (maxi_normal + maxi_all)/2
        # maxi_moy = np.mean(maxi_normal,maxi_moy)
        print('max',maxi_moy)
        temp = 100000

        i = 0 
        while i < len(mixed_sound_data):
            if mixed_sound_data[i,0] > maxi_moy:
                end_index = min(i + temp, len(mixed_sound_data))
                mixed_sound_data[i+5000:end_index,0] = wav_data_sound[i+5000:end_index,0]
                mixed_sound_data[i+5000:end_index,1] = wav_data_sound[i+5000:end_index,1]

                i = end_index 
            else:
                i += 1

        return mixed_sound_data

    def generate_linear_triangle():
        #first sequence
        minD = -0.9
        maxD = 0.9
        valuesD_1 = np.linspace(minD, maxD, 145)

        #second sequence
        valuesD_2 = np.linspace(maxD, maxD, 145)

        #third sequence
        valuesD_3 = np.linspace(maxD,minD,145)

        valuesD = valuesD_1 + valuesD_2

    # Lecture et superposition d'un fichier .wav
    def play_and_mix_wav(file_path, generated_sound, samplerate, wav_weight):
        """
        Joue un son mixé entre le fichier .wav et un son généré.

        :param file_path: Chemin du fichier .wav
        :param generated_sound: Signal stéréo généré
        :param samplerate: Fréquence d'échantillonnage
        :param wav_weight: Facteur de pondération pour le fichier .wav (0 à 1)
        """
        try:
            # Chargement du fichier .wav
            wav_data, wav_samplerate = sf.read(file_path)

            if wav_samplerate != samplerate:
                raise ValueError("La fréquence d'échantillonnage du fichier .wav ne correspond pas à celle du son généré.")

            # Ajustement de la durée si nécessaire
            min_length = min(len(wav_data), len(generated_sound))
            wav_data = wav_data[:min_length]
            generated_sound = generated_sound[:min_length]

            # Réduction de l'influence du fichier .wav
            wav_data = wav_weight * wav_data

            # Superposition des deux sons
            mixed_sound = generated_sound + wav_data

            # Lecture du son mixé
            print("Lecture du son mixé...")
            print(mixed_sound)

            mixed_sound_2 = check_if_kik(mixed_sound,wav_data[:900000])
            # draw_graph(mixed_sound[90000:120000])
            print(mixed_sound_2[0,0])
            print(mixed_sound_2[441,0])

            value_canal_droit_triangle = generate_linear_triangle()
            draw_graph(value_canal_droit_triangle)

            draw_graph(mixed_sound_2[:441])
            # sd.play(mixed_sound_2, samplerate=samplerate)
            # sd.wait()
            print("Lecture terminée.")
        except Exception as e:
            print(f"Erreur lors de la lecture ou du mixage : {e}")

    play_and_mix_wav("carotte.wav", stereo_sound[:900000], fs, wav_weight=0.3)

    print("Le son a été joué. Connecte un oscilloscope pour visualiser le cercle avec des perturbations dynamiques.")


#Frequency 
# Under 100 (algo)
# Form
# -> 1 for circle
# -> 2 for chips
# -> 3 for lissajous form
# -> 4 for mor complexe and repetition form (la forme est moins précise)
# comme il y a division de la fréquence la forme est moins stable


launch_song(100,1,20,0.3)


# TODO :
# Modifier la vitesse de rotation en fonction du tempo
# Modifier la forme en cas de kick
# Modulation sonore pour modifier la taille de la forme
# Lisser certaines courbes 
# Essayer de changer la fréquence de base pour faire genre un dessin ou un truc plus énervé
# connecter l'input avec une playlist (ou encore mieux youtube ou spotify)



# si je genere une courbe mathematique animé frame par frame pour faire une animation et que je lance le code doit y avoir moyen de faire une folie 