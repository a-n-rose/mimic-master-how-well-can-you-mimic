import librosa
import numpy as np
import matplotlib.pyplot as plt
import acoustid
import chromaprint
from fuzzywuzzy import fuzz

from rednoise_fun import rednoise, wave2stft, stft2power, get_mean_bandwidths, get_var_bandwidths, stft2wave, savewave, get_date, matchvol, get_pitch,get_pitch2, get_pitch_mean, pitch_sqrt, sound_index, get_energy, get_energy_mean

def get_fingpr(filename):
    duration, fp_encoded = acoustid.fingerprint_file(filename)
    fingerprint, version = chromaprint.decode_fingerprint(fp_encoded)
    return(fingerprint)

def comp_fingpr(fingerprint1,fingerprint2):
    similarity = fuzz.ratio(fingerprint1,fingerprint2)
    return(similarity)

def wave2fingerprint(wavefile, target, noise):
    y_stft, y, sr = wave2stft(wavefile)
    y_power = stft2power(y_stft)
    y_energy = get_energy(y_stft)
    n_stft, ny, nsr = wave2stft(noise)
    n_power = stft2power(n_stft)
    n_energy = get_energy(n_stft)
    n_energy_mean = get_energy_mean(n_energy)

    t_stft, ty, tsr = wave2stft(target)
    t_power = stft2power(t_stft)
    t_energy = get_energy(t_stft)
    
    npow_mean = get_mean_bandwidths(n_power)
    #npow_mean = get_rms(n_power)
    npow_var = get_var_bandwidths(n_power)
    
    y_stftred = np.array([rednoise(npow_mean,npow_var,y_power[i],y_stft[i]) for i in range(y_stft.shape[0])])

    
    voice_start,voice = sound_index(y_energy,start=True,rms_mean_noise = n_energy_mean)
    if voice:
        print(voice_start)
        print(voice_start/len(y_energy))
        start = voice_start/len(y_energy)
        start_time = (len(y)*start)/sr
        print("Start time: {} sec".format(start_time))
        y_stftred_voice = y_stftred[voice_start:]
        voicestart_samp = stft2wave(y_stftred_voice,len(y))
        date = get_date()
        savewave('./processed_recordings/rednoise_speechstart_{}.wav'.format(date),voicestart_samp,sr)
        print('Removed silence from beginning of recording. File saved.')
        
    else:
        #handle no speech in recording, or too much background noise
        return None
        
    rednoise_samp = stft2wave(y_stftred_voice,len(y))
    date = get_date()
    savewave('./processed_recordings/rednoise_{}.wav'.format(date),rednoise_samp,sr)
    print('Background noise reduction complete. File saved.')
    print('Now matching volume to target recording.')
    
    y_stftmatched = matchvol(t_power,y_power,y_stftred_voice)
    matchvol_samp = stft2wave(y_stftmatched,len(y))
    savewave('./processed_recordings/rednoise2_{}.wav'.format(date),matchvol_samp,sr)
    print('Matched volume. File saved.')
    
    
    #compare fingerprints of processed mimic and target sound
    fp_target = get_fingpr(target)
    fp_mimic = get_fingpr('./processed_recordings/rednoise2_{}.wav'.format(date))
    
    fp_score = comp_fingpr(fp_mimic,fp_target)
    return fp_score*10


def get_score(mimic_sound,mimic_noise):
    mimic_sound = mimic_sound[0][1]
    mimic_noise = mimic_noise[0][1]
    score = mimic_sound - mimic_noise
    score = int(score*100)
    return score
