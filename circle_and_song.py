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

    def rotate_generator(_n_reapeats,bases,speed):
        n_repeats = _n_reapeats
        result = []

        for i in range(n_repeats):
            angle = i * (speed * np.pi / n_repeats) 
            rotation_matrix = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)]
            ])

            transformed_shape = np.dot(bases, rotation_matrix.T)

            result.append(transformed_shape)

        repeated_combined = np.vstack(result)

        return repeated_combined

    def generate_3d_square_bug():
        minD = -0.49
        maxD = 0.49
        
        # Canal gauche
        valuesD_1 = np.linspace(minD, minD, 110)
        valuesD_2 = np.linspace(minD, maxD, 110)
        valuesD_3 = np.linspace(maxD, maxD, 110)
        valuesD_4 = np.linspace(maxD, minD, 110)
        valuesD = np.concatenate((valuesD_1, valuesD_2, valuesD_3, valuesD_4))
        
        # Canal droit
        valuesG_1 = np.linspace(minD, maxD, 110)
        valuesG_2 = np.linspace(maxD, maxD, 110)
        valuesG_3 = np.linspace(maxD, minD, 110)
        valuesG_4 = np.linspace(minD, minD, 110)
        valuesG = np.concatenate((valuesG_1, valuesG_2, valuesG_3, valuesG_4))
        
        # Répéter les motifs 1000 fois
        valuesD = np.tile(valuesD, 1000)  # Canal gauche
        valuesG = np.tile(valuesG, 1000)  # Canal droit
        
        # Ajuster le canal gauche pour introduire un décalage progressif
        scaling_factor = 0.995  # Ajustement léger pour simuler une fréquence légèrement différente
        adjusted_length = int(len(valuesD) * scaling_factor)
        valuesD = np.interp(
            np.linspace(0, len(valuesD), adjusted_length),
            np.arange(len(valuesD)),
            valuesD,
        )
        
        # Fusionner les deux canaux
        combined = np.array([[l, n] for l, n in zip(valuesD, valuesG[:len(valuesD)])])
        
        return combined

    def generate_key_point_fromvect(startP,endP,nbkey):
        #TODO : Vérifier que startP et minP sont dans l'interval
        x1, y1 = startP
        x2, y2 = endP

        #assert by 0 division
        if x1 == x2:
            x_list = [x1] * nbkey
            y_list = np.linspace(y1, y2, nbkey).tolist()
        else:
            m = (y2 - y1) / (x2 - x1)
            c = y1 - m * x1

            x_points = np.linspace(x1, x2, nbkey)
            y_points = m * x_points + c

            x_list = x_points.tolist()
            y_list = y_points.tolist()

        return x_list,y_list

    def generate_form_fromlistpoint(keyPoints, nbkey=440, repetition=1000,rotation=False):
        #inutile pour le moment l'objectif est des les avoirs pour limiter la saturation
        minD = -0.49
        maxD = 0.49

        #calcul du nombre de points par segment
        nb_segments = len(keyPoints)
        if nb_segments == 0:
            raise ValueError("La liste des keyPoints est vide.")
        nbkey_per_segment = max(2, nbkey // nb_segments)

        all_x = []
        all_y = []

        for startP, endP in keyPoints:
            x_list, y_list = generate_key_point_fromvect(startP, endP, nbkey_per_segment)
            all_x.extend(x_list)
            all_y.extend(y_list)
        
        combined = np.array([[x, y] for x, y in zip(all_x, all_y)])
        
        if(rotation):
            repeated_combined = rotate_generator(repetition,combined,3)
        else :
            repeated_combined = np.tile(combined, (repetition, 1))

        return repeated_combined
    
    def load_carottes():
        key_points = [
            ((-0.4816092399935375,-0.37894657900300266),(-0.1591693938523662,0.1592021537552604)),
            ((-0.1591693938523662,0.1592021537552604),(0.11945458469470865,0.2209937619007812)),
            ((0.11945458469470865,0.2209937619007812),(0.10035536035882046,-0.02055525175898196)),
            ((0.10035536035882046,-0.02055525175898196),(-0.4816092399935375,-0.37894657900300266)),
            ((0.11945458469470865,0.2209937619007812),(0.1037258117122125,0.3692936214500312)),
            ((0.1037258117122125,0.3692936214500312),(0.2306794793566458,0.35244136468307097)),
            ((0.2306794793566458,0.35244136468307097),(0.11945458469470865,0.2209937619007812)),
            ((0.11945458469470865,0.2209937619007812),(0.26775444424395817,0.27492098355505395)),
            ((0.26775444424395817,0.27492098355505395),(0.21045677123629358,0.21649982676292517)),
            ((0.21045677123629358,0.21649982676292517),(0.11945458469470865,0.2209937619007812)),
            ((0.10035536035882046,-0.02055525175898196),(-0.06816720731078127,0.046853775308858925)),
            ((-0.06816720731078127,0.046853775308858925),(0.05736277170044882,-0.047031382612303566)),
            ((0.05736277170044882,-0.047031382612303566),(0.10035536035882046,-0.02055525175898196)),
            ((-0.2465128375022424,0.013426859301285444),(-0.18051558575718243,-0.05538324907736642)),
            ((-0.18051558575718243,-0.05538324907736642),(-0.26037792668174536,-0.009713829608059324)),
            ((-0.26037792668174536,-0.009713829608059324),(-0.2465128375022424,0.013426859301285444)),
            ((-0.17740286614060008,-0.19160713255688813),(-0.24792461282502312,-0.16099072481698382)),
            ((-0.24792461282502312,-0.16099072481698382),(-0.1975339375099458,-0.2040044525700567)),
            ((-0.1975339375099458,-0.2040044525700567),(-0.17740286614060008,-0.19160713255688813)),
        ]
        return key_points

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

            #square
            minD = -0.49
            maxD = 0.49
            keyPoints = [
                ((maxD, maxD), (minD, maxD)),
                ((minD, maxD), (minD, minD)),
                ((minD, minD), (maxD, minD)),
                ((maxD, minD), (maxD, maxD))
            ]

            #triangle
            minD_T = -0.49
            maxD_T = 0.49
            keyPoints_T = [
                ((maxD_T, maxD_T), (minD_T, maxD_T)),
                ((minD_T, maxD_T), (0, minD_T)),
                ((0, minD_T), (maxD_T, maxD_T)),
            ]

            keyPoints_k = load_carottes()
            # Ajustement de la durée si nécessaire
            min_length = min(len(wav_data), len(generated_sound))
            wav_data = wav_data[:min_length]
            generated_sound = generated_sound[:min_length]
            triangle = generate_form_fromlistpoint(keyPoints_k,440,1000,False)
            square = generate_form_fromlistpoint(keyPoints,440,1000,True)

            # Réduction de l'influence du fichier .wav
            wav_data = wav_weight * wav_data


            # Superposition des deux sons
            # print(max(generated_sound[:441000,0]))
            mixed_sound = generated_sound[:441000] + wav_data[:441000]
            print("mixage du premier son ok")
            mixed_sound_2 = triangle + wav_data[441000:878000]
            print("mixage du deuxieme son ok")
            mixed_sound_3 = square + wav_data[878000:1318000]
            print("mixage du troisieme son ok")

            # Lecture du son mixé
            # print("Lecture du son mixé...")
            # print(mixed_sound)

            # mixed_sound_2 = check_if_kik(mixed_sound,wav_data[:900000])
            # draw_graph(mixed_sound[90000:120000])
            # print(mixed_sound[0,0])
            # print(mixed_sound[441,0])

            # draw_graph(triangle)
            # draw_graph(generated_sound[115000:120000])
            draw_graph(triangle[249000:250000])

            # draw_graph(mixed_sound)
            
            duoform = np.concatenate((mixed_sound, mixed_sound_2,mixed_sound_3))

            # sd.play(mixed_sound_3, samplerate=samplerate)
            # sd.wait()
            sd.play(duoform, samplerate=samplerate)
            sd.wait()
            print("Lecture terminée.")
        except Exception as e:
            print(f"Erreur lors de la lecture ou du mixage : {e}")

    print(len(stereo_sound))
    play_and_mix_wav("carotte.wav", stereo_sound[:1323000], fs, wav_weight=0.3)

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