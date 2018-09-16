import librosa
import numpy as np
import matplotlib.pyplot as plt
import time

from check_energy_sim import check_energy
from rednoise_fun import rednoise, wave2stft, stft2power, get_mean_bandwidths, get_var_bandwidths, stft2wave, savewave, get_date, matchvol, sound_index, get_energy_rms, get_energy_mean, get_energy_ms

def match_len(matrix_list):
    matrix_lengths = [len(matrix) for matrix in matrix_list]
    min_index = np.argmin(matrix_lengths)
    newlen = matrix_lengths[min_index]
    matched_matrix_list = []
    for item in matrix_list:
        item = item[:newlen]
        matched_matrix_list.append(item)
    return matched_matrix_list

def hermes_wc(pitch_list, sumpower):
    if len(pitch_list) != 2:
        return None
    coefficients = []
    for i in range(len(sumpower)):
        nom = sum(sumpower[i]*((pitch_list[0][i]-np.mean(pitch_list[0]))*(pitch_list[1][i]-np.mean(pitch_list[1]))))
        den = np.sqrt(sum(sumpower[i]*((pitch_list[0][i]-np.mean(pitch_list[0]))**2))*sum(sumpower[i]*((pitch_list[1][i]-np.mean(pitch_list[1]))**2)))
        coefficients.append(nom/den)
    return coefficients
    
def long_term_info(y,sr):
    interval = 0.01
    window = 0.256
    start_stft = time.time()
    stft = librosa.stft(y,hop_length=int(interval*sr),n_fft=int(window*sr))
    end_stft = time.time()
    stft = np.transpose(stft)
    power = np.abs(stft)**2
    start_pitch = time.time()
    pitch, mag = librosa.piptrack(y=y,sr=sr,hop_length=int(interval*sr),n_fft=int(window*sr))
    end_pitch = time.time()
    duration_stft = end_stft - start_stft
    duration_pitch = end_pitch - start_pitch
    pitch = np.transpose(pitch)
    return stft,power,pitch

def clip_around_sounds(sound_type,stft,samples_length,energy_length,start_index,end_index,sr):
    start_percentile = start_index/energy_length
    start_time = (samples_length*start_percentile)/sr
    end_percentile = end_index/energy_length
    end_time = (samples_length*end_percentile)/sr
    end = end_index/energy_length
    end_time = (samples_length*end)/sr
    len_ms = (end_time-start_time)*1000 
    stft_start = stft[start_index:end_index]

    return stft_start, len_ms

