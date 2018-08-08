import librosa
import numpy as np
import matplotlib.pyplot as plt

from rednoise_fun import rednoise, wave2stft, stft2power, get_mean_bandwidths, get_var_bandwidths, stft2wave, savewave, get_date, matchvol, get_pitch,get_pitch2, get_pitch_mean, pitch_sqrt, sound_index, get_energy, get_energy_mean

def wave2pitchmeansqrt(wavefile, target, noise):
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
        y_stft_voice = y_stftred[voice_start:]
        voicestart_samp = stft2wave(y_stft_voice,len(y))
        date = get_date()
        savewave('./processed_recordings/rednoise_speechstart_{}.wav'.format(date),voicestart_samp,sr)
        print('Removed silence from beginning of recording. File saved.')
        
    else:
        #handle no speech in recording, or too much background noise
        return None
        
    
    rednoise_samp = stft2wave(y_stft_voice,len(y))
    date = get_date()
    savewave('./processed_recordings/rednoise_{}.wav'.format(date),rednoise_samp,sr)
    print('Background noise reduction complete. File saved.')
    print('Now matching volume to target recording.')
    
    y_stftmatched = matchvol(t_power,y_power,y_stftred)
    matchvol_samp = stft2wave(y_stftmatched,len(y))
    savewave('./processed_recordings/rednoise2_{}.wav'.format(date),matchvol_samp,sr)
    print('Matched volume. File saved.')
    print('Now extracting pitch information')
    
    #find start and end indices of sounds/speech:
    target_start,target = sound_index(t_energy,start=True,rms_mean_noise = None)
    target_end,target = sound_index(t_energy,start=False,rms_mean_noise = None)
    target_len = target_end - target_start
    
    mimic_start,mimic = sound_index(y_energy,start=True,rms_mean_noise = n_energy_mean) 
    mimic_end_match = mimic_start+target_len
    
    if mimic:
            
        t_stft_sound = t_stft[target_start:target_end]
        t_sound = stft2wave(t_stft_sound,len(ty))
        t_sound_pitch,t_m = get_pitch2(t_sound,tsr)
        tp_mean = get_pitch_mean(t_sound_pitch)
        tpm_sqrt = pitch_sqrt(tp_mean)
        
        y_stft_mimic = y_stftmatched[mimic_start:mimic_end_match]
        y_mimic = stft2wave(y_stft_mimic,len(y))
        #have to normalize y_mimic - problem dealt
        #with in the comparison of the sqrt_mean of pitch curves
        y_mimic_pitch,y_m = get_pitch2(y_mimic,sr)
        yp_mean = get_pitch_mean(y_mimic_pitch)
        ypm_sqrt = pitch_sqrt(yp_mean)
    
        
        n_pitch, n_m = get_pitch(noise)
        np_mean = get_pitch_mean(n_pitch)
        npm_sqrt = pitch_sqrt(np_mean)
        
        #to get them on the same scale
        if np.max(tpm_sqrt) < np.max(ypm_sqrt):
            mag = np.max(tpm_sqrt)/np.max(ypm_sqrt)
            ypm_sqrt *= mag
        for index in range(len(npm_sqrt)):
            if npm_sqrt[index] > 0.0:
                npm_sqrt = npm_sqrt[index:]
                break
        return (ypm_sqrt, tpm_sqrt, npm_sqrt)
    else:
        print("No mimic found.")
        return None
    
def compare_sim(pitch_mean1, pitch_mean2):
    pm1 = pitch_mean1.copy()
    pm2 = pitch_mean2.copy()
    if len(pm1) != len(pm2):
        index_min = np.argmin([len(pm1),len(pm2)])
        if index_min > 0:
            pm1 = pm1[:len(pm2)]
        else:
            pm2 = pm2[:len(pm1)]
    corrmatrix = np.corrcoef(pm1,pm2)
    return(corrmatrix)


def get_score(mimic_sound,mimic_noise):
    mimic_sound = mimic_sound[0][1]
    mimic_noise = mimic_noise[0][1]
    score = mimic_sound - mimic_noise
    score = int(score*100)
    return score
