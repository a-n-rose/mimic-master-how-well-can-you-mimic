import librosa
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
import time

from rednoise_fun_longwindow import rednoise, wave2stft, stft2power, get_mean_bandwidths, get_var_bandwidths, stft2wave, savewave, get_date, matchvol, get_pitch_wave,get_pitch_samples, get_pitch_mean, pitch_sqrt, sound_index, get_energy, get_energy_mean, wave2stft_long, get_pitch_wave_long, get_pitch_samples_long

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
        print("2 pitch matrices are necessary to be compared.")
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
    print("Duration of STFT calculation with {} ms intervals and {} ms windows: {} seconds".format(interval*1000,window*1000,duration_stft))
    print("Duration of pitch calculation with {} ms intervals and {} ms windows: {} seconds".format(interval*1000,window*1000,duration_pitch))
    return stft,power,pitch

def clip_around_sounds(sound_type,stft,samples_length,energy_length,start_index,end_index,sr):
    print("\n\nIndex for when {} starts: {}\nIndex for when sound ends: {}".format(sound_type,start_index,end_index))
    print("{} start relative to length of energy spectrum: {}\n{} end relative to length of signal: {}".format(sound_type,start_index/energy_length,sound_type,end_index/energy_length))
    start_percentile = start_index/energy_length
    start_time = (samples_length*start_percentile)/sr
    end_percentile = end_index/energy_length
    end_time = (samples_length*end_percentile)/sr
    end = end_index/energy_length
    end_time = (samples_length*end)/sr
    print("Start time: {} sec\nEnd time: {} sec".format(start_time,end_time))
    print("Length of {}: {} sec\n\n".format(sound_type,end_time-start_time))
    len_ms = (end_time-start_time)*1000 
    stft_start = stft[start_index:end_index]

    return stft_start, len_ms

def wave2pitchmeansqrt(wavefile, target, noise):
    #for saving wavefiles - w unique names
    date = get_date()
    
    #get mimic stft, samples, sampling rate
    y_stft, y, sr = wave2stft(wavefile)
    y_power = stft2power(y_stft)
    y_energy = get_energy(y_stft)
    
    #get noise stft, samples, sampling rate
    n_stft, ny, nsr = wave2stft(noise)
    n_power = stft2power(n_stft)
    n_energy = get_energy(n_stft)
    n_energy_mean = get_energy_mean(n_energy)
    npow_mean = get_mean_bandwidths(n_power)
    npow_var = get_var_bandwidths(n_power)



    #get target stft, samples, sampling rate
    t_stft, ty, tsr = wave2stft(target)
    t_power = stft2power(t_stft)
    t_energy = get_energy(t_stft)
    
    

    
    y_stftred = np.array([rednoise(npow_mean,npow_var,y_power[i],y_stft[i]) for i in range(y_stft.shape[0])])
    
    y_nr = stft2wave(y_stftred,len(y))

    #save reduced noise mimic to see what's going on:
    savewave('{}_reducednoise.wav'.format(wavefile),y_nr, sr)
    print("Reduced noise mimic saved")

    
    #reduce the noise in noise signal, for new reference for "noise" to find when mimic starts and ends
    #save wavefile for later
    n_stftred = np.array([rednoise(npow_mean,npow_var,n_power[i],n_stft[i]) for i in range(n_stft.shape[0])])
    n_rn = stft2wave(n_stftred,len(ny))
    savewave('backgroundnoise_silence_{}.wav'.format(date),n_rn,sr)
    
    #recompute power values with reduced noise noise signal:
    n_power_rn = stft2power(n_stftred)
    n_energy_rn = get_energy(n_stftred)
    n_energy_rn_mean = get_energy_mean(n_energy_rn)
    npow_rn_mean = get_mean_bandwidths(n_power_rn)
    npow_rn_var = get_var_bandwidths(n_power_rn)

    
    #noise reference values - change these to change how mimic start/end search uses noise (with reduced noise noise signal or original noise signal)
    rms_mean_noise = n_energy_mean #options: n_energy_rn_mean   n_energy_mean  None
    
    

    
    voice_start,voice = sound_index(y_energy,start=True,rms_mean_noise = rms_mean_noise)
    if voice:
        #get start and/or end indices of mimic and target
        #end index of mimic
        voice_end, voice = sound_index(y_energy,start=False,rms_mean_noise = rms_mean_noise)
        #start and end index of target
        target_start,target = sound_index(t_energy,start=True,rms_mean_noise = None)
        target_end,target = sound_index(t_energy,start=False,rms_mean_noise = None)
        
        y_stftred, mimic_len_ms = clip_around_sounds("MIMIC",y_stftred,len(y),len(y_power),voice_start,voice_end,sr)
        t_stft_sound, target_len_ms = clip_around_sounds("TARGET",t_stft,len(ty),len(t_power),target_start,target_end,sr)
        
        print('Now matching volume to target recording.')
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
        savewave('./processed_recordings/mimiconly_librosa_{}.wav'.format(date),mimic_only_samps,sr)
        savewave('./processed_recordings/targetonly_librosa_{}.wav'.format(date),target_only_samps,sr)

        #try with pydub:
        
        #clip mimic and save 
        mimic_full = AudioSegment.from_wav("{}.wav".format(filename_mimic))
        mimic_slice = mimic_full[:mimic_len_ms]
        mimic_slice.export("./processed_recordings/mimiconly_pydub_{}.wav".format(date), format="WAV")

        target_full = AudioSegment.from_wav("{}.wav".format(filename_targetsound))
        target_slice = target_full[:target_len_ms]
        target_slice.export("./processed_recordings/targetonly_pydub_{}.wav".format(date), format="WAV")

        
        #get pitch, power, and stft from clipped files:

        #mimic
        m_clipped,sr = librosa.load("./processed_recordings/mimiconly_librosa_{}.wav".format(date))
        stft_mclipped,power_mclipped,pitch_mclipped = long_term_info(m_clipped,sr)
        #target
        t_clipped,sr = librosa.load("./processed_recordings/targetonly_librosa_{}.wav".format(date))
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
        
        
        if score_mimic and score_noise and score_mimic > score_noise:
            if score_mimic > 0:
                score = int(score_mimic*1000)
            else:
                print("Hmmmm, nice try but I bet you can do better. No points earned")
                score = 0
            print("Similarity of your mimic to the sound: {}".format(score_mimic))
            print("Similarity of your background noise to the sound: {}".format(score_noise))
        else:
            score = 0
        return score
    else:
        print("Hmmmmm.. I didn't catch that. If this problem persists, type 'exit' and check your mic.")
        return None