def wave2pitchmeansqrt(wavefile, target, noise):
    #for saving wavefiles - w unique names
    date = get_date()
    
    #get mimic stft, samples, sampling rate
    y_stft, y, sr = wave2stft(wavefile)
    y_power = stft2power(y_stft)
    y_energy = get_energy_rms(y_stft)
    y_energy_mean = get_energy_mean(y_energy)
    y_energy2 = get_energy_ms(y_stft)
    y_energy2_mean = get_energy_mean(y_energy2)
    
    #get noise stft, samples, sampling rate
    n_stft, ny, nsr = wave2stft(noise)
    n_power = stft2power(n_stft)
    n_energy = get_energy_rms(n_stft)
    n_energy_mean = get_energy_mean(n_energy)
    n_energy_var = np.var(n_energy)
    npow_mean = get_mean_bandwidths(n_power)
    npow_var = get_var_bandwidths(n_power)

    #get target stft, samples, sampling rate
    t_stft, ty, tsr = wave2stft(target)
    t_power = stft2power(t_stft)
    t_energy = get_energy_rms(t_stft)
    t_energy_mean = get_energy_mean(t_energy)
    t_energy2 = get_energy_ms(t_stft)
    t_energy2_mean = get_energy_mean(t_energy2)
    

    
    y_stftred = np.array([rednoise(npow_mean,npow_var,y_power[i],y_stft[i]) for i in range(y_stft.shape[0])])
    y_rn_energy = get_energy_rms(y_stftred)
    y_nr = stft2wave(y_stftred,len(y))

    #save reduced noise mimic to see what's going on:
    savewave('{}_reducednoise.wav'.format(wavefile),y_nr, sr)

    
    #reduce the noise in noise signal, for new reference for "noise" to find when mimic starts and ends
    #save wavefile for later
    n_stftred = np.array([rednoise(npow_mean,npow_var,n_power[i],n_stft[i]) for i in range(n_stft.shape[0])])
    n_rn = stft2wave(n_stftred,len(ny))
    savewave('backgroundnoise_silence_{}.wav'.format(date),n_rn,sr)
    
    #recompute power values with reduced noise noise signal:
    n_power_rn = stft2power(n_stftred)
    n_energy_rn = get_energy_rms(n_stftred)
    n_energy_rn_mean = get_energy_mean(n_energy_rn)
    npow_rn_mean = get_mean_bandwidths(n_power_rn)
    n_energy_rn_var = np.var(n_energy_rn)

    
    #noise reference values - change these to change how mimic start/end search uses noise (with reduced noise noise signal or original noise signal)
    rms_mean_noise = n_energy_rn_mean #options: n_energy_rn_mean   n_energy_mean  None
    #rms_var_noise = n_energy_rn_var  #options: n_energy_var   None
    energy_mimic = y_energy2  #options y_rn_energy   y_energy     y_power
    energy_mimic_mean = y_energy2_mean  #options: y_energy_mean   y_power_mean
    energy_target = t_energy2  #options  t_energy   t_power
    energy_target_mean = t_energy2_mean #options: t_energy_mean  t_power_mean
    
    voice_start,voice = sound_index(energy_mimic,energy_mimic_mean,start=True,)
    if voice:
        #get start and/or end indices of mimic and target
        #end index of mimic
        voice_end, voice = sound_index(energy_mimic,energy_mimic_mean,start=False)
        #start and end index of target
        target_start,target = sound_index(energy_target,energy_target_mean,start=True)
        target_end,target = sound_index(energy_target,energy_target_mean,start=False)
        
        y_stftred, mimic_len_ms = clip_around_sounds("MIMIC",y_stftred,len(y),len(y_power),voice_start,voice_end,sr)
        t_stft_sound, target_len_ms = clip_around_sounds("TARGET",t_stft,len(ty),len(t_power),target_start,target_end,sr)
        
        y_stftmatched = matchvol(t_power,y_power,y_stftred)
        
        #save waves to see that everything worked:
        
        #mimic  
        mimic_samp_check = stft2wave(y_stftmatched,len(y))
        filename_mimic = './processed_recordings/mimicstart_{}'.format(date)
        savewave('{}.wav'.format(filename_mimic),mimic_samp_check,sr)
        
        #target 
        t_sound = stft2wave(t_stft_sound,len(ty))
        filename_targetsound = './processed_recordings/adjusted_targetsound_{}'.format(date)
        savewave(filename_targetsound+'.wav',t_sound,sr)
 
        
        #clip the file (don't include silence at end)
        
        #try with librosa:
        mimic_only_samps, sr = librosa.load('{}.wav'.format(filename_mimic),duration=mimic_len_ms/1000)
        target_only_samps, sr = librosa.load('{}.wav'.format(filename_targetsound),duration=target_len_ms/1000)
        #save these to check
        savewave('./processed_recordings/mimiconly_{}.wav'.format(date),mimic_only_samps,sr)
        savewave('./processed_recordings/targetonly_{}.wav'.format(date),target_only_samps,sr)

        
        #get pitch, power, and stft from clipped files:

        #mimic
        m_clipped,sr = librosa.load("./processed_recordings/mimiconly_{}.wav".format(date))
        stft_mclipped,power_mclipped,pitch_mclipped = long_term_info(m_clipped,sr)
        #target
        t_clipped,sr = librosa.load("./processed_recordings/targetonly_{}.wav".format(date))
        stft_tclipped,power_tclipped,pitch_tclipped = long_term_info(t_clipped,sr)
        #noise (over longer windows)
        n_silent,sr = librosa.load('backgroundnoise_silence_{}.wav'.format(date))
        stft_nlong, power_nlong, pitch_nlong = long_term_info(n_silent,sr)

        #compare pitch w hermes weighted correlation and time warping 
        #target and mimic
        powerlist_mimic = match_len([power_tclipped,power_mclipped])
        pitchlist_mimic = match_len([pitch_tclipped,pitch_mclipped])
        sumpower_mimic = list(map(sum,powerlist_mimic))
        coefficients_mimic = hermes_wc(pitchlist_mimic,sumpower_mimic)
        score_mimic = sum(coefficients_mimic)
        
        #target and noise
        powerlist_noise = match_len([power_tclipped,power_nlong])
        pitchlist_noise = match_len([pitch_tclipped,pitch_nlong])
        sumpower_noise = list(map(sum,powerlist_noise))
        coefficients_noise = hermes_wc(pitchlist_noise,sumpower_noise)
        score_noise = sum(coefficients_noise)
    
        
        #this part is a bit experimental
        #I want to avoid giving points to someone whose random mimic somehow scores better than background noise
        score=1
        #see if energy levels correspond
        mim_energy_clipped = get_energy_rms(stft_mclipped)
        targ_energy_clipped = get_energy_ms(stft_tclipped)
        #score = check_energy(mim_energy_clipped,targ_energy_clipped)
        score = find_peaks_valleys(mim_energy_clipped,targ_energy_clipped)
        
        if score_mimic and score > 0 and score_noise and score_mimic > score_noise:
            diff = score_mimic - score_noise
            score = int(abs(diff) * 100)
            print("Similarity of your mimic to the sound: {}".format(score_mimic))
            print("Similarity of your background noise to the sound: {}".format(score_noise))
        else:
            score = 0
        return score
    else:
        print("Hmmmmm.. I didn't catch that. If this problem persists, type 'exit' and check your mic.")
        return None
